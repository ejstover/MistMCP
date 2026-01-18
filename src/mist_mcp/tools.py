"""Deprecated legacy tools module for the Mist MCP server."""

from __future__ import annotations

import warnings


DEPRECATION_MESSAGE = (
    "mist_mcp.tools is deprecated; use the dedicated servers in "
    "servers/mist-ro or servers/mist-rw."
)


warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)


def __getattr__(name: str) -> object:
    raise AttributeError(
        f"{DEPRECATION_MESSAGE} The legacy tools module no longer exposes {name!r}."
    )


__all__: list[str] = []
