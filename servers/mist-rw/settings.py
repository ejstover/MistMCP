from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MistRWSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    api_base: str = Field("https://api.ac2.mist.com/api/v1", alias="MIST_API_BASE")
    org_id: str = Field("", alias="MIST_ORG_ID")
    token_rw: str = Field("", alias="MIST_TOKEN_RW")
    timeout_seconds: int = Field(10, alias="MIST_TIMEOUT_SECONDS")

    def headers(self) -> dict:
        return {"Authorization": f"Token {self.token_rw}"}
