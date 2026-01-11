"""Tool implementations exposed via the MCP server."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .client import MistClient


def find_device(client: MistClient, identifier: str, site_id: Optional[str] = None) -> Dict[str, List[dict]]:
    """Find device inventory entries by IP, MAC, or hostname for a site or the org."""

    matches = client.find_device_by_identifier(identifier, site_id=site_id)
    return {"matches": matches}


def find_client(client: MistClient, identifier: str, site_id: Optional[str] = None) -> Dict[str, List[dict]]:
    """Find connected or historical clients by IP, MAC, or hostname."""

    matches = client.find_client_by_identifier(identifier, site_id=site_id)
    return {"matches": matches}


def list_sites(client: MistClient, country_codes: Optional[Iterable[str]] = None) -> Dict[str, List[dict]]:
    """List sites, optionally filtered by country codes."""

    sites = client.list_sites(country_codes=country_codes)
    return {"sites": sites}


def sites_by_country(client: MistClient, country_codes: Optional[Iterable[str]] = None) -> Dict[str, List[dict]]:
    """Group sites by country code with IDs and names for follow-on queries."""

    sites = client.list_sites(country_codes=country_codes)
    grouped: Dict[str, List[Dict[str, object]]] = {}

    for site in sites:
        country_code = str(site.get("country_code") or "").upper()
        site_id = site.get("id")
        if not country_code or not site_id:
            continue

        grouped.setdefault(country_code, []).append(
            {
                "id": site_id,
                "name": site.get("name"),
                "timezone": site.get("timezone"),
            }
        )

    countries = [
        {
            "country_code": code,
            "site_count": len(site_list),
            "sites": sorted(site_list, key=lambda site: str(site.get("name") or site.get("id"))),
        }
        for code, site_list in sorted(grouped.items())
    ]

    return {"countries": countries}


def site_device_counts(client: MistClient, site_id: str) -> Dict[str, Dict[str, int]]:
    """Summarize device counts for a site by device type."""

    devices = client.site_devices(site_id)
    counts: Dict[str, int] = {}
    for device in devices:
        device_type = str(device.get("type", "unknown")).lower()
        counts[device_type] = counts.get(device_type, 0) + 1
    return {"site_id": site_id, "device_counts": counts}


def sites_with_recent_errors(client: MistClient, site_ids: Iterable[str], minutes: int = 60) -> Dict[str, List[dict]]:
    """Return alarms for the provided sites within the given time window."""

    results: List[dict] = []
    for site_id in site_ids:
        alarms = client.site_alarms(site_id, minutes=minutes)
        for alarm in alarms:
            alarm["site_id"] = site_id
        results.extend(alarms)
    return {"alarms": results}


def configure_switch_port_profile(
    client: MistClient,
    site_id: str,
    device_id: str,
    port_id: str,
    port_profile_id: str,
) -> Dict[str, dict]:
    """Apply a Mist port usage profile to a specific switch port."""

    updated_port = client.update_switch_port_config(
        site_id=site_id, device_id=device_id, port_id=port_id, usage_id=port_profile_id
    )
    return {"site_id": site_id, "device_id": device_id, "port_id": port_id, "port": updated_port}


def bounce_device_port(
    client: MistClient,
    site_id: str,
    device_id: str,
    ports: Iterable[str],
) -> Dict[str, object]:
    """Bounce one or more switch ports on a device."""

    port_list = [port for port in ports if port]
    if not port_list:
        raise ValueError("ports cannot be empty")

    result = client.bounce_device_port(site_id=site_id, device_id=device_id, ports=port_list)
    return {"site_id": site_id, "device_id": device_id, "ports": port_list, "result": result}


def create_site(client: MistClient, site_data: Dict[str, object]) -> Dict[str, dict]:
    """Create a Mist site after verifying required fields are present."""

    required_fields = ["name", "country_code", "timezone", "address"]
    missing = [field for field in required_fields if not site_data.get(field)]
    if missing:
        raise ValueError(f"Missing required site fields: {', '.join(missing)}")

    new_site = client.create_site(site_data)
    return {"site": new_site}


def subscription_summary(client: MistClient) -> Dict[str, object]:
    """Summarize organization subscriptions and return raw details."""

    subscriptions = client.license_summary()

    def _parse_int(value: object) -> int:
        try:
            return int(value) if value is not None else 0
        except (TypeError, ValueError):
            return 0

    total_available = 0
    total_used = 0
    renewal_candidates: List[str] = []
    for sub in subscriptions:
        total_available += _parse_int(sub.get("total") or sub.get("count") or sub.get("quantity"))
        total_used += _parse_int(sub.get("used") or sub.get("assigned") or sub.get("consumed"))

        for key in ("renewal_date", "renewal", "expires_on", "expiration", "expiration_date"):
            value = sub.get(key)
            if isinstance(value, str) and value:
                renewal_candidates.append(value)
                break

    renewal_candidates.sort()
    next_renewal = renewal_candidates[0] if renewal_candidates else None

    summary = {
        "total_subscriptions": len(subscriptions),
        "total_available": total_available,
        "total_used": total_used,
        "next_renewal": next_renewal,
    }

    return {"summary": summary, "subscriptions": subscriptions}


def list_guest_authorizations(client: MistClient) -> Dict[str, List[dict]]:
    """List all guest authorizations in the organization."""

    guests = client.list_guest_authorizations()
    return {"guests": guests}


def list_site_networks(client: MistClient, site_id: str) -> Dict[str, List[dict]]:
    """List derived networks at a site."""

    networks = client.list_site_networks(site_id)
    return {"site_id": site_id, "networks": networks}


def org_device_summary(client: MistClient) -> Dict[str, int]:
    """Return counts of devices across the organization."""

    summary = client.org_device_summary()
    return {"summary": summary}


def site_setting_port_usages(client: MistClient, site_id: str) -> Dict[str, object]:
    """Return derived site settings focusing on port usages."""

    setting = client.get_site_setting(site_id)
    return {
        "site_id": site_id,
        "port_usages": setting.get("port_usages", []) if isinstance(setting, dict) else [],
        "setting": setting,
    }


def list_country_codes(client: MistClient) -> Dict[str, List[dict]]:
    """List supported country codes for the Mist dashboard."""

    countries = client.list_country_codes()
    return {"countries": countries}


def acknowledge_all_alarms(client: MistClient, site_id: str) -> Dict[str, object]:
    """Acknowledge all alarms at a site."""

    result = client.acknowledge_all_site_alarms(site_id)
    return {"site_id": site_id, "result": result}


def acknowledge_alarms(client: MistClient, site_id: str, alarm_ids: Iterable[str]) -> Dict[str, object]:
    """Acknowledge multiple alarms at a site."""

    result = client.acknowledge_site_alarms(site_id, alarm_ids)
    return {"site_id": site_id, "alarm_ids": list(alarm_ids), "result": result}


def acknowledge_alarm(client: MistClient, site_id: str, alarm_id: str) -> Dict[str, object]:
    """Acknowledge a single alarm at a site."""

    result = client.acknowledge_site_alarm(site_id, alarm_id)
    return {"site_id": site_id, "alarm_id": alarm_id, "result": result}


def switch_cable_test(
    client: MistClient,
    site_id: str,
    device_id: str,
    host: str,
    count: int,
) -> Dict[str, object]:
    """Trigger a switch cable test (TDR) ping command and return session metadata."""

    result = client.run_switch_cable_test(site_id=site_id, device_id=device_id, host=host, count=count)
    channel = f"/sites/{site_id}/devices/{device_id}/cmd"
    return {
        "site_id": site_id,
        "device_id": device_id,
        "host": host,
        "count": count,
        "session": result.get("session"),
        "ws_channel": channel,
        "response": result,
    }


def inventory_status_summary(
    client: MistClient,
    site_id: Optional[str] = None,
    device_types: Optional[Iterable[str]] = None,
) -> Dict[str, object]:
    """Summarize inventory connectivity by model with in-stock tracking.

    Args:
        site_id: Optional site to scope the inventory request. When omitted the
            organization inventory is used.
        device_types: Optional iterable of device types (for example, ``ap`` or
            ``switch``) used to filter the response.

    Returns:
        A dictionary containing overall totals and per-model connectivity
        breakdowns including in-stock counts (devices that have never
        connected).
    """

    devices = client.get_inventory(site_id=site_id)
    if device_types:
        normalized_types = {str(value).lower() for value in device_types}
        devices = [
            device
            for device in devices
            if str(device.get("type", "")).lower() in normalized_types
        ]

    def _classify(device: dict) -> Dict[str, bool]:
        status = str(device.get("status", "")).lower()
        connected_flag = device.get("connected") is True or status in {"connected", "online"}
        last_seen = device.get("last_seen") or device.get("last_seen_ts") or device.get("last_seen_epoch")
        ever_connected = connected_flag or bool(last_seen)

        if connected_flag:
            return {"connected": True, "disconnected": False, "in_stock": False}
        if not ever_connected:
            return {"connected": False, "disconnected": False, "in_stock": True}
        return {"connected": False, "disconnected": True, "in_stock": False}

    overall = {"total": 0, "connected": 0, "disconnected": 0, "in_stock": 0}
    per_model: Dict[str, Dict[str, int]] = {}

    for device in devices:
        model = str(device.get("model") or "unknown")
        flags = _classify(device)

        overall["total"] += 1
        for key, value in flags.items():
            if value:
                overall[key] += 1

        if model not in per_model:
            per_model[model] = {"total": 0, "connected": 0, "disconnected": 0, "in_stock": 0}

        per_model[model]["total"] += 1
        for key, value in flags.items():
            if value:
                per_model[model][key] += 1

    by_model = [
        {"model": model, **counts}
        for model, counts in sorted(per_model.items())
    ]

    return {"summary": overall, "by_model": by_model}
