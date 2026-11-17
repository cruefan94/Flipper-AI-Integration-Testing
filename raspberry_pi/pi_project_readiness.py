#!/usr/bin/env python3
"""Safe Pi 4B readiness snapshot for the Flipper/ESP32/Arduino project.

No serial device is opened, no firmware flashed, no services restarted.
"""
from __future__ import annotations
import json
from pathlib import Path
import shutil

try:
    from .pi_usb_inventory import inventory
    from .pi_health_monitor import snapshot
except ImportError:
    from pi_usb_inventory import inventory
    from pi_health_monitor import snapshot


def readiness(
    tty_root: Path = Path("/sys/class/tty"),
    pi_root: Path = Path("/"),
    find_executable=shutil.which,
) -> dict:
    ports = inventory(tty_root)
    qflipper = bool(find_executable("qFlipper") or find_executable("qflipper"))
    return {
        "read_only": True,
        "qflipper_installed": qflipper,
        "serial_ports": ports,
        "serial_port_count": len(ports),
        "pi_health": snapshot(pi_root),
        "flipper_detected_by_ai_protocol": False,
        "esp32_identity_verified": False,
        "arduino_identity_verified": False,
        "next_steps": [
            "Confirm USB device identity locally using qFlipper and board labels.",
            "Do not flash or connect 5V Arduino GPIO to 3.3V Flipper/ESP32 pins.",
            "Keep firmware backups and validate exact images before flashing.",
        ],
        "disclaimer": "USB VID/PID and port presence do not prove Flipper AI, ESP32, or Arduino interoperability.",
    }


if __name__ == "__main__":
    print(json.dumps(readiness(), indent=2, sort_keys=True))
