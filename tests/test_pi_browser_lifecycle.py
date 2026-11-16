"""Headless lifecycle regression tests for the read-only Pi browser panel.

These tests never instantiate a Tk root or touch Pi/Flipper hardware.
"""
import unittest
from unittest.mock import patch

from raspberry_pi.pi_browser_dashboard import BrowserAdvicePanel, format_budget


class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, *, text):
        self.text = text


def panel_fixture():
    panel = BrowserAdvicePanel.__new__(BrowserAdvicePanel)
    panel.closed = False
    panel.interval_ms = 10_000
    panel.timer_id = None
    panel.memory = DummyLabel()
    panel.advice = DummyLabel()
    events = []
    panel.after = lambda interval, callback: events.append(("schedule", interval)) or "next"
    panel.after_cancel = lambda timer_id: events.append(("cancel", timer_id))
    return panel, events


class BrowserLifecycleTests(unittest.TestCase):
    def test_refresh_cancels_existing_timer_before_reschedule(self):
        panel, events = panel_fixture()
        panel.timer_id = "previous"
        with patch("raspberry_pi.pi_browser_dashboard.snapshot", return_value={
            "status": "comfortable", "total_mib": 4096,
            "available_mib": 2048, "recommendations": ["No action."]
        }):
            panel.refresh()
        self.assertEqual(events, [("cancel", "previous"), ("schedule", 10_000)])
        self.assertEqual(panel.timer_id, "next")

    def test_stop_cancels_timer_and_prevents_future_reads(self):
        panel, events = panel_fixture()
        panel.timer_id = "previous"
        panel.stop()
        self.assertTrue(panel.closed)
        self.assertIsNone(panel.timer_id)
        self.assertEqual(events, [("cancel", "previous")])
        with patch("raspberry_pi.pi_browser_dashboard.snapshot") as read:
            panel.refresh()
        read.assert_not_called()
        self.assertEqual(events, [("cancel", "previous")])

    def test_stop_without_timer_is_safe(self):
        panel, events = panel_fixture()
        panel.stop()
        panel.stop()
        self.assertEqual(events, [])

    def test_invalid_advice_never_displays_as_valid(self):
        base = {"status": "comfortable", "total_mib": 4096, "available_mib": 2000}
        for recommendations in ([], [None], "OK", [1], None):
            with self.subTest(recommendations=recommendations):
                title, _ = format_budget({**base, "recommendations": recommendations})
                self.assertEqual(title, "Unavailable")


if __name__ == "__main__":
    unittest.main()
