"""Pure offline parser for pasted /proc/meminfo text. No file or device access.

Never persist or print input text; callers may provide sanitized excerpts.
Returns only memory quantities and a fixed browser-advice label.
"""
from dataclasses import dataclass
import re
import unittest

from browser_memory_advisor import advise_browser

_LINE = re.compile(r"^(MemTotal|MemAvailable):[ \t]*([0-9]+)[ \t]+kB[ \t]*$")
_MAX_KIB = 1 << 44


@dataclass(frozen=True)
class MemorySnapshot:
    total_mib: float
    available_mib: float
    advice: str


def parse_meminfo(text: object, tabs: object) -> MemorySnapshot | None:
    """Fail closed on malformed, duplicate, missing, or implausible fields."""
    if type(text) is not str or len(text) > 65536:
        return None
    found = {}
    for line in text.splitlines():
        if line.startswith(("MemTotal:", "MemAvailable:")):
            match = _LINE.fullmatch(line)
            if not match or match[1] in found:
                return None
            value = int(match[2])
            if value > _MAX_KIB:
                return None
            found[match[1]] = value
    if set(found) != {"MemTotal", "MemAvailable"}:
        return None
    total = found["MemTotal"]
    available = found["MemAvailable"]
    if not total or available > total:
        return None
    total_mib, available_mib = total / 1024, available / 1024
    advice = advise_browser(total_mib, available_mib, tabs)
    if advice.level == "INVALID":
        return None
    return MemorySnapshot(total_mib, available_mib, advice.level)


class MeminfoParserTests(unittest.TestCase):
    GOOD = "MemTotal:       3999999 kB\nMemFree: 100 kB\nMemAvailable: 2048000 kB\n"

    def test_good(self):
        self.assertEqual(parse_meminfo(self.GOOD, 3).advice, "OK")

    def test_critical(self):
        self.assertEqual(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 100000 kB", 2).advice, "CRITICAL")

    def test_tabs(self):
        self.assertEqual(parse_meminfo(self.GOOD, 12).advice, "TABS")

    def test_duplicate(self):
        self.assertIsNone(parse_meminfo(self.GOOD + "MemTotal: 1 kB\n", 2))

    def test_missing(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4000 kB", 2))

    def test_units(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4000 MB\nMemAvailable: 2000 kB", 2))

    def test_negative(self):
        self.assertIsNone(parse_meminfo("MemTotal: -1 kB\nMemAvailable: 0 kB", 2))

    def test_available_over_total(self):
        self.assertIsNone(parse_meminfo("MemTotal: 1 kB\nMemAvailable: 2 kB", 2))

    def test_bad_tabs(self):
        self.assertIsNone(parse_meminfo(self.GOOD, True))

    def test_not_text(self):
        self.assertIsNone(parse_meminfo(None, 2))

    def test_no_sensitive_output(self):
        data = self.GOOD + "SecretKey: do-not-repeat\n"
        self.assertNotIn("do-not-repeat", repr(parse_meminfo(data, 2)))


if __name__ == "__main__":
    unittest.main()
