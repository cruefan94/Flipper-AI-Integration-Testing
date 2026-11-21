"""Pure, read-only qFlipper recovery preflight. Never interprets port presence as a backup."""
from __future__ import annotations

from typing import Mapping, Any


def recovery_preflight(inventory: Mapping[str, Any]) -> dict:
    """Return conservative, non-actionable recovery readiness signals.

    No filesystem, serial, firmware, process or network access is performed.
    User-verified backups and recovery steps are intentionally never inferred.
    """
    ports = inventory.get("usb_serial_port_names", [])
    if not isinstance(ports, list):
        ports = []
    ports = [p for p in ports if isinstance(p, str) and p.startswith(("ttyACM", "ttyUSB"))]
    return {
        "schema_version": 1,
        "usb_serial_candidates": len(ports),
        "qflipper_config_detected": inventory.get("qflipper_config_present") is True,
        "qflipper_logs_detected": inventory.get("qflipper_log_directory_present") is True,
        "connection_tested": False,
        "backup_verified": False,
        "recovery_tested": False,
        "safe_to_flash": False,
        "next_step": "Manually verify device connection, backup integrity and recovery on the owner's Pi; no flashing.",
    }
