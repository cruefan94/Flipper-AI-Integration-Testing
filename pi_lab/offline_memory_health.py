"""Offline Raspberry Pi memory-pressure assessment from owner-supplied /proc/meminfo.

Pure parser: never reads a Pi file, runs a command, or changes system settings.
Only MemTotal and MemAvailable are accepted into the returned report.
"""
from dataclasses import dataclass
import re

_MAX_INPUT = 16384
_LINE = re.compile(r"^(MemTotal|MemAvailable):[ \t]*([0-9]+)[ \t]+kB[ \t]*$")


@dataclass(frozen=True)
class MemoryHealth:
    total_kib: int
    available_kib: int
    available_percent: int
    pressure: str


def assess_meminfo(text: str) -> MemoryHealth:
    """Return conservative pressure classification; fail closed on invalid evidence."""
    if not isinstance(text, str) or len(text) > _MAX_INPUT:
        raise ValueError("invalid meminfo input")
    values = {}
    for line in text.splitlines():
        if line.startswith(("MemTotal:", "MemAvailable:")):
            match = _LINE.fullmatch(line)
            if match is None or match.group(1) in values:
                raise ValueError("invalid or duplicate memory field")
            values[match.group(1)] = int(match.group(2))
    if set(values) != {"MemTotal", "MemAvailable"}:
        raise ValueError("missing required memory field")
    total, available = values["MemTotal"], values["MemAvailable"]
    if not (0 < total <= 1_073_741_824 and 0 <= available <= total):
        raise ValueError("impossible memory amounts")
    percent = available * 100 // total
    pressure = "HIGH" if percent < 10 else "MODERATE" if percent < 25 else "LOW"
    return MemoryHealth(total, available, percent, pressure)
