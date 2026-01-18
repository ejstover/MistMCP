from __future__ import annotations


def observe_router(question: str, site: str | None = None) -> str:
    site_clause = f" for site {site}" if site else ""
    return (
        "You are a read-only Mist observer."
        " Use only read-only tools."
        " Consult the glossary and allowlist first."
        f" Plan minimal calls.{site_clause}"
        " Return a compact table and 2-3 bullet insights. No writes."
    )


def action_router(question: str) -> str:
    return (
        "Read-only server: actions are dry-run only."
        " Provide a plan and request explicit confirmation before any write."
    )
