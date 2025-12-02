"""Entry point for the Mist MCP server."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .client import MistClient
from .config import MistConfig
from . import tools


mcp = FastMCP("mist-mcp")


@lru_cache(maxsize=1)
def get_client() -> MistClient:
    """Lazily instantiate the Mist client to defer env validation until runtime."""

    config = MistConfig.load()
    return MistClient(config)


@mcp.tool()
def find_device(identifier: str, site_id: Optional[str] = None) -> dict:
    """Find devices by IP address, MAC address, or hostname."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    return tools.find_device(client, identifier=identifier, site_id=resolved_site)


@mcp.tool()
def find_client(identifier: str, site_id: Optional[str] = None) -> dict:
    """Find clients by IP address, MAC address, or hostname."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    return tools.find_client(client, identifier=identifier, site_id=resolved_site)


@mcp.tool()
def list_sites(country_codes: Optional[List[str]] = None) -> dict:
    """List Mist sites filtered by country codes when provided."""

    client = get_client()
    return tools.list_sites(client, country_codes=country_codes)


@mcp.tool()
def site_device_counts(site_id: Optional[str] = None) -> dict:
    """Count switches, APs, and other devices at a site."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    return tools.site_device_counts(client, site_id=resolved_site)


@mcp.tool()
def sites_with_recent_errors(minutes: int = 60, site_ids: Optional[List[str]] = None, country_codes: Optional[List[str]] = None) -> dict:
    """Retrieve alarms for the provided sites within the last N minutes."""

    client = get_client()
    target_site_ids: List[str] = []

    if site_ids:
        target_site_ids.extend(site_ids)
    elif country_codes:
        sites = client.list_sites(country_codes=country_codes)
        target_site_ids.extend([site["id"] for site in sites if site.get("id")])
    elif client.config.default_site_id:
        target_site_ids.append(client.config.default_site_id)
    else:
        sites = client.list_sites()
        target_site_ids.extend([site["id"] for site in sites if site.get("id")])

    if not target_site_ids:
        raise ValueError("No sites available for alarm lookup")

    return tools.sites_with_recent_errors(client, site_ids=target_site_ids, minutes=minutes)


@mcp.tool()
def configure_switch_port_profile(
    site_id: str, device_id: str, port_id: str, port_profile_id: str
) -> dict:
    """Apply a Mist port profile to a switch port."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    return tools.configure_switch_port_profile(
        client,
        site_id=resolved_site,
        device_id=device_id,
        port_id=port_id,
        port_profile_id=port_profile_id,
    )


@mcp.tool()
def create_site(site_data: dict) -> dict:
    """Create a new Mist site. Requires name, country_code, timezone, and address."""

    client = get_client()
    return tools.create_site(client, site_data=site_data)


@mcp.tool()
def subscription_summary() -> dict:
    """Summarize subscriptions for the configured organization."""

    client = get_client()
    return tools.subscription_summary(client)


@mcp.tool()
def inventory_status_summary(
    site_id: Optional[str] = None, device_types: Optional[List[str]] = None
) -> dict:
    """Summarize device connectivity (connected, disconnected, in-stock) by model."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    return tools.inventory_status_summary(client, site_id=resolved_site, device_types=device_types)


if __name__ == "__main__":
    mcp.run()
