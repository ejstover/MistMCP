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

    def org_device_summary(self) -> dict:
        """Return device counts for the configured organization."""

        payload = self._get(f"/api/v1/orgs/{self.config.org_id}/devices/summary")
        return payload if isinstance(payload, dict) else {}

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
        """Find clients by IP, MAC, or hostname across wired and wireless searches."""

        filters: Dict[str, str] = {}
        normalized = identifier.strip().lower()
        if ":" in normalized or "-" in normalized:
            filters["mac"] = normalized
        elif self._looks_like_ip(normalized):
            filters["ip_address"] = normalized
        else:
            filters["hostname"] = normalized

        if site_id:
            filters["site_id"] = site_id

        wired = self.search_wired_clients(**filters)
        wireless = self.search_wireless_clients(**filters)
        clients = [*wired, *wireless]
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

        payload = self._get(f"/api/v1/sites/{site_id}/alarms/search", duration=minutes)
        return payload if isinstance(payload, list) else payload.get("results", [])

    def get_switch_ports(self, site_id: str, device_id: str) -> List[dict]:
        """Return switch port details for a device."""

        payload = self._get(f"/api/v1/sites/{site_id}/devices/{device_id}/switch_ports")
        return payload if isinstance(payload, list) else payload.get("results", [])

    def update_switch_port_config(
        self, site_id: str, device_id: str, port_id: str, usage_id: str
    ) -> dict:
        """Apply a local switch port usage to a port using the site-local endpoint."""

        body = {"usage": usage_id}
        return self._put(
            f"/api/v1/sites/{site_id}/devices/{device_id}/switch_ports/{port_id}/local_config",
            payload=body,
        )

    def create_site(self, site_data: dict) -> dict:
        """Create a new Mist site with the provided metadata."""

        return self._post(
            f"/api/v1/orgs/{self.config.org_id}/sites/create", payload=site_data
        )

    def license_summary(self) -> List[dict]:
        """Summarize licenses for the organization."""

        payload = self._get(f"/api/v1/orgs/{self.config.org_id}/licenses/summary")
        return payload if isinstance(payload, list) else payload.get("results", [])

    def search_wired_clients(self, **filters) -> List[dict]:
        """Search wired clients using the dedicated Mist endpoint."""

        payload = self._get(
            f"/api/v1/orgs/{self.config.org_id}/wired_clients/search", **filters
        )
        return payload if isinstance(payload, list) else payload.get("results", [])

    def search_wireless_clients(self, **filters) -> List[dict]:
        """Search wireless clients using the dedicated Mist endpoint."""

        payload = self._get(
            f"/api/v1/orgs/{self.config.org_id}/clients/search", **filters
        )
        return payload if isinstance(payload, list) else payload.get("results", [])

    def list_guest_authorizations(self) -> List[dict]:
        """List guest authorizations across the organization."""

        payload = self._get(
            f"/api/v1/orgs/{self.config.org_id}/guests/authorizations"
        )
        return payload if isinstance(payload, list) else payload.get("results", [])

    def list_site_networks(self, site_id: str) -> List[dict]:
        """List derived networks for a site."""

        payload = self._get(f"/api/v1/sites/{site_id}/networks/derived")
        return payload if isinstance(payload, list) else payload.get("results", [])

    def get_site_setting(self, site_id: str) -> dict:
        """Retrieve derived site setting including port usages."""

        return self._get(f"/api/v1/sites/{site_id}/setting/derived")

    def acknowledge_all_site_alarms(self, site_id: str) -> dict:
        """Acknowledge all alarms at a site."""

        return self._post(f"/api/v1/sites/{site_id}/alarms/ack/all", payload={})

    def acknowledge_site_alarms(self, site_id: str, alarm_ids: Iterable[str]) -> dict:
        """Acknowledge specific alarms at a site."""

        body = {"alarm_ids": list(alarm_ids)}
        return self._post(f"/api/v1/sites/{site_id}/alarms/ack", payload=body)

    def acknowledge_site_alarm(self, site_id: str, alarm_id: str) -> dict:
        """Acknowledge a single alarm at a site."""

        return self._post(
            f"/api/v1/sites/{site_id}/alarms/{alarm_id}/ack", payload={}
        )

    def ping_from_device(self, site_id: str, device_id: str, count: int, host: str) -> dict:
        """Trigger a device-originated ping and return the command session details."""

        body = {"count": count, "host": host}
        return self._post(
            f"/api/v1/sites/{site_id}/devices/{device_id}/ping", payload=body
        )

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
