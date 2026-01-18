from __future__ import annotations

import random
import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict, Tuple


@dataclass
class CacheEntry:
    value: dict
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int = 300, jitter_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self.jitter_seconds = jitter_seconds
        self._lock = threading.Lock()
        self._data: Dict[str, CacheEntry] = {}

    def get_or_set(self, key: str, loader: Callable[[], dict]) -> Tuple[dict, bool]:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if entry and entry.expires_at > now:
                return entry.value, False

        value = loader()
        expires_at = now + self.ttl_seconds + random.randint(0, self.jitter_seconds)
        with self._lock:
            self._data[key] = CacheEntry(value=value, expires_at=expires_at)
        return value, True
