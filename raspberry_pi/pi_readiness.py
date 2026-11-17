#!/usr/bin/env python3
"""Read-only Flipper AI Pi 4B readiness summary; never opens USB devices.

Device names and USB VID/PID are hints only. No output asserts that an
attached controller is a verified Flipper, ESP32 or flashable firmware target.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil

try:
    from raspberry_pi.pi_usb_inventory import inventory
except ModuleNotFoundError:
    # Supports both "python -m raspberry_pi.pi_readiness" from the repo root
    # and "python raspberry_pi/pi_readiness.py" on the owner's desktop.
    from pi_usb_inventory import inventory


def readiness(sys_tty: Path = Path("/sys/class/tty"), which=shutil.which) -> dict:
    ports = inventory(sys_tty)
    return {
        "schema": 1,
        "read_only": True,
        "qflipper_installed": bool(which("qFlipper") or which("qflipper")),
        "usb_serial_ports": [
            {
                "port": row["port"],
                "vid": row["vid"],
                "pid": row["pid"],
                "manufacturer": row["manufacturer"],
                "product": row["product"],
                "device_identity_confirmed": False,
            }
            for row in ports
        ],
        "verified_flipper_link": False,
        "verified_esp32_link": False,
        "notes": [
            "USB metadata alone cannot confirm a Flipper or ESP32 identity.",
            "Confirm Flipper discovery in qFlipper on the Pi before an approved firmware update.",
            "Do not confuse ESP32 UART or USB images with Flipper Zero F7 updater files.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(readiness(), indent=2))
