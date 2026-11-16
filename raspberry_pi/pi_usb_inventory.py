"""Read-only Linux USB serial inventory for Pi qFlipper diagnostics.

Never opens /dev/tty*, changes permissions, or accesses device serial numbers.
USB VID/PID and labels are hints, not verified board identity.
"""
from __future__ import annotations
import json
from pathlib import Path


def _safe_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace").strip()[:96]
    except (OSError, UnicodeError):
        return None


def inventory(sys_tty: Path = Path("/sys/class/tty")) -> list[dict[str, str | None]]:
    """Inspect ttyACM/ttyUSB sysfs links; no device nodes are opened."""
    devices = []
    try:
        entries = sorted(sys_tty.iterdir(), key=lambda p: p.name)
    except OSError:
        return devices
    for entry in entries:
        if not (entry.name.startswith("ttyACM") or entry.name.startswith("ttyUSB")):
            continue
        if not entry.name[6:].isdigit():
            continue
        try:
            current = (entry / "device").resolve(strict=True)
        except (OSError, RuntimeError):
            continue
        info = None
        for parent in (current, *current.parents):
            vid = _safe_text(parent / "idVendor")
            pid = _safe_text(parent / "idProduct")
            if vid and pid:
                info = {"port": "/dev/" + entry.name, "vid": vid,
                        "pid": pid, "manufacturer": _safe_text(parent / "manufacturer"),
                        "product": _safe_text(parent / "product")}
                break
        if info:
            devices.append(info)
        else:
            devices.append({"port": "/dev/" + entry.name, "vid": None,
                            "pid": None, "manufacturer": None, "product": None})
    return devices


if __name__ == "__main__":
    print(json.dumps({"usb_serial_ports": inventory(), "read_only": True}, indent=2))
