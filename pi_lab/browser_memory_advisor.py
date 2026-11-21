"""Offline, read-only Raspberry Pi browser memory advice. No process or hardware access.

Usage: python3 -m unittest discover -s pi_lab -p 'browser_memory_advisor.py'
The API accepts caller-supplied numbers only; it does not inspect the Pi.
"""
from dataclasses import dataclass
import math
import unittest


@dataclass(frozen=True)
class BrowserAdvice:
    level: str
    suggestion: str


def advise_browser(total_mib: object, available_mib: object, open_tabs: object) -> BrowserAdvice:
    """Return fixed safe advice, never shell commands or destructive actions."""
    if (type(total_mib) not in (int, float)
            or type(available_mib) not in (int, float)
            or type(open_tabs) is not int):
        return BrowserAdvice("INVALID", "Check the supplied memory and tab readings.")
    if (not math.isfinite(total_mib) or not math.isfinite(available_mib)
            or total_mib <= 0 or available_mib < 0
            or available_mib > total_mib or open_tabs < 0 or open_tabs > 10000):
        return BrowserAdvice("INVALID", "Check the supplied memory and tab readings.")
    ratio = available_mib / total_mib
    if available_mib < 256 or ratio < 0.08:
        return BrowserAdvice("CRITICAL", "Save browser work; consider manually closing unused tabs.")
    if available_mib < 512 or ratio < 0.16:
        return BrowserAdvice("LOW", "Consider manually closing unused browser tabs.")
    if open_tabs >= 12:
        return BrowserAdvice("TABS", "Consider bookmarking and manually closing unused tabs.")
    return BrowserAdvice("OK", "No browser changes recommended.")


class BrowserAdvisorTests(unittest.TestCase):
    def test_ok(self): self.assertEqual(advise_browser(4096, 2500, 4).level, "OK")
    def test_low_absolute(self): self.assertEqual(advise_browser(4096, 400, 4).level, "LOW")
    def test_low_ratio(self): self.assertEqual(advise_browser(4096, 600, 4).level, "LOW")
    def test_critical_absolute(self): self.assertEqual(advise_browser(4096, 200, 4).level, "CRITICAL")
    def test_critical_ratio(self): self.assertEqual(advise_browser(4096, 300, 4).level, "CRITICAL")
    def test_many_tabs(self): self.assertEqual(advise_browser(4096, 2000, 12).level, "TABS")
    def test_negative(self): self.assertEqual(advise_browser(4096, -1, 3).level, "INVALID")
    def test_over_total(self): self.assertEqual(advise_browser(4096, 5000, 3).level, "INVALID")
    def test_nan(self): self.assertEqual(advise_browser(float("nan"), 100, 3).level, "INVALID")
    def test_boolean(self): self.assertEqual(advise_browser(True, 1, 1).level, "INVALID")
    def test_fractional_tabs(self): self.assertEqual(advise_browser(4096, 1000, 1.5).level, "INVALID")
    def test_no_execution(self):
        self.assertNotIn("sudo", advise_browser(4096, 200, 20).suggestion)


if __name__ == "__main__":
    unittest.main()
