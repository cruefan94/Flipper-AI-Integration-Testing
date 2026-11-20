"""Opt-in, read-only Raspberry Pi OS /proc collector.

No service, fan, OLED, GPIO, USB, network, or firmware operations.
No background scheduling; callers explicitly request each sample.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Any

from raspberry_pi.pi_health_snapshot import parse_pi_health

MEMINFO = Path("/proc/meminfo")
UPTIME = Path("/proc/uptime")


def collect_pi_health(
    *,
    consent: bool = False,
    reader: Callable[[Path], str] | None = None,
) -> dict[str, Any]:
    """Read only two fixed kernel status files, and only with explicit consent.

    A supplied reader supports synthetic offline tests without touching host /proc.
    All failures return unknown; timestamps or connected-device claims are omitted.
    """
    unknown = parse_pi_health("", "")
    unknown["collection_status"] = "not_authorized" if not consent else "unavailable"
    if not consent:
        return unknown
    if reader is None:
        def reader(path: Path) -> str:
            return path.read_text(encoding="ascii")
    try:
        meminfo = reader(MEMINFO)
        uptime = reader(UPTIME)
        if not isinstance(meminfo, str) or not isinstance(uptime, str):
            return unknown
        if len(meminfo) > 65536 or len(uptime) > 1024:
            return unknown
        result = parse_pi_health(meminfo, uptime)
        result["collection_status"] = (
            "read_only_sample_unverified"
            if result["status"] == "parsed_unverified" else "unavailable"
        )
        return result
    except (OSError, UnicodeError, ValueError, TypeError):
        return unknown
