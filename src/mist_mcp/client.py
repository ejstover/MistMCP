"""Lightweight client for the Juniper Mist REST API."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import requests

from .config import MistConfig


class MistClient:
    """Minimal Mist API wrapper for read-only operations used by the MCP server."""

    def __init__(self, config: MistConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {config.api_token}"})

    def _get(self, path: str, **params) -> dict:
        url = f"{self.config.base_url}{path}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.config.base_url}{path}"
        response = self.session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def _put(self, path: str, payload: dict) -> dict:
        url = f"{self.config.base_url}{path}"
        response = self.session.put(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_inventory(self, site_id: Optional[str] = None, **filters) -> List[dict]:
        """Fetch device inventory for an org or site and apply optional filters.

        Mist supports filtering inventory via query parameters; any additional keyword
        arguments are passed through to the API so the server can perform the filter
        natively when possible.
        """

        if site_id:
            path = f"/api/v1/sites/{site_id}/inventory"
        else:
            path = f"/api/v1/orgs/{self.config.org_id}/inventory"
        payload = self._get(path, **filters)
        return payload if isinstance(payload, list) else payload.get("results", [])

    def find_device_by_identifier(self, identifier: str, site_id: Optional[str] = None) -> List[dict]:
        """Find devices by IP, MAC, or hostname.

        The function first attempts to let Mist perform the filtering by passing query
        parameters when the identifier shape is recognized; it then applies a local
        fallback to ensure results even when the remote API ignores the filter.
        """

        filters: Dict[str, str] = {}
        normalized = identifier.strip().lower()
        if ":" in normalized or "-" in normalized:
            filters["mac"] = normalized
        elif self._looks_like_ip(normalized):
            filters["ip_address"] = normalized
        else:
            filters["hostname"] = normalized

        devices = self.get_inventory(site_id=site_id, **filters)
        return self._filter_devices(devices, normalized)

    def find_client_by_identifier(self, identifier: str, site_id: Optional[str] = None) -> List[dict]:
        """Find clients by IP, MAC, or hostname.

        The method lets Mist handle the filter when possible and then applies a local
        fallback to ensure matches even if the remote API ignores the search query.
        """

        filters: Dict[str, str] = {}
        normalized = identifier.strip().lower()
        if ":" in normalized or "-" in normalized:
            filters["mac"] = normalized
        elif self._looks_like_ip(normalized):
            filters["ip_address"] = normalized
        else:
            filters["hostname"] = normalized

        if site_id:
            path = f"/api/v1/sites/{site_id}/clients/search"
        else:
            path = f"/api/v1/orgs/{self.config.org_id}/clients/search"

        payload = self._get(path, **filters)
        clients = payload if isinstance(payload, list) else payload.get("results", [])
        return self._filter_clients(clients, normalized)

    def list_sites(self, country_codes: Optional[Iterable[str]] = None) -> List[dict]:
        payload = self._get(f"/api/v1/orgs/{self.config.org_id}/sites")
        sites = payload if isinstance(payload, list) else payload.get("results", [])
        if country_codes:
            normalized = {code.upper() for code in country_codes}
            sites = [site for site in sites if site.get("country_code", "").upper() in normalized]
        return sites

    def site_devices(self, site_id: str) -> List[dict]:
        payload = self._get(f"/api/v1/sites/{site_id}/devices")
        return payload if isinstance(payload, list) else payload.get("results", [])

    def site_alarms(self, site_id: str, minutes: int = 60) -> List[dict]:
        """Retrieve recent site alarms.

        The Mist API accepts a ``duration`` parameter in minutes to constrain results.
        """

        payload = self._get(f"/api/v1/sites/{site_id}/alarms", duration=minutes)
        return payload if isinstance(payload, list) else payload.get("results", [])

    def get_switch_ports(self, site_id: str, device_id: str) -> List[dict]:
        """Return switch port details for a device."""

        payload = self._get(f"/api/v1/sites/{site_id}/devices/{device_id}/switch_ports")
        return payload if isinstance(payload, list) else payload.get("results", [])

    def set_switch_port_profile(
        self, site_id: str, device_id: str, port_id: str, port_profile_id: str
    ) -> dict:
        """Apply a port profile to a switch port."""

        body = {"portconf_id": port_profile_id}
        return self._put(
            f"/api/v1/sites/{site_id}/devices/{device_id}/switch_ports/{port_id}",
            payload=body,
        )

    def create_site(self, site_data: dict) -> dict:
        """Create a new Mist site with the provided metadata."""

        return self._post(f"/api/v1/orgs/{self.config.org_id}/sites", payload=site_data)

    def list_subscriptions(self) -> List[dict]:
        """List subscriptions for the organization."""

        payload = self._get(f"/api/v1/orgs/{self.config.org_id}/subscriptions")
        return payload if isinstance(payload, list) else payload.get("results", [])

    @staticmethod
    def _looks_like_ip(identifier: str) -> bool:
        parts = identifier.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def _filter_devices(devices: List[dict], identifier: str) -> List[dict]:
        """Ensure results contain the identifier even if the API does not filter."""

        def matches(device: dict) -> bool:
            for key in ("mac", "mac_address", "ip", "ip_address", "hostname", "name"):
                value = device.get(key)
                if isinstance(value, str) and identifier in value.lower():
                    return True
            return False

        filtered = [device for device in devices if matches(device)]
        return filtered or devices

    @staticmethod
    def _filter_clients(clients: List[dict], identifier: str) -> List[dict]:
        """Ensure client results contain the identifier even if the API does not filter."""

        def matches(client: dict) -> bool:
            for key in ("mac", "mac_address", "ip", "ip_address", "hostname", "name"):
                value = client.get(key)
                if isinstance(value, str) and identifier in value.lower():
                    return True
            return False

        filtered = [client for client in clients if matches(client)]
        return filtered or clients
