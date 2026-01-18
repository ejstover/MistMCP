from __future__ import annotations

import json
from pathlib import Path

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from gateway.auth import AuthMiddleware
from gateway.rbac import authorize, load_policy
from gateway.settings import Settings


def test_authorize_readonly_blocks_write():
    policy = load_policy(str(Path(__file__).parents[1] / "policy_rbac.json"))
    allowed, reason, committed = authorize(
        policy,
        user_roles=["ReadOnly"],
        tool_name="mist_call_write",
        verb="call",
        site="site-1",
        site_scope=["*"],
        commit=True,
        confirmation="explicit",
    )
    assert allowed is False
    assert committed is False
    assert "Role" in reason or "Commit" in reason


def test_authorize_commit_requires_confirmation():
    policy = load_policy(str(Path(__file__).parents[1] / "policy_rbac.json"))
    allowed, reason, committed = authorize(
        policy,
        user_roles=["ReadWrite"],
        tool_name="mist_call_write",
        verb="call",
        site="site-1",
        site_scope=["*"],
        commit=True,
        confirmation=None,
    )
    assert allowed is False
    assert committed is False
    assert "confirmation" in reason.lower()


def test_authorize_readwrite_read_allowed():
    policy = load_policy(str(Path(__file__).parents[1] / "policy_rbac.json"))
    allowed, reason, committed = authorize(
        policy,
        user_roles=["ReadWrite"],
        tool_name="mist_call_get",
        verb="call",
        site="site-1",
        site_scope=["*"],
        commit=False,
    )
    assert allowed is True
    assert committed is False
    assert reason == "Dry-run"


def test_invalid_jwt_returns_401(tmp_path):
    dev_jwks = tmp_path / "dev_jwks.json"
    dev_jwks.write_text(json.dumps({"keys": []}))

    settings = Settings(
        MODE_AUTH="dev",
        DEV_JWKS_PATH=str(dev_jwks),
        JWT_AUDIENCE="mcp-gateway",
        JWT_ISSUER="http://localhost/dev",
    )
    app = FastAPI()
    app.add_middleware(AuthMiddleware, settings=settings, jwks_cache=None)

    @app.get("/protected")
    async def protected():
        return {"ok": True}

    client = TestClient(app)
    token = jwt.encode({"sub": "user"}, "secret", algorithm="HS256")
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
