"""Entry point for the Mist MCP server."""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from .client import MistClient
from .config import MistConfig
from .glossary import GLOSSARY
from . import tools


mcp = FastMCP("mist-mcp")


@mcp.resource(
    "resource://mist-glossary",
    name="mist_glossary",
    title="Juniper Mist MCP Glossary",
    description="Canonical terms, fields, and best practices for Mist MCP usage.",
    mime_type="application/json",
)
def glossary_resource() -> dict:
    """Return the Mist MCP glossary resource."""

    return GLOSSARY


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
def sites_by_country(country_codes: Optional[List[str]] = None) -> dict:
    """Group Mist sites by country with IDs for follow-on calls."""

    client = get_client()
    return tools.sites_by_country(client, country_codes=country_codes)


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
def org_device_summary() -> dict:
    """Return counts of device types across the organization."""

    client = get_client()
    return tools.org_device_summary(client)


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
def list_country_codes() -> dict:
    """List supported country codes from the Mist constants endpoint."""

    client = get_client()
    return tools.list_country_codes(client)



@mcp.tool()
def list_alarm_definitions() -> dict:
    """List definitions for supported alarm types."""

    client = get_client()
    return tools.list_alarm_definitions(client)


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
    title="Sites by country",
    description="Group Mist sites by country code and include IDs for follow-on queries.",
)
def sites_by_country_prompt(country_codes: Optional[List[str]] = None) -> List[dict]:
    """Guide the model to call the sites_by_country tool."""

    country_codes_hint = 'omit or pass an array such as ["US", "CA"]'

    return [
        {
            "role": "system",
            "content": "Use the sites_by_country tool to group sites by country and list site ids.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `sites_by_country` with these parameters and summarize site IDs and names per country.\n"
                f"- country_codes: {country_codes or country_codes_hint}"
            ),
        },
    ]


@mcp.prompt(
    title="Site device counts",
    description="Summarize device counts by type for a Mist site.",
)
def site_device_counts_prompt(site_id: Optional[str] = None) -> List[dict]:
    """Guide the model to call the site_device_counts tool."""

    return [
        {
            "role": "system",
            "content": "Use the site_device_counts tool to tally APs, switches, and other device types.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `site_device_counts` with these parameters and summarize totals by device type.\n"
                f"- site_id: {site_id or 'omit to use the default site id when configured'}"
            ),
        },
    ]



@mcp.prompt(
    title="Subscription summary",
    description="Summarize Mist subscription usage and renewals.",
)
def subscription_summary_prompt() -> List[dict]:
    """Guide the model to call the subscription_summary tool."""

    return [
        {
            "role": "system",
            "content": "Use the subscription_summary tool to report totals, utilization, and the next renewal date.",
        },
        {
            "role": "user",
            "content": "Invoke `subscription_summary` and summarize the returned subscription overview.",
        },
    ]


@mcp.prompt(
    title="List guest authorizations",
    description="List all guest authorizations for the organization.",
)
def list_guest_authorizations_prompt() -> List[dict]:
    """Guide the model to call the list_guest_authorizations tool."""

    return [
        {
            "role": "system",
            "content": "Use the list_guest_authorizations tool to return guest details including codes and expirations.",
        },
        {
            "role": "user",
            "content": "Invoke `list_guest_authorizations` and present the guests in a concise list or table.",
        },
    ]


@mcp.prompt(
    title="Site networks",
    description="Show derived networks configured at a Mist site.",
)
def list_site_networks_prompt(site_id: Optional[str] = None) -> List[dict]:
    """Guide the model to call the list_site_networks tool."""

    return [
        {
            "role": "system",
            "content": "Use the list_site_networks tool to enumerate derived networks for the site.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `list_site_networks` with these parameters and summarize the networks.\n"
                f"- site_id: {site_id or 'omit to use the default site id when set'}"
            ),
        },
    ]


@mcp.prompt(
    title="Site port usages",
    description="Inspect derived port usages for a site to pick the right switch profile.",
)
def site_port_usages_prompt(site_id: Optional[str] = None) -> List[dict]:
    """Guide the model to call the site_port_usages tool."""

    return [
        {
            "role": "system",
            "content": "Use the site_port_usages tool to return port usage definitions from site settings.",
        },
        {
            "role": "user",
            "content": (
                "Invoke `site_port_usages` with these parameters and describe the available port usages.\n"
                f"- site_id: {site_id or 'omit to rely on the default site id'}"
            ),
        },
    ]



@mcp.prompt(
    title="List alarm definitions",
    description="List supported Mist alarm types and their metadata.",
)
def list_alarm_definitions_prompt() -> List[dict]:
    """Guide the model to call the list_alarm_definitions tool."""

    return [
        {
            "role": "system",
            "content": "Use the list_alarm_definitions tool to fetch alarm metadata such as display names and fields.",
        },
        {
            "role": "user",
            "content": "Invoke `list_alarm_definitions` and summarize the available alarm types.",
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
