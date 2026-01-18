# Mist MCP Gateway (Dual-Auth + RBAC Demo)

This repository demonstrates a minimal, production-minded MCP gateway with **dual authentication modes**, **strict RBAC**, and an example **read-only Mist MCP server**. It is designed for pilots and homelab usage where read-only is the default and writes are explicitly gated.

## Architecture overview

```
Browser → FastAPI gateway (MCP client) → model stub → MCP servers (mist-ro)
```

Key features:
- **Dual Auth Modes**
  - **DEV**: locally signed RS256 JWTs using a local JWKS file.
  - **OIDC**: verify JWTs from an existing IdP via JWKS (Azure AD, Okta, Ping, Auth0, Keycloak).
- **Role mapping** to exactly two roles: `ReadOnly` / `ReadWrite`.
- **Server-side RBAC** with allow/deny, dry-run default, and commit gating.
- **Structured audit logs** for every tool call.
- **Read-only MCP server** (`servers/mist-ro`) with sample tools/resources/prompts.

## Repo layout

```
.
├─ README.md
├─ .env.example
├─ commons/
│  ├─ jwks_cache.py
│  └─ logging_conf.py
├─ gateway/
│  ├─ main.py
│  ├─ settings.py
│  ├─ auth.py
│  ├─ rbac.py
│  ├─ policy_rbac.json
│  ├─ mcp_client.py
│  ├─ rbac_prompt.txt
│  └─ tests/
│     └─ test_rbac.py
└─ servers/
   ├─ mist-ro/
   │  ├─ server.py
   │  ├─ tools.py
   │  ├─ resources.py
   │  ├─ prompts.py
   │  ├─ caching.py
   │  ├─ settings.py
   │  └─ requirements.txt
   └─ mist-rw/
      ├─ server.py
      ├─ tools.py
      ├─ resources.py
      ├─ prompts.py
      ├─ caching.py
      ├─ settings.py
      └─ requirements.txt
```

## Quickstart (DEV mode)

1. **Create a virtualenv**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r servers/mist-ro/requirements.txt
   pip install -r servers/mist-rw/requirements.txt
   pip install fastapi uvicorn httpx PyJWT pydantic pydantic-settings cryptography
   ```
3. **Create a .env**
   ```bash
   cp .env.example .env
   ```
4. **Generate a dev JWKS**
   ```bash
   python scripts/gen_dev_jwks.py
   ```
5. **Run the gateway**
   ```bash
   uvicorn gateway.main:app --reload
   ```
6. **Mint a dev token**
   ```bash
   curl -X POST http://localhost:8000/auth/dev/mint \
     -H 'Content-Type: application/json' \
     -d '{"sub":"user-1","email":"user@example.com","roles":["ReadOnly"],"ttl":900}'
   ```
7. **Call /whoami and /mcp/chat**
   ```bash
   curl http://localhost:8000/whoami -H "Authorization: Bearer <token>"
   curl -X POST http://localhost:8000/mcp/chat \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer <token>" \
     -d '{"message":"hello"}'
   ```

## Quickstart (OIDC mode with existing IdP)

1. Set the following in `.env`:
   - `MODE_AUTH=oidc`
   - `OIDC_JWKS_URL` (e.g., `https://login.microsoftonline.com/<tenant>/discovery/v2.0/keys`)
   - `OIDC_ISSUER` (e.g., `https://login.microsoftonline.com/<tenant>/v2.0`)
   - `JWT_AUDIENCE=mcp-gateway`
   - `ROLE_CLAIM=roles` (or `groups` / `scp` depending on IdP)
   - `ROLE_MAP_JSON='{"ReadOnly":["ReadOnly"],"ReadWrite":["ReadWrite"]}'`
2. Obtain an access token from your IdP.
3. Call the gateway:
   ```bash
   curl http://localhost:8000/whoami -H "Authorization: Bearer <token>"
   ```

## RBAC behavior

- **Roles**: `ReadOnly` or `ReadWrite` only.
- **Dry-run default**: all tools run in dry-run unless `commit=true`.
- **Commit gating**: requires `ReadWrite` **and** explicit confirmation (`confirmation` field).
- **Site scope**: enforced via `SITE_SCOPE_JSON`.

## Write server (mist-rw)

Write operations now live in `servers/mist-rw` and require `MIST_TOKEN_RW`. This separation keeps read-only operations isolated in `servers/mist-ro` while preserving functionality for write workflows such as switch port changes, site creation, and alarm acknowledgments.

## Security notes

- Short JWT TTLs recommended.
- JWKS is cached with TTL and background refresh.
- Secrets (Authorization headers, tokens) are masked in logs.
- Mist tokens are never exposed to the browser; the MCP server reads `MIST_TOKEN_RO` from env.

## Environment variables

See `.env.example` for the full list, including:
- `MODE_AUTH`, `WRITE_ENABLED`, `JWT_AUDIENCE`, `JWT_ISSUER`, `DEV_JWKS_PATH`
- `OIDC_JWKS_URL`, `OIDC_ISSUER`
- `ROLE_CLAIM`, `ROLE_MAP_JSON`, `SITE_SCOPE_JSON`
- `MIST_API_BASE`, `MIST_ORG_ID`, `MIST_TOKEN_RO`
- `MIST_TOKEN_RW`

## Notes on the MCP gateway

The gateway includes a **stub model** that can be swapped for a real provider. The MCP client is a minimal placeholder intended to demonstrate audit logging and RBAC enforcement. When integrating a real model, wire tool calls through a proper MCP client implementation and keep the audit logging structure intact.
