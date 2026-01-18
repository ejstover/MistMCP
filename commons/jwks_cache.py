from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional

import httpx
from jwt.algorithms import RSAAlgorithm

DEFAULT_TTL_SECONDS = 60 * 60 * 12


@dataclass
class JWKSCache:
    jwks_url: str
    ttl_seconds: int = DEFAULT_TTL_SECONDS
    timeout_seconds: int = 10

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._last_refresh = 0.0
        self._keys: Dict[str, str] = {}

    def get_key(self, kid: str) -> Optional[str]:
        if not kid:
            return None
        if self._is_expired():
            self.refresh(blocking=False)
        return self._keys.get(kid)

    def refresh(self, blocking: bool = True) -> None:
        if blocking:
            with self._lock:
                self._refresh_locked()
        else:
            thread = threading.Thread(target=self._refresh_safe, daemon=True)
            thread.start()

    def _refresh_safe(self) -> None:
        with self._lock:
            self._refresh_locked()

    def _refresh_locked(self) -> None:
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(self.jwks_url)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError:
            return

        keys = payload.get("keys", []) if isinstance(payload, dict) else []
        updated: Dict[str, str] = {}
        for jwk in keys:
            if jwk.get("kty") != "RSA":
                continue
            kid = jwk.get("kid")
            if not kid:
                continue
            updated[kid] = json.dumps(jwk)

        if updated:
            self._keys = updated
            self._last_refresh = time.time()

    def _is_expired(self) -> bool:
        return (time.time() - self._last_refresh) > self.ttl_seconds


def jwk_to_public_key(jwk_json: str):
    return RSAAlgorithm.from_jwk(jwk_json)
