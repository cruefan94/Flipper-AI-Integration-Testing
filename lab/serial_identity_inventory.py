"""Offline-only USB serial inventory reconciliation.

No device access, serial opens, flashing, or hardware identity assertions.
All inputs are synthetic records from an external, separately authorized scan.
"""
from collections import defaultdict
from pathlib import PurePosixPath


def reconcile_serial_inventory(records):
    """Group aliases by resolved canonical path; never infer chip family.

    records: iterable of {'path': '/dev/...', 'target': '/dev/...'}.
    Caller must supply already-resolved targets; this function never touches /dev.
    """
    groups = defaultdict(set)
    errors = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append({"index": index, "reason": "invalid_record"})
            continue
        path, target = record.get("path"), record.get("target")
        if not isinstance(path, str) or not isinstance(target, str):
            errors.append({"index": index, "reason": "invalid_path"})
            continue
        def allowed(value):
            if not value.startswith("/dev/") or ".." in PurePosixPath(value).parts:
                return False
            name = PurePosixPath(value).name
            return (name.startswith("ttyUSB") and name[6:].isdigit()) or (
                name.startswith("ttyACM") and name[6:].isdigit()) or (
                value.startswith("/dev/serial/by-id/") and len(name) > 0)
        if not allowed(path) or not allowed(target) or target.startswith("/dev/serial/by-id/"):
            errors.append({"index": index, "reason": "untrusted_device_path"})
            continue
        groups[target].add(path)
    return {
        "devices": [{"canonical": key, "aliases": sorted(value), "chip": "unverified",
                     "flash_authorized": False}
                    for key, value in sorted(groups.items())],
        "errors": errors,
    }
