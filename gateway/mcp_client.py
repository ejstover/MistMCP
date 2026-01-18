from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Dict

from commons.logging_conf import mask_sensitive

logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self) -> None:
        self.tools = {
            "mist_call_get": self._stub_tool,
            "mistql_observe": self._stub_tool,
            "mist_call_write": self._stub_tool,
        }

    def _stub_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "ok",
            "note": "stub tool executed",
            "params": params,
        }

    def call_tool(
        self, tool_name: str, params: Dict[str, Any], user: Dict[str, Any], commit: bool
    ) -> Dict[str, Any]:
        req_id = str(uuid.uuid4())
        start = time.time()
        tool_fn = self.tools.get(tool_name)
        status = "error"
        response: Dict[str, Any] = {"error": "tool not found"}
        if tool_fn:
            response = tool_fn(params)
            status = "ok"
        latency_ms = int((time.time() - start) * 1000)
        logger.info(
            "tool_call",
            {
                "extra": {
                    "ts": time.time(),
                    "req_id": req_id,
                    "user_id": user.get("id"),
                    "roles": user.get("roles"),
                    "tool": tool_name,
                    "params_masked": mask_sensitive(params),
                    "committed": commit,
                    "latency_ms": latency_ms,
                    "status": status,
                }
            },
        )
        return response


class StubModel:
    def generate(self, message: str) -> Dict[str, Any]:
        return {
            "reply": f"Stub model response: {message}",
            "tool": None,
        }

    def generate_with_tool(self, message: str) -> Dict[str, Any]:
        if message.startswith("tool:"):
            payload = message[len("tool:") :]
            tool_name, _, raw = payload.partition(":")
            params = json.loads(raw) if raw else {}
            return {
                "reply": f"Calling tool {tool_name} with params.",
                "tool": tool_name,
                "params": params,
            }
        return self.generate(message)
