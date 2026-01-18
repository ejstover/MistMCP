from __future__ import annotations

import json
import logging
import logging.config
from typing import Any, Dict

SENSITIVE_KEYS = {
    "authorization",
    "token",
    "access_token",
    "refresh_token",
    "mist_token_ro",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if isinstance(record.args, dict):
            payload.update(record.args)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)
        return json.dumps(mask_sensitive(payload), ensure_ascii=False)


def mask_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: mask_sensitive_value(k, v) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    return value


def mask_sensitive_value(key: str, value: Any) -> Any:
    if key.lower() in SENSITIVE_KEYS:
        return "***"
    if isinstance(value, dict):
        return mask_sensitive(value)
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    return value


def setup_logging(level: str = "INFO") -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                }
            },
            "root": {"handlers": ["default"], "level": level},
        }
    )
