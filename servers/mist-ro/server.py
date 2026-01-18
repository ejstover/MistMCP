from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

sys.path.append(str(Path(__file__).resolve().parent))

from prompts import action_router, observe_router  # noqa: E402
from resources import allowlist, glossary, kpi_dictionary, site_index  # noqa: E402
from tools import mist_call, mist_resolve  # noqa: E402

mcp = FastMCP("mist-ro")


@mcp.resource("glossary")
def glossary_resource():
    return glossary()


@mcp.resource("allowlist")
def allowlist_resource():
    return allowlist()


@mcp.resource("kpi_dictionary")
def kpi_resource():
    return kpi_dictionary()


@mcp.resource("site_index")
def site_index_resource():
    return site_index(lambda: {"items": [], "updated_at": 0, "count": 0})


@mcp.tool("mist_resolve")
def tool_mist_resolve(site_name: str):
    return mist_resolve(site_name)


@mcp.tool("mist_call")
def tool_mist_call(path: str, site_id: str, method: str = "GET", params: dict | None = None):
    return mist_call(path=path, site_id=site_id, method=method, params=params)


@mcp.prompt("observe_router")
def prompt_observe(question: str, site: str | None = None):
    return observe_router(question, site)


@mcp.prompt("action_router")
def prompt_action(question: str):
    return action_router(question)


if __name__ == "__main__":
    mcp.run()
