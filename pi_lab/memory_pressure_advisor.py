"""Offline, read-only Raspberry Pi memory pressure classifier.

Accepts /proc/meminfo text supplied by a caller; never reads hardware,
executes commands, changes services, or prints source contents.
"""
import re
import unittest

_ALLOWED = ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree")
_PATTERN = re.compile(r"^(MemTotal|MemAvailable|SwapTotal|SwapFree):[ \t]+([0-9]+)[ \t]+kB[ \t]*$")


def classify_meminfo(text):
    """Return only a fixed label; reject malformed or partial readings."""
    if not isinstance(text, str) or len(text) > 65536:
        return "INVALID"
    found = {}
    for line in text.splitlines():
        if any(line.startswith(key + ":") for key in _ALLOWED):
            match = _PATTERN.fullmatch(line)
            if not match or match.group(1) in found:
                return "INVALID"
            found[match.group(1)] = int(match.group(2))
    if "MemTotal" not in found or "MemAvailable" not in found:
        return "INVALID"
    total, available = found["MemTotal"], found["MemAvailable"]
    if total <= 0 or available > total:
        return "INVALID"
    if ("SwapTotal" in found) != ("SwapFree" in found):
        return "INVALID"
    if "SwapTotal" in found and found["SwapFree"] > found["SwapTotal"]:
        return "INVALID"
    percent = 100 * available / total
    if percent < 10:
        return "CRITICAL"
    if percent < 20:
        return "LOW"
    return "OK"


class MemoryPressureTests(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(classify_meminfo("MemTotal: 4000 kB\nMemAvailable: 2000 kB"), "OK")

    def test_low(self):
        self.assertEqual(classify_meminfo("MemTotal: 4000 kB\nMemAvailable: 600 kB"), "LOW")

    def test_critical(self):
        self.assertEqual(classify_meminfo("MemTotal: 4000 kB\nMemAvailable: 100 kB"), "CRITICAL")

    def test_missing(self):
        self.assertEqual(classify_meminfo("MemTotal: 4000 kB"), "INVALID")

    def test_duplicate(self):
        self.assertEqual(classify_meminfo("MemTotal: 4000 kB\nMemTotal: 3000 kB\nMemAvailable: 100 kB"), "INVALID")

    def test_bad_value(self):
        self.assertEqual(classify_meminfo("MemTotal: -1 kB\nMemAvailable: 1 kB"), "INVALID")

    def test_impossible(self):
        self.assertEqual(classify_meminfo("MemTotal: 100 kB\nMemAvailable: 200 kB"), "INVALID")

    def test_swap_pair(self):
        self.assertEqual(classify_meminfo("MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 100 kB"), "INVALID")

    def test_swap_bounds(self):
        self.assertEqual(classify_meminfo("MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: 10 kB\nSwapFree: 11 kB"), "INVALID")

    def test_oversize(self):
        self.assertEqual(classify_meminfo("x" * 65537), "INVALID")


if __name__ == "__main__":
    unittest.main()
