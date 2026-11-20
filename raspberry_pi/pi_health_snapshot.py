"""Offline parser for owner-supplied Raspberry Pi OS health snapshots.

No filesystem, subprocess, GPIO, service, USB, network or hardware access.
Caller obtains /proc/meminfo and /proc/uptime separately, with consent.
"""
from __future__ import annotations

import re
from typing import Any

_MEM_RE = re.compile(r"^(MemTotal|MemAvailable):\s*([0-9]+)\s+kB\s*$")


def parse_pi_health(meminfo_text: str, uptime_text: str) -> dict[str, Any]:
    """Fail closed on missing/invalid inputs; never infer device health."""
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "unknown",
        "memory_total_kib": None,
        "memory_available_kib": None,
        "memory_used_percent": None,
        "uptime_seconds": None,
        "hardware_verified": False,
        "cooling_control_authorized": False,
    }
    if not isinstance(meminfo_text, str) or not isinstance(uptime_text, str):
        return result
    values: dict[str, int] = {}
    for line in meminfo_text.splitlines():
        match = _MEM_RE.fullmatch(line.strip())
        if match:
            key, raw = match.groups()
            if key in values:
                return result
            values[key] = int(raw)
    total, available = values.get("MemTotal"), values.get("MemAvailable")
    try:
        parts = uptime_text.strip().split()
        if len(parts) != 2:
            return result
        uptime = float(parts[0])
        idle = float(parts[1])
    except ValueError:
        return result
    from math import isfinite
    if (total is None or available is None or total <= 0 or
        available < 0 or available > total or
        not isfinite(uptime) or not isfinite(idle) or
        uptime < 0 or idle < 0):
        return result
    result.update(
        status="parsed_unverified",
        memory_total_kib=total,
        memory_available_kib=available,
        memory_used_percent=round(100 * (total - available) / total, 1),
        uptime_seconds=uptime,
    )
    return result
