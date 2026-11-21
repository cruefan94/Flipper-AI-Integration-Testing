"""Read-only, privacy-preserving qFlipper USB inventory for Raspberry Pi OS.

Does not open serial ports, read log contents, invoke qFlipper or require root.
Only reports USB tty device names and whether qFlipper configuration/log paths exist.
"""
from __future__ import annotations
import json
from pathlib import Path


def snapshot(sys_tty: Path = Path("/sys/class/tty"),
             home: Path | None = None) -> dict:
    home = home or Path.home()
    ports = []
    if sys_tty.is_dir():
        for item in sorted(sys_tty.iterdir(), key=lambda p: p.name):
            if not item.name.startswith(("ttyACM", "ttyUSB")):
                continue
            # A sysfs device link indicates a physical/virtual USB serial device.
            if (item / "device").exists():
                ports.append(item.name)
    config = home / ".config" / "Flipper Devices Inc" / "qFlipper.ini"
    logs = home / ".local" / "share" / "qFlipper"
    return {
        "schema_version": 1,
        "usb_serial_port_names": ports,
        "qflipper_config_present": config.is_file(),
        "qflipper_log_directory_present": logs.is_dir(),
        "qflipper_log_file_count": sum(
            1 for p in logs.iterdir()
            if p.is_file() and p.name.startswith("qFlipper-") and p.suffix == ".txt"
        ) if logs.is_dir() else 0,
        "device_connection_verified": False,
        "backup_verified": False,
        "firmware_status": "not_checked",
    }


if __name__ == "__main__":
    print(json.dumps(snapshot(), indent=2, sort_keys=True))
