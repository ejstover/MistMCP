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
def list_guest_authorizations() -> dict:
    """List all guest authorizations in the organization."""

    client = get_client()
    return tools.list_guest_authorizations(client)


@mcp.tool()
def list_site_networks(site_id: Optional[str] = None) -> dict:
    """List derived networks for a site."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    return tools.list_site_networks(client, site_id=resolved_site)


@mcp.tool()
def site_port_usages(site_id: Optional[str] = None) -> dict:
    """Return derived site port usages to help select the correct switch profile."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    return tools.site_setting_port_usages(client, site_id=resolved_site)


@mcp.tool()
def acknowledge_all_alarms(site_id: Optional[str] = None) -> dict:
    """Acknowledge all alarms for a site."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    return tools.acknowledge_all_alarms(client, site_id=resolved_site)


@mcp.tool()
def acknowledge_alarms(site_id: Optional[str] = None, alarm_ids: List[str] = None) -> dict:
    """Acknowledge specific alarms for a site."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    if not alarm_ids:
        raise ValueError("alarm_ids cannot be empty")
    return tools.acknowledge_alarms(client, site_id=resolved_site, alarm_ids=alarm_ids)


@mcp.tool()
def acknowledge_alarm(site_id: Optional[str] = None, alarm_id: str = "") -> dict:
    """Acknowledge a single alarm for a site."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    if not resolved_site:
        raise ValueError("site_id is required when MIST_DEFAULT_SITE_ID is not set")
    if not alarm_id:
        raise ValueError("alarm_id is required")
    return tools.acknowledge_alarm(client, site_id=resolved_site, alarm_id=alarm_id)


@mcp.tool()
def inventory_status_summary(
    site_id: Optional[str] = None, device_types: Optional[List[str]] = None
) -> dict:
    """Summarize device connectivity (connected, disconnected, in-stock) by model."""

    client = get_client()
    resolved_site = site_id or client.config.default_site_id
    return tools.inventory_status_summary(client, site_id=resolved_site, device_types=device_types)


@mcp.prompt(
    title="Inventory overview",
    description="Summarize Mist device connectivity by model, optionally filtered to a site or device types.",
)
def inventory_overview_prompt(
    site_id: Optional[str] = None, device_types: Optional[List[str]] = None
) -> List[dict]:
    """Guide the model to call the inventory_status_summary tool."""

    default_device_types = "omit or pass a list such as ['ap', 'switch']"

    return [
        {
            "role": "system",
            "content": "Use the inventory_status_summary tool to report connected, disconnected, and in-stock counts by model.",
        },
        {
            "role": "user",
            "content": (
                "Call `inventory_status_summary` with the provided arguments and summarize totals and by-model counts.\n"
                f"- site_id: {site_id or 'omit to use the organization or default site scope'}\n"
                f"- device_types: {device_types or default_device_types}"
            ),
        },
    ]


@mcp.prompt(
    title="Find a device",
    description="Look up a Mist device by IP, MAC, or hostname and return matches.",
)
def device_lookup_prompt(identifier: str, site_id: Optional[str] = None) -> List[dict]:
    """Guide the model to call the find_device tool."""

    return [
        {
            "role": "system",
            "content": "Use the find_device tool to search inventory for device details including site and model.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `find_device` with these parameters and present the resulting matches.\n"
                f"- identifier: {identifier}\n"
                f"- site_id: {site_id or 'omit to search the organization or default site'}"
            ),
        },
    ]


@mcp.prompt(
    title="Find a client",
    description="Look up a Mist client by IP, MAC, or hostname and return matches.",
)
def client_lookup_prompt(identifier: str, site_id: Optional[str] = None) -> List[dict]:
    """Guide the model to call the find_client tool."""

    return [
        {
            "role": "system",
            "content": "Use the find_client tool to search connected or historical clients including VLAN and AP details.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `find_client` with these parameters and present the resulting matches.\n"
                f"- identifier: {identifier}\n"
                f"- site_id: {site_id or 'omit to search the organization or default site'}"
            ),
        },
    ]


@mcp.prompt(
    title="List Mist sites",
    description="List Mist sites optionally filtered by country codes.",
)
def list_sites_prompt(country_codes: Optional[List[str]] = None) -> List[dict]:
    """Guide the model to call the list_sites tool."""

    country_codes_hint = 'omit or pass an array such as ["DE", "NL"]'

    return [
        {
            "role": "system",
            "content": "Use the list_sites tool to enumerate Mist sites and include names and IDs in the reply.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `list_sites` with these parameters and present the sites in a short table.\n"
                f"- country_codes: {country_codes or country_codes_hint}"
            ),
        },
    ]


@mcp.prompt(
    title="Site issues",
    description="Check for recent site alarms across specific sites or countries.",
)
def site_errors_prompt(
    minutes: int = 60, site_ids: Optional[List[str]] = None, country_codes: Optional[List[str]] = None
) -> List[dict]:
    """Guide the model to call the sites_with_recent_errors tool."""

    return [
        {
            "role": "system",
            "content": "Use the sites_with_recent_errors tool to summarize active alarms for Mist sites.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `sites_with_recent_errors` with the provided filters and report alarms grouped by site.\n"
                f"- minutes: {minutes}\n"
                f"- site_ids: {site_ids or 'omit to rely on country_codes or default site'}\n"
                f"- country_codes: {country_codes or 'omit to search all sites available'}"
            ),
        },
    ]


if __name__ == "__main__":
    mcp.run()
