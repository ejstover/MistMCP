from __future__ import annotations

from typing import List, Optional


def action_router(question: str, site: Optional[str] = None) -> str:
    site_clause = f" for site {site}" if site else ""
    return (
        "You are a write-capable Mist operator."
        " Require explicit confirmation and commit=true for any write."
        " Summarize intended changes before executing."
        f" Use the site scope guardrails.{site_clause}"
    )


def configure_switch_port_profile_prompt(
    site_id: Optional[str] = None,
    device_id: str = "",
    port_id: str = "",
    port_profile_id: str = "",
) -> List[dict]:
    return [
        {
            "role": "system",
            "content": "Use configure_switch_port_profile only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": (
                "Invoke configure_switch_port_profile with:\n"
                f"- site_id: {site_id or 'required'}\n"
                f"- device_id: {device_id or 'required'}\n"
                f"- port_id: {port_id or 'required'}\n"
                f"- port_profile_id: {port_profile_id or 'required'}"
            ),
        },
    ]


def bounce_device_port_prompt(
    site_id: Optional[str] = None,
    device_id: str = "",
    ports: Optional[List[str]] = None,
) -> List[dict]:
    port_hint = ports or ["ge-0/0/0", "ge-0/0/1"]
    return [
        {
            "role": "system",
            "content": "Use bounce_device_port only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": (
                "Invoke bounce_device_port with:\n"
                f"- site_id: {site_id or 'required'}\n"
                f"- device_id: {device_id or 'required'}\n"
                f"- ports: {port_hint}"
            ),
        },
    ]


def create_site_prompt(site_data: Optional[dict] = None) -> List[dict]:
    site_hint = site_data or {
        "name": "Site name",
        "country_code": "US",
        "timezone": "America/New_York",
        "address": "123 Main St, Anytown",
    }
    return [
        {
            "role": "system",
            "content": "Use create_site only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": f"Invoke create_site with site_data: {site_hint}",
        },
    ]


def acknowledge_all_alarms_prompt(site_id: Optional[str] = None) -> List[dict]:
    return [
        {
            "role": "system",
            "content": "Use acknowledge_all_alarms only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": f"Invoke acknowledge_all_alarms with site_id: {site_id or 'required'}",
        },
    ]


def acknowledge_alarms_prompt(
    site_id: Optional[str] = None, alarm_ids: Optional[List[str]] = None
) -> List[dict]:
    alarm_list = alarm_ids or ["alarm-id-1", "alarm-id-2"]
    return [
        {
            "role": "system",
            "content": "Use acknowledge_alarms only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": (
                "Invoke acknowledge_alarms with:\n"
                f"- site_id: {site_id or 'required'}\n"
                f"- alarm_ids: {alarm_list}"
            ),
        },
    ]


def acknowledge_alarm_prompt(site_id: Optional[str] = None, alarm_id: str = "") -> List[dict]:
    return [
        {
            "role": "system",
            "content": "Use acknowledge_alarm only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": (
                "Invoke acknowledge_alarm with:\n"
                f"- site_id: {site_id or 'required'}\n"
                f"- alarm_id: {alarm_id or 'required'}"
            ),
        },
    ]


def switch_cable_test_prompt(
    site_id: Optional[str] = None,
    device_id: str = "",
    host: str = "",
    count: int = 4,
) -> List[dict]:
    return [
        {
            "role": "system",
            "content": "Use switch_cable_test only after explicit confirmation.",
        },
        {
            "role": "user",
            "content": (
                "Invoke switch_cable_test with:\n"
                f"- site_id: {site_id or 'required'}\n"
                f"- device_id: {device_id or 'required'}\n"
                f"- host: {host or 'required'}\n"
                f"- count: {count}"
            ),
        },
    ]
