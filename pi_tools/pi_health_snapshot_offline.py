"""Offline Raspberry Pi health snapshot parser; no shell, hardware, or service access.

Consumes caller-supplied /proc/meminfo and /proc/loadavg text. It never reads
those files itself. The 10-second polling UI is a separate, opt-in milestone.
"""
from dataclasses import dataclass
import re
import unittest

MAX_CHARS = 32768
MEM_LINE = re.compile(r"^(MemTotal|MemAvailable):\s+(\d+)\s+kB\s*$")
LOAD_LINE = re.compile(r"^(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+\d+/\d+\s+\d+\s*$")


@dataclass(frozen=True)
class PiHealth:
    total_mib: int
    available_mib: int
    used_percent: int
    load_1m: float
    load_5m: float
    load_15m: float
    status: str


def summarize_health(meminfo: object, loadavg: object) -> PiHealth:
    """Fail closed on missing, duplicated, inconsistent or oversized data."""
    if type(meminfo) is not str or type(loadavg) is not str:
        raise ValueError("invalid snapshot")
    if len(meminfo) > MAX_CHARS or len(loadavg) > MAX_CHARS:
        raise ValueError("oversized snapshot")
    values = {}
    for line in meminfo.splitlines():
        match = MEM_LINE.fullmatch(line)
        if match:
            key, amount = match.groups()
            if key in values:
                raise ValueError("duplicate memory field")
            values[key] = int(amount)
    if set(values) != {"MemTotal", "MemAvailable"}:
        raise ValueError("missing memory field")
    total, available = values["MemTotal"], values["MemAvailable"]
    if total <= 0 or available > total:
        raise ValueError("inconsistent memory snapshot")
    match = LOAD_LINE.fullmatch(loadavg.strip())
    if not match:
        raise ValueError("invalid load snapshot")
    loads = tuple(float(v) for v in match.groups())
    if any(not (0 <= value < 1000000) for value in loads):
        raise ValueError("invalid load value")
    used_percent = round(100 * (total - available) / total)
    status = "LOW_AVAILABLE_MEMORY" if available * 10 < total else "OBSERVED_NOT_DIAGNOSED"
    return PiHealth(total // 1024, available // 1024, used_percent, *loads, status)


class PiHealthTests(unittest.TestCase):
    MEM = "MemTotal:  4000000 kB\nMemAvailable:  2000000 kB\n"
    LOAD = "0.25 0.50 0.75 1/100 1234"

    def test_normal(self):
        result = summarize_health(self.MEM, self.LOAD)
        self.assertEqual(result.used_percent, 50)
        self.assertEqual(result.status, "OBSERVED_NOT_DIAGNOSED")

    def test_low_available(self):
        result = summarize_health("MemTotal: 4000000 kB\nMemAvailable: 100000 kB", self.LOAD)
        self.assertEqual(result.status, "LOW_AVAILABLE_MEMORY")

    def test_no_private_process_data_in_result(self):
        self.assertNotIn("1234", repr(summarize_health(self.MEM, self.LOAD)))

    def test_missing_field(self):
        with self.assertRaises(ValueError):
            summarize_health("MemTotal: 4000000 kB", self.LOAD)

    def test_duplicate_field(self):
        with self.assertRaises(ValueError):
            summarize_health(self.MEM + "MemTotal: 4000000 kB", self.LOAD)

    def test_impossible_memory(self):
        with self.assertRaises(ValueError):
            summarize_health("MemTotal: 100 kB\nMemAvailable: 101 kB", self.LOAD)

    def test_invalid_load(self):
        with self.assertRaises(ValueError):
            summarize_health(self.MEM, "broken")

    def test_no_io(self):
        import inspect
        source = inspect.getsource(summarize_health)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("open(", source)


if __name__ == "__main__":
    unittest.main()
