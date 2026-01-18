from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

sys.path.append(str(Path(__file__).resolve().parent))

from prompts import (  # noqa: E402
    acknowledge_alarm_prompt,
    acknowledge_alarms_prompt,
    acknowledge_all_alarms_prompt,
    action_router,
    bounce_device_port_prompt,
    configure_switch_port_profile_prompt,
    create_site_prompt,
    switch_cable_test_prompt,
)
from resources import allowlist  # noqa: E402
from tools import (  # noqa: E402
    acknowledge_alarm,
    acknowledge_alarms,
    acknowledge_all_alarms,
    bounce_device_port,
    configure_switch_port_profile,
    create_site,
    ping_from_device,
    switch_cable_test,
)

mcp = FastMCP("mist-rw")


@mcp.resource("allowlist")
def allowlist_resource():
    return allowlist()


@mcp.tool("configure_switch_port_profile")
def tool_configure_switch_port_profile(
    site_id: str, device_id: str, port_id: str, port_profile_id: str
):
    return configure_switch_port_profile(site_id, device_id, port_id, port_profile_id)


@mcp.tool("bounce_device_port")
def tool_bounce_device_port(site_id: str, device_id: str, ports: list[str]):
    return bounce_device_port(site_id, device_id, ports)


@mcp.tool("create_site")
def tool_create_site(site_data: dict):
    return create_site(site_data)


@mcp.tool("acknowledge_all_alarms")
def tool_ack_all_alarms(site_id: str):
    return acknowledge_all_alarms(site_id)


@mcp.tool("acknowledge_alarms")
def tool_ack_alarms(site_id: str, alarm_ids: list[str]):
    return acknowledge_alarms(site_id, alarm_ids)


@mcp.tool("acknowledge_alarm")
def tool_ack_alarm(site_id: str, alarm_id: str):
    return acknowledge_alarm(site_id, alarm_id)


@mcp.tool("switch_cable_test")
def tool_switch_cable_test(site_id: str, device_id: str, host: str, count: int):
    return switch_cable_test(site_id, device_id, host, count)


@mcp.tool("ping_from_device")
def tool_ping_from_device(site_id: str, device_id: str, host: str, count: int = 4):
    return ping_from_device(site_id, device_id, host, count)


@mcp.prompt("action_router")
def prompt_action(question: str, site: str | None = None):
    return action_router(question, site)


@mcp.prompt("configure_switch_port_profile_prompt")
def prompt_configure_switch_port_profile(
    site_id: str | None = None,
    device_id: str = "",
    port_id: str = "",
    port_profile_id: str = "",
):
    return configure_switch_port_profile_prompt(site_id, device_id, port_id, port_profile_id)


@mcp.prompt("bounce_device_port_prompt")
def prompt_bounce_device_port(
    site_id: str | None = None, device_id: str = "", ports: list[str] | None = None
):
    return bounce_device_port_prompt(site_id, device_id, ports)


@mcp.prompt("create_site_prompt")
def prompt_create_site(site_data: dict | None = None):
    return create_site_prompt(site_data)


@mcp.prompt("acknowledge_all_alarms_prompt")
def prompt_ack_all_alarms(site_id: str | None = None):
    return acknowledge_all_alarms_prompt(site_id)


@mcp.prompt("acknowledge_alarms_prompt")
def prompt_ack_alarms(site_id: str | None = None, alarm_ids: list[str] | None = None):
    return acknowledge_alarms_prompt(site_id, alarm_ids)


@mcp.prompt("acknowledge_alarm_prompt")
def prompt_ack_alarm(site_id: str | None = None, alarm_id: str = ""):
    return acknowledge_alarm_prompt(site_id, alarm_id)


@mcp.prompt("switch_cable_test_prompt")
def prompt_switch_cable_test(
    site_id: str | None = None, device_id: str = "", host: str = "", count: int = 4
):
    return switch_cable_test_prompt(site_id, device_id, host, count)


if __name__ == "__main__":
    mcp.run()
