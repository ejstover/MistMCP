from __future__ import annotations

import json
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Policy:
    version: str
    tools: Dict[str, dict]
    scopes: Dict[str, dict]


def load_policy(path: str) -> Policy:
    payload = json.loads(Path(path).read_text())
    return Policy(
        version=payload.get("version", ""),
        tools=payload.get("tools", {}),
        scopes=payload.get("scopes", {}),
    )


def authorize(
    policy: Policy,
    user_roles: List[str],
    tool_name: str,
    verb: str,
    site: Optional[str],
    site_scope: List[str],
    commit: bool = False,
    confirmation: Optional[str] = None,
) -> Tuple[bool, str, bool]:
    tool_policy = policy.tools.get(tool_name)
    if not tool_policy:
        return False, "Tool not allowed", False

    allowed_roles = tool_policy.get("allow", [])
    if not any(role in allowed_roles for role in user_roles):
        return False, "Role not permitted", False

    if site and not _site_allowed(site, site_scope):
        return False, "Site scope denied", False

    commit_requires = tool_policy.get("commit_requires", [])
    if commit:
        if "explicit_confirm" in commit_requires and not confirmation:
            return False, "Commit confirmation missing", False
        if "ReadWrite" not in user_roles:
            return False, "Commit requires ReadWrite", False
        return True, "Committed", True

    return True, "Dry-run", False


def _site_allowed(site: str, allowed_scopes: List[str]) -> bool:
    if not allowed_scopes:
        return False
    return any(fnmatch(site, pattern) for pattern in allowed_scopes)
