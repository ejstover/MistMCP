from __future__ import annotations

import time
from typing import Any, Dict, List

import httpx

from caching import TTLCache
from resources import allowlist, site_index
from settings import MistSettings

SITE_CACHE = TTLCache(ttl_seconds=1800, jitter_seconds=600)


def mist_resolve(site_name: str) -> Dict[str, str]:
    settings = MistSettings()

    def loader() -> dict:
        with httpx.Client(timeout=settings.timeout_seconds) as client:
            response = client.get(
                f"{settings.api_base}/orgs/{settings.org_id}/sites",
                headers=settings.headers(),
            )
            response.raise_for_status()
            sites = response.json()
        return {"items": sites, "updated_at": time.time(), "count": len(sites)}

    index = site_index(loader)
    for site in index.get("items", []):
        if site.get("name", "").lower() == site_name.lower():
            return {"name": site.get("name"), "site_id": site.get("id")}
    return {"name": site_name, "site_id": ""}


def mist_call(
    path: str,
    site_id: str,
    method: str = "GET",
    params: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    if method.upper() != "GET":
        return {"error": "read-only server: only GET allowed"}

    allowed = allowlist()
    if not any(_matches_allowlist(path, template) for template in allowed):
        return {"error": "endpoint not in allowlist"}

    settings = MistSettings()
    url = f"{settings.api_base}/sites/{site_id}{path}"
    params = params or {}
    results: List[Dict[str, Any]] = []

    with httpx.Client(timeout=settings.timeout_seconds) as client:
        next_url: str | None = url
        while next_url:
            for attempt in range(3):
                try:
                    response = client.get(next_url, headers=settings.headers(), params=params)
                    response.raise_for_status()
                    payload = response.json()
                    if isinstance(payload, list):
                        results.extend(payload)
                        next_url = None
                    elif isinstance(payload, dict) and "results" in payload:
                        results.extend(payload.get("results", []))
                        next_url = payload.get("next")
                    else:
                        results.append(payload)
                        next_url = None
                    break
                except httpx.HTTPError:
                    if attempt == 2:
                        raise
                    time.sleep(2**attempt)
            if next_url:
                params = {}

    return {"items": results, "count": len(results)}


def _matches_allowlist(path: str, template: str) -> bool:
    normalized = template.split(" ", 1)[-1].strip()
    return path.startswith(normalized)
