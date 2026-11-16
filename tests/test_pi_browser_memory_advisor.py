"""Synthetic, hardware-free browser memory advice regression tests."""
import unittest

from raspberry_pi.pi_browser_memory_advisor import browser_budget


class BrowserBudgetTests(unittest.TestCase):
    def test_missing_and_inconsistent_data_fail_closed(self):
        for mem in ({}, {"MemTotal": 0, "MemAvailable": 0},
                    {"MemTotal": 100, "MemAvailable": 101},
                    {"MemTotal": 100, "MemAvailable": -1}):
            self.assertEqual(browser_budget(mem)["status"], "unavailable")

    def test_critical_is_advice_only(self):
        result = browser_budget({"MemTotal": 4096000, "MemAvailable": 300000})
        self.assertEqual(result["status"], "critical")
        self.assertTrue(result["read_only"])
        self.assertIn("close unused tabs", result["recommendations"][0])

    def test_thresholds(self):
        self.assertEqual(browser_budget({"MemTotal": 1000, "MemAvailable": 100})["status"], "constrained")
        self.assertEqual(browser_budget({"MemTotal": 1000, "MemAvailable": 250})["status"], "comfortable")

    def test_does_not_claim_per_tab_memory(self):
        result = browser_budget({"MemTotal": 4096000, "MemAvailable": 2000000})
        self.assertNotIn("per_tab", result)


if __name__ == "__main__":
    unittest.main()
