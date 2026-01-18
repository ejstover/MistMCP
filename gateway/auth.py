from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWTError
from jwt.algorithms import RSAAlgorithm
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from commons.jwks_cache import JWKSCache, jwk_to_public_key
from gateway.settings import Settings

logger = logging.getLogger(__name__)

PUBLIC_PATHS = {"/health", "/auth/dev/mint"}


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings, jwks_cache: Optional[JWKSCache] = None):
        super().__init__(app)
        self.settings = settings
        self.jwks_cache = jwks_cache

    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = _extract_bearer_token(request)
        if not token:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        try:
            claims = verify_jwt(token, self.settings, self.jwks_cache)
        except HTTPException as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)

        request.state.user = build_user_context(claims, self.settings)
        return await call_next(request)


def _extract_bearer_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return auth.split(" ", 1)[1].strip()


def verify_jwt(token: str, settings: Settings, jwks_cache: Optional[JWKSCache]) -> Dict[str, Any]:
    try:
        unverified = jwt.get_unverified_header(token)
    except PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token header") from exc

    kid = unverified.get("kid")
    if settings.mode_auth == "dev":
        jwks = load_dev_jwks(settings.dev_jwks_path)
        key = jwks.get(kid)
        if not key:
            raise HTTPException(status_code=401, detail="Unknown key id")
        public_key = jwk_to_public_key(key)
        issuer = settings.jwt_issuer
    else:
        if not jwks_cache:
            raise HTTPException(status_code=401, detail="JWKS cache unavailable")
        key = jwks_cache.get_key(kid)
        if not key:
            jwks_cache.refresh(blocking=True)
            key = jwks_cache.get_key(kid)
        if not key:
            raise HTTPException(status_code=401, detail="Unknown key id")
        public_key = jwk_to_public_key(key)
        issuer = settings.oidc_issuer

    try:
        return jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.jwt_audience,
            issuer=issuer,
            leeway=300,
        )
    except PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token validation failed") from exc


def load_dev_jwks(path: str) -> Dict[str, str]:
    jwks_path = Path(path)
    if not jwks_path.exists():
        raise HTTPException(status_code=401, detail="Dev JWKS not found")
    payload = json.loads(jwks_path.read_text())
    keys = payload.get("keys", []) if isinstance(payload, dict) else []
    return {jwk.get("kid"): json.dumps(jwk) for jwk in keys if jwk.get("kid")}


def load_dev_private_key(path: str) -> Optional[str]:
    payload = json.loads(Path(path).read_text())
    keys = payload.get("keys", []) if isinstance(payload, dict) else []
    for jwk in keys:
        if jwk.get("kid") and jwk.get("d"):
            return json.dumps(jwk)
    return None


def build_user_context(claims: Dict[str, Any], settings: Settings) -> Dict[str, Any]:
    roles = map_roles(claims.get(settings.role_claim, []), settings.role_map)
    return {
        "id": claims.get("sub"),
        "email": claims.get("email")
        or claims.get("upn")
        or claims.get("preferred_username"),
        "name": claims.get("name"),
        "roles": roles,
        "site_scope": select_site_scope(roles, settings.site_scope),
    }


def map_roles(raw_roles: Any, role_map: Dict[str, List[str]]) -> List[str]:
    if isinstance(raw_roles, str):
        claim_roles = set(raw_roles.split())
    else:
        claim_roles = {str(role) for role in raw_roles or []}

    mapped: List[str] = []
    for target_role, source_roles in role_map.items():
        if any(role in claim_roles for role in source_roles):
            mapped.append(target_role)
    return mapped


def select_site_scope(roles: List[str], scope_map: Dict[str, List[str]]) -> List[str]:
    scopes: List[str] = []
    for role in roles:
        scopes.extend(scope_map.get(role, []))
    return sorted(set(scopes))


def mint_dev_token(
    payload: Dict[str, Any], settings: Settings, ttl_seconds: int
) -> str:
    private_jwk = load_dev_private_key(settings.dev_jwks_path)
    if not private_jwk:
        raise HTTPException(status_code=500, detail="Dev signing key missing")

    private_key = RSAAlgorithm.from_jwk(private_jwk)
    now = datetime.now(timezone.utc)
    claims = {
        **payload,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
    }
    return jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": json.loads(private_jwk)["kid"]})
