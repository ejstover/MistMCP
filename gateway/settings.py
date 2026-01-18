from __future__ import annotations

import json
from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mode_auth: str = Field("dev", alias="MODE_AUTH")
    write_enabled: bool = Field(False, alias="WRITE_ENABLED")

    jwt_audience: str = Field("mcp-gateway", alias="JWT_AUDIENCE")
    jwt_issuer: str = Field("http://localhost/dev", alias="JWT_ISSUER")
    dev_jwks_path: str = Field("./dev_jwks.json", alias="DEV_JWKS_PATH")

    oidc_jwks_url: str = Field("", alias="OIDC_JWKS_URL")
    oidc_issuer: str = Field("", alias="OIDC_ISSUER")

    role_claim: str = Field("roles", alias="ROLE_CLAIM")
    role_map_json: str = Field(
        '{"ReadOnly":["ReadOnly"],"ReadWrite":["ReadWrite"]}', alias="ROLE_MAP_JSON"
    )
    site_scope_json: str = Field(
        '{"ReadOnly":["*"],"ReadWrite":["*"]}', alias="SITE_SCOPE_JSON"
    )

    log_level: str = Field("INFO", alias="LOG_LEVEL")

    @property
    def role_map(self) -> Dict[str, List[str]]:
        return json.loads(self.role_map_json)

    @property
    def site_scope(self) -> Dict[str, List[str]]:
        return json.loads(self.site_scope_json)
