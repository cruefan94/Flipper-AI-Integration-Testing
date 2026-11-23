"""Offline, read-only Pironman service evidence normalization.

Consumes owner-supplied snapshots only. No subprocess, hardware, network, or writes.
This is evidence for UI planning, never permission to change fan/OLED/RGB settings.
"""
from dataclasses import dataclass
import re

_ALLOWED = {"active", "inactive", "failed", "unknown"}
_NAME = re.compile(r"^[a-zA-Z0-9_.@-]{1,100}\\.service$")
_MAX_LINES = 128
_MAX_BYTES = 16384


@dataclass(frozen=True)
class ServiceEvidence:
    unit: str
    state: str
    confirmed: bool = False
    hardware_write_authorized: bool = False


def parse_service_snapshot(snapshot: str) -> tuple[ServiceEvidence, ...]:
    """Parse explicit 'UNIT STATE' lines, rejecting ambiguous/unsafe input.

    Output confirmed=False because owner-supplied text is not device attestation.
    """
    if not isinstance(snapshot, str) or len(snapshot.encode("utf-8")) > _MAX_BYTES:
        raise ValueError("invalid snapshot size/type")
    lines = snapshot.splitlines()
    if len(lines) > _MAX_LINES:
        raise ValueError("too many service lines")
    output = []
    seen = set()
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError("expected UNIT STATE")
        unit, state = parts
        if not _NAME.fullmatch(unit) or state not in _ALLOWED:
            raise ValueError("invalid unit/state")
        if unit in seen:
            raise ValueError("duplicate unit")
        seen.add(unit)
        output.append(ServiceEvidence(unit, state))
    return tuple(output)
