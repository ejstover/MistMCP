from __future__ import annotations

from typing import Dict

from caching import TTLCache

SITE_CACHE = TTLCache(ttl_seconds=1800, jitter_seconds=600)


def glossary() -> Dict[str, str]:
    return {
        "firmware": "Version or firmware release on a device",
        "os": "Operating system or firmware family",
        "cpu": "Device CPU utilization",
        "score": "Mist site score (0-100)",
        "ssid": "Wi-Fi network name",
        "rssi": "Received signal strength indicator",
        "snr": "Signal-to-noise ratio",
    }


def allowlist() -> Dict[str, str]:
    return {
        "GET /stats/summary": "Site summary",
        "GET /devices": "Site devices",
    }


def kpi_dictionary() -> Dict[str, str]:
    return {
        "site_score": "Aggregate site health score (0-100)",
        "wired_clients": "Count of wired clients",
        "wireless_clients": "Count of wireless clients",
    }


def site_index(loader) -> Dict[str, object]:
    payload, refreshed = SITE_CACHE.get_or_set("site-index", loader)
    payload["refreshed"] = refreshed
    return payload
