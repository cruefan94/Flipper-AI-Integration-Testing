"""Offline boundary regressions for the Pi browser memory advisor.

No Pi device, process, network, or hardware access.
Run: python3 -m unittest discover -s pi_lab -p 'test_browser_advisor_boundaries.py' -v
"""
import unittest
from browser_memory_advisor import advise_browser


class BrowserAdvisorBoundaryTests(unittest.TestCase):
    def test_exact_critical_absolute_boundary(self):
        self.assertEqual(advise_browser(4096, 256, 1).level, "CRITICAL")

    def test_just_below_critical_absolute_boundary(self):
        self.assertEqual(advise_browser(4096, 255, 1).level, "CRITICAL")

    def test_exact_low_absolute_boundary(self):
        self.assertEqual(advise_browser(4096, 512, 1).level, "LOW")

    def test_just_below_low_absolute_boundary(self):
        self.assertEqual(advise_browser(4096, 511, 1).level, "LOW")

    def test_just_above_low_ratio_boundary(self):
        self.assertEqual(advise_browser(4096, 700, 1).level, "OK")

    def test_tabs_boundary(self):
        self.assertEqual(advise_browser(4096, 2000, 11).level, "OK")
        self.assertEqual(advise_browser(4096, 2000, 12).level, "TABS")

    def test_infinite_inputs_rejected(self):
        self.assertEqual(advise_browser(float("inf"), 100, 2).level, "INVALID")
        self.assertEqual(advise_browser(4096, float("-inf"), 2).level, "INVALID")

    def test_huge_tab_count_rejected(self):
        self.assertEqual(advise_browser(4096, 2000, 10001).level, "INVALID")

    def test_no_actions_in_suggestions(self):
        for available in (100, 400, 1000, 3000):
            advice = advise_browser(4096, available, 20)
            self.assertNotIn("sudo", advice.suggestion.lower())
            self.assertNotIn("kill", advice.suggestion.lower())


if __name__ == "__main__":
    unittest.main()
