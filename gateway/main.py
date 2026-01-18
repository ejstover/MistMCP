from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from commons.logging_conf import setup_logging
from commons.jwks_cache import JWKSCache
from gateway.auth import AuthMiddleware, mint_dev_token
from gateway.mcp_client import MCPClient, StubModel
from gateway.rbac import authorize, load_policy
from gateway.settings import Settings

settings = Settings()
setup_logging(settings.log_level)

app = FastAPI(title="MCP Gateway")

jwks_cache: Optional[JWKSCache] = None
if settings.mode_auth == "oidc":
    if not settings.oidc_jwks_url:
        raise RuntimeError("OIDC_JWKS_URL is required for oidc mode")
    jwks_cache = JWKSCache(settings.oidc_jwks_url)
    jwks_cache.refresh(blocking=False)

app.add_middleware(AuthMiddleware, settings=settings, jwks_cache=jwks_cache)

policy = load_policy(str(Path(__file__).with_name("policy_rbac.json")))

mcp_client = MCPClient()
model = StubModel()


class DevMintRequest(BaseModel):
    sub: str
    email: str
    roles: list[str] = Field(default_factory=list)
    ttl: int = 900


class ChatRequest(BaseModel):
    message: str
    tool: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    commit: bool = False
    confirmation: Optional[str] = None


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/whoami")
async def whoami(request: Request) -> dict:
    return request.state.user


@app.post("/auth/dev/mint")
async def mint_dev(request: DevMintRequest) -> dict:
    if settings.mode_auth != "dev":
        raise HTTPException(status_code=403, detail="Dev mint disabled")
    payload = {
        "sub": request.sub,
        "email": request.email,
        settings.role_claim: request.roles,
    }
    token = mint_dev_token(payload, settings, request.ttl)
    return {"token": token}


@app.post("/mcp/chat")
async def mcp_chat(request: Request, body: ChatRequest) -> dict:
    user = request.state.user
    prompt_template = Path(__file__).with_name("rbac_prompt.txt").read_text()
    prompt = prompt_template.format(
        USER_ID=user.get("id"),
        USER_EMAIL=user.get("email"),
        ROLES_JSON_ARRAY=json.dumps(user.get("roles", [])),
        SITE_SCOPE_JSON=json.dumps(user.get("site_scope", [])),
    )

    model_output = model.generate_with_tool(body.message)
    tool_name = body.tool or model_output.get("tool")
    params = body.params or model_output.get("params", {})

    response: Dict[str, Any] = {
        "system_prompt": prompt,
        "reply": model_output.get("reply"),
    }

    if tool_name:
        if body.commit and not settings.write_enabled:
            return {
                **response,
                "tool": tool_name,
                "status": "denied",
                "reason": "Write disabled by policy",
            }
        allowed, reason, committed = authorize(
            policy,
            user.get("roles", []),
            tool_name,
            verb="call",
            site=params.get("site"),
            site_scope=user.get("site_scope", []),
            commit=body.commit,
            confirmation=body.confirmation,
        )
        if not allowed:
            return {**response, "tool": tool_name, "status": "denied", "reason": reason}

        tool_response = mcp_client.call_tool(
            tool_name, params, user=user, commit=committed
        )
        response.update(
            {
                "tool": tool_name,
                "status": reason,
                "committed": committed,
                "tool_response": tool_response,
            }
        )

    return response
