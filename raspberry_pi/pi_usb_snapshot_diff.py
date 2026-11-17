"""Pure, read-only USB inventory change reporting for Pi workstation diagnostics.

A port change is not proof of device identity or a safe firmware target.
No serial ports are opened and no private USB serial numbers are collected.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping


FIELDS = ("vid", "pid", "manufacturer", "product")


def _normalized(items: Iterable[Mapping[str, str | None]]) -> dict[str, dict[str, str | None]]:
    ports: dict[str, dict[str, str | None]] = {}
    for item in items:
        port = item.get("port")
        if not isinstance(port, str) or not (
            port.startswith("/dev/ttyACM") and port[11:].isdigit()
            or port.startswith("/dev/ttyUSB") and port[11:].isdigit()
        ):
            continue
        ports[port] = {key: item.get(key) if isinstance(item.get(key), str) else None
                       for key in FIELDS}
    return ports


def compare_snapshots(before: Iterable[Mapping[str, str | None]],
                      after: Iterable[Mapping[str, str | None]]) -> dict:
    """Compare snapshots without device I/O; report re-enumeration as unverified."""
    old, new = _normalized(before), _normalized(after)
    return {
        "connected": sorted(set(new) - set(old)),
        "disconnected": sorted(set(old) - set(new)),
        "metadata_changed": sorted(port for port in old.keys() & new.keys()
                                   if old[port] != new[port]),
        "identity_verified": False,
        "read_only": True,
    }
