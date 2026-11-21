"""Consent-gated, read-only USB VID/PID inventory for Raspberry Pi Linux.

Never reads serial numbers, USB descriptors, logs, or device nodes.
A VID/PID match does NOT establish that a Flipper is connected.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def inventory(*, consent: bool = False, root: Path = Path("/sys/bus/usb/devices")) -> dict:
    if type(consent) is not bool:
        raise ValueError("consent must be boolean")
    if not consent:
        return {"status": "not_authorized", "devices": [], "device_identity": "unknown"}
    devices = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: p.name)
    except OSError:
        return {"status": "sysfs_unavailable", "devices": [], "device_identity": "unknown"}
    for entry in entries:
        try:
            # Read only the two public USB identifier fields, never serial/manufacturer.
            vid = (entry / "idVendor").read_text(encoding="ascii").strip().lower()
            pid = (entry / "idProduct").read_text(encoding="ascii").strip().lower()
            if len(vid) != 4 or len(pid) != 4:
                continue
            int(vid, 16)
            int(pid, 16)
        except (OSError, ValueError, UnicodeError):
            continue
        devices.append({"vendor_id": vid, "product_id": pid})
    return {"status": "read_only_inventory", "devices": devices,
            "device_identity": "unverified", "usb_access": "not_tested",
            "backup": "not_tested", "recovery": "not_tested"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only USB VID/PID inventory; no device access")
    parser.add_argument("--consent", action="store_true", help="allow sysfs VID/PID lookup")
    args = parser.parse_args()
    print(json.dumps(inventory(consent=args.consent), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
