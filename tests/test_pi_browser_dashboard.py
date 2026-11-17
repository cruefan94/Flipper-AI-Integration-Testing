"""Synthetic read-only browser dashboard tests; no Tk display needed."""
import unittest
from unittest.mock import patch

from raspberry_pi.pi_browser_dashboard import BrowserAdvicePanel, format_budget


class Label:
    def __init__(self):
        self.text = ""
    def configure(self, *, text):
        self.text = text


class BrowserPanelTests(unittest.TestCase):
    def test_valid_budget(self):
        title, advice = format_budget({
            "status": "constrained", "total_mib": 4096,
            "available_mib": 512, "recommendations": ["Close tabs manually."]
        })
        self.assertIn("512 / 4096", title)
        self.assertIn("manually", advice)

    def test_malformed_budget_fails_closed(self):
        for data in ({}, {"status": "comfortable", "total_mib": 100,
                          "available_mib": 101, "recommendations": ["OK"]},
                     {"status": "critical", "total_mib": True,
                      "available_mib": 0, "recommendations": ["OK"]}):
            self.assertEqual(format_budget(data)[0], "Unavailable")

    def test_failed_refresh_clears_stale_and_schedules(self):
        panel = BrowserAdvicePanel.__new__(BrowserAdvicePanel)
        panel.closed = False
        panel.timer_id = None
        panel.interval_ms = 10000
        panel.memory = Label()
        panel.advice = Label()
        panel.memory.text = "stale"
        panel.after = lambda ms, callback: "scheduled"
        with patch("raspberry_pi.pi_browser_dashboard.snapshot",
                   side_effect=OSError("missing")):
            panel.refresh()
        self.assertEqual(panel.memory.text, "Unavailable")
        self.assertEqual(panel.timer_id, "scheduled")

    def test_closed_panel_does_not_read(self):
        panel = BrowserAdvicePanel.__new__(BrowserAdvicePanel)
        panel.closed = True
        with patch("raspberry_pi.pi_browser_dashboard.snapshot") as read:
            panel.refresh()
        read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
