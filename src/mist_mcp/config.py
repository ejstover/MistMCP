"""Configuration loader for the Mist MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv
import os


load_dotenv()


@dataclass
class MistConfig:
    """Runtime configuration loaded from environment variables.

    Attributes:
        api_token: Personal API token for authenticating with the Mist cloud.
        org_id: Default organization identifier.
        base_url: Mist API base URL. Defaults to the public cloud endpoint.
        default_site_id: Optional site identifier used when one is not provided.
    """

    api_token: str
    org_id: str
    base_url: str = "https://api.mist.com"
    default_site_id: Optional[str] = None

    @classmethod
    def load(cls) -> "MistConfig":
        api_token = os.getenv("MIST_API_TOKEN")
        org_id = os.getenv("MIST_ORG_ID")
        base_url = os.getenv("MIST_API_BASE_URL", "https://api.mist.com").rstrip("/")
        default_site_id = os.getenv("MIST_DEFAULT_SITE_ID")

        if not api_token:
            raise ValueError("MIST_API_TOKEN is required")
        if not org_id:
            raise ValueError("MIST_ORG_ID is required")

        return cls(api_token=api_token, org_id=org_id, base_url=base_url, default_site_id=default_site_id)
