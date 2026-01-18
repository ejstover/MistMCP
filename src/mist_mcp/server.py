"""Deprecated entry point for the legacy Mist MCP server."""

from __future__ import annotations

import sys
import textwrap
import warnings


DEPRECATION_MESSAGE = """
The legacy all-in-one server module (mist_mcp.server) has been deprecated.

Use the dedicated read-only or read-write servers instead:
  - servers/mist-ro
  - servers/mist-rw
"""


def _emit_warning() -> None:
    warnings.warn(
        textwrap.dedent(DEPRECATION_MESSAGE).strip(),
        DeprecationWarning,
        stacklevel=2,
    )


def main() -> None:
    """Print a deprecation warning and exit."""

    _emit_warning()
    sys.stderr.write(textwrap.dedent(DEPRECATION_MESSAGE).strip() + "\n")


if __name__ == "__main__":
    main()
