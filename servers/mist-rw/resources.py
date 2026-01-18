from __future__ import annotations

from typing import Dict


def allowlist() -> Dict[str, str]:
    return {
        "PUT /devices/{device_id}/switch_ports/{port_id}/local_config": "Update switch port usage",
        "POST /devices/{device_id}/bounce_port": "Bounce device ports",
        "POST /orgs/{org_id}/sites/create": "Create site",
        "POST /alarms/ack/all": "Acknowledge all alarms",
        "POST /alarms/ack": "Acknowledge specific alarms",
        "POST /alarms/{alarm_id}/ack": "Acknowledge single alarm",
        "POST /devices/{device_id}/ping": "Run switch cable test",
    }
