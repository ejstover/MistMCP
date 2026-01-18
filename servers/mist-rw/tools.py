from __future__ import annotations

import time
from typing import Dict, Iterable, List

import httpx

from resources import allowlist
from settings import MistRWSettings


def configure_switch_port_profile(
    site_id: str,
    device_id: str,
    port_id: str,
    port_profile_id: str,
) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("PUT /devices/{device_id}/switch_ports/{port_id}/local_config")
    payload = {"usage": port_profile_id}
    result = _request(
        "PUT",
        f"{settings.api_base}/sites/{site_id}/devices/{device_id}/switch_ports/{port_id}/local_config",
        payload=payload,
        settings=settings,
    )
    return {"site_id": site_id, "device_id": device_id, "port_id": port_id, "port": result}


def bounce_device_port(site_id: str, device_id: str, ports: Iterable[str]) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /devices/{device_id}/bounce_port")
    port_list = [port for port in ports if port]
    if not port_list:
        raise ValueError("ports cannot be empty")
    payload = {"ports": port_list}
    result = _request(
        "POST",
        f"{settings.api_base}/sites/{site_id}/devices/{device_id}/bounce_port",
        payload=payload,
        settings=settings,
    )
    return {"site_id": site_id, "device_id": device_id, "ports": port_list, "result": result}


def create_site(site_data: Dict[str, object]) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /orgs/{org_id}/sites/create")
    required_fields = ["name", "country_code", "timezone", "address"]
    missing = [field for field in required_fields if not site_data.get(field)]
    if missing:
        raise ValueError(f"Missing required site fields: {', '.join(missing)}")
    result = _request(
        "POST",
        f"{settings.api_base}/orgs/{settings.org_id}/sites/create",
        payload=site_data,
        settings=settings,
    )
    return {"site": result}


def acknowledge_all_alarms(site_id: str) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /alarms/ack/all")
    result = _request(
        "POST",
        f"{settings.api_base}/sites/{site_id}/alarms/ack/all",
        payload={},
        settings=settings,
    )
    return {"site_id": site_id, "result": result}


def acknowledge_alarms(site_id: str, alarm_ids: Iterable[str]) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /alarms/ack")
    alarm_list = [alarm_id for alarm_id in alarm_ids if alarm_id]
    if not alarm_list:
        raise ValueError("alarm_ids cannot be empty")
    payload = {"alarm_ids": alarm_list}
    result = _request(
        "POST",
        f"{settings.api_base}/sites/{site_id}/alarms/ack",
        payload=payload,
        settings=settings,
    )
    return {"site_id": site_id, "alarm_ids": alarm_list, "result": result}


def acknowledge_alarm(site_id: str, alarm_id: str) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /alarms/{alarm_id}/ack")
    if not alarm_id:
        raise ValueError("alarm_id is required")
    result = _request(
        "POST",
        f"{settings.api_base}/sites/{site_id}/alarms/{alarm_id}/ack",
        payload={},
        settings=settings,
    )
    return {"site_id": site_id, "alarm_id": alarm_id, "result": result}


def switch_cable_test(site_id: str, device_id: str, host: str, count: int) -> Dict[str, object]:
    settings = MistRWSettings()
    _ensure_allowed("POST /devices/{device_id}/ping")
    if not host:
        raise ValueError("host is required")
    if count <= 0:
        raise ValueError("count must be a positive integer")
    payload = {"count": count, "host": host}
    result = _request(
        "POST",
        f"{settings.api_base}/sites/{site_id}/devices/{device_id}/ping",
        payload=payload,
        settings=settings,
    )
    return {
        "site_id": site_id,
        "device_id": device_id,
        "host": host,
        "count": count,
        "session": result.get("session") if isinstance(result, dict) else None,
        "ws_channel": f"/sites/{site_id}/devices/{device_id}/cmd",
        "response": result,
    }


def ping_from_device(site_id: str, device_id: str, host: str, count: int = 4) -> Dict[str, object]:
    return switch_cable_test(site_id=site_id, device_id=device_id, host=host, count=count)


def _ensure_allowed(operation: str) -> None:
    if operation not in allowlist():
        raise ValueError("operation not in allowlist")


def _request(
    method: str,
    url: str,
    payload: Dict[str, object],
    settings: MistRWSettings,
) -> Dict[str, object]:
    with httpx.Client(timeout=settings.timeout_seconds) as client:
        for attempt in range(3):
            try:
                response = client.request(
                    method,
                    url,
                    headers=settings.headers(),
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
    return {}
