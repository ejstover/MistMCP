"""Glossary resource for Mist MCP."""

GLOSSARY = {
    "meta": {
        "name": "Juniper Mist MCP Glossary",
        "version": "v1",
        "updated_at": "2026-01-18T00:00:00Z",
        "notes": [
            "Use these canonical names when selecting fields/endpoints.",
            "Prefer org/site-scoped queries, then filter client/device results.",
            "When synonyms map to multiple Mist fields, try the canonical key first, then fallbacks in order.",
        ],
    },
    "entities": {
        "org": ["org", "organization", "tenant"],
        "sites": ["site", "location", "plant", "facility", "building", "campus"],
        "devices.ap": ["ap", "access point", "aps", "wifi ap", "radio"],
        "devices.switch": ["switch", "ex", "switches", "edge switch", "core switch"],
        "devices.gateway": ["gateway", "ssr", "wan edge", "router"],
        "clients": ["client", "endpoint", "station", "device", "host", "user device"],
    },
    "identifiers": {
        "mac": ["mac", "mac address"],
        "ip": ["ip", "ip address", "ipv4"],
        "hostname": ["hostname", "device name", "client name"],
        "serial": ["serial", "serial number", "sn"],
    },
    "fields": {
        "version": {
            "synonyms": ["version", "firmware", "software version", "os version", "image", "sw version"],
            "mist_fields": ["version", "sw_version", "image"],
        },
        "model": {
            "synonyms": ["model", "platform", "hw model"],
            "mist_fields": ["model"],
        },
        "site_id": {
            "synonyms": ["site id", "site uuid"],
            "mist_fields": ["site_id"],
        },
        "org_id": {
            "synonyms": ["org id", "organization id", "tenant id"],
            "mist_fields": ["org_id"],
        },
        "ap_name": {
            "synonyms": ["ap", "ap name", "access point", "radio name"],
            "mist_fields": ["ap_name", "ap"],
        },
        "switch": {
            "synonyms": ["switch", "switch name"],
            "mist_fields": ["switch"],
        },
        "port": {
            "synonyms": ["port", "switchport", "interface"],
            "mist_fields": ["port", "ifname"],
        },
        "ssid": {
            "synonyms": ["ssid", "wifi name", "wireless network"],
            "mist_fields": ["ssid"],
        },
        "band": {
            "synonyms": ["band", "2.4ghz", "5ghz", "6ghz"],
            "mist_fields": ["band"],
        },
        "rssi": {
            "synonyms": ["rssi", "signal", "signal strength"],
            "mist_fields": ["rssi"],
        },
        "snr": {
            "synonyms": ["snr", "signal-to-noise", "noise ratio"],
            "mist_fields": ["snr"],
        },
        "last_seen": {
            "synonyms": ["last seen", "seen", "last active"],
            "mist_fields": ["last_seen"],
        },
        "cpu": {
            "synonyms": ["cpu", "cpu util", "cpu usage"],
            "mist_fields": ["cpu"],
        },
        "mem": {
            "synonyms": ["memory", "mem", "ram usage"],
            "mist_fields": ["mem"],
        },
        "uptime": {
            "synonyms": ["uptime", "time since reboot"],
            "mist_fields": ["uptime"],
        },
        "loss": {
            "synonyms": ["packet loss", "loss"],
            "mist_fields": ["loss"],
        },
        "latency": {
            "synonyms": ["latency", "rtt", "delay"],
            "mist_fields": ["latency"],
        },
        "jitter": {
            "synonyms": ["jitter", "latency variance"],
            "mist_fields": ["jitter"],
        },
        "retries": {
            "synonyms": ["retries", "retry rate"],
            "mist_fields": ["retries"],
        },
        "coverage": {
            "synonyms": ["coverage", "coverage score"],
            "mist_fields": ["coverage"],
        },
        "auth": {
            "synonyms": ["auth", "authentication", "802.1x auth"],
            "mist_fields": ["auth"],
        },
        "dhcp": {
            "synonyms": ["dhcp", "dhcp success", "dhcp failures"],
            "mist_fields": ["dhcp"],
        },
        "dns": {
            "synonyms": ["dns", "dns failures", "dns success"],
            "mist_fields": ["dns"],
        },
        "ttc": {
            "synonyms": ["time to connect", "ttc"],
            "mist_fields": ["ttc"],
        },
        "score": {
            "synonyms": ["score", "site score", "performance score", "overall score"],
            "mist_fields": ["score", "site_score"],
        },
    },
    "actions": {
        "observe": ["show", "list", "get", "find", "where is", "count", "top"],
        "audit": ["audit", "check", "validate", "verify", "diff"],
        "plan": ["plan", "propose", "dry run", "preview"],
        "mutate": ["set", "configure", "rename", "assign", "apply", "update", "reboot", "upgrade"],
    },
    "questions_to_patterns": {
        "whereis": ["where is", "is <id> wifi or wired", "find client", "locate device"],
        "get_device_field": ["what version is <device>", "what firmware", "what model"],
        "site_score": ["site score", "performance score", "overall performance"],
        "top_metric": ["highest cpu", "top retries", "worst clients"],
        "inventory_counts": ["how many sites", "how many switches", "subscriptions vs switches"],
    },
    "endpoint_hints": {
        "sites": ["/orgs/{org_id}/sites"],
        "devices_at_site": ["/sites/{site_id}/devices"],
        "client_stats": ["/sites/{site_id}/stats/clients"],
        "device_stats": ["/sites/{site_id}/stats/devices"],
        "licenses": ["/orgs/{org_id}/licenses"],
        "site_score": ["/sites/{site_id}/insights/score"],
    },
    "time_windows": {
        "last_15m": ["last 15 minutes", "15m"],
        "last_hour": ["last hour", "1h"],
        "last_24h": ["last day", "24h"],
        "workday": ["business hours", "workday"],
    },
    "status_terms": {
        "wifi": ["wifi", "wireless"],
        "wired": ["wired", "ethernet"],
        "active": ["active", "online", "up"],
        "inactive": ["inactive", "offline", "down", "not seen"],
    },
    "units": {
        "rssi": "dBm",
        "snr": "dB",
        "latency": "ms",
        "jitter": "ms",
        "loss": "percent",
        "cpu": "percent",
        "mem": "percent",
        "uptime": "seconds",
        "score": "0-100",
    },
    "best_practices": [
        "Resolve site names to UUIDs before device/client queries; avoid org-wide scans when a site is known.",
        "Prefer stats endpoints for live state (clients/devices) and devices endpoint for inventory attributes (model, version).",
        "For 'version', try 'version' first, then 'sw_version', then 'image'.",
        "Infer wifi vs wired: presence of ap/ap_name/band implies Wi-Fi; presence of switch with no AP implies wired.",
        "Use a short time window (e.g., 1–2h) for client lookups to avoid stale DHCP reuse.",
        "Always paginate when lists may exceed defaults; prefer server-side aggregation to reduce tokens.",
        "Keep answers compact: return a tiny table with key fields plus 2–3 bullet insights.",
        "Treat writes as unsafe by default; require explicit confirmation and provide a dry-run preview first.",
    ],
}
