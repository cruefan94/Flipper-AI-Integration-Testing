"""Additional headless browser-panel regressions following independent review.

No Tk root, Pi hardware, process control or system configuration changes.
"""
import unittest
from unittest.mock import patch

from raspberry_pi.pi_browser_dashboard import BrowserAdvicePanel
from tests.test_pi_browser_lifecycle import panel_fixture


GOOD = {
    "status": "comfortable", "total_mib": 4096,
    "available_mib": 2048, "recommendations": ["No action."]
}


class BrowserPanelReviewRegressions(unittest.TestCase):
    def test_scheduled_callback_refreshes_and_reschedules(self):
        panel, events = panel_fixture()
        scheduled = []
        def after(interval, callback):
            scheduled.append(callback)
            events.append(("schedule", interval))
            return f"timer-{len(scheduled)}"
        panel.after = after
        with patch("raspberry_pi.pi_browser_dashboard.snapshot", return_value=GOOD) as read:
            panel.refresh()
            self.assertEqual(read.call_count, 1)
            self.assertEqual(len(scheduled), 1)
            scheduled.pop(0)()
            self.assertEqual(read.call_count, 2)
        self.assertEqual(len(scheduled), 1)
        self.assertEqual(events, [("schedule", 10000), ("cancel", "timer-1"), ("schedule", 10000)])
        panel.stop()

    def test_stop_twice_cancels_active_timer_once(self):
        panel, events = panel_fixture()
        panel.timer_id = "pending"
        panel.stop()
        panel.stop()
        self.assertEqual(events, [("cancel", "pending")])
        self.assertTrue(panel.closed)
        self.assertIsNone(panel.timer_id)

    def test_failed_snapshot_is_unavailable_and_retries(self):
        for error in (OSError("procfs"), ValueError("malformed"), TypeError("bad data")):
            with self.subTest(error=type(error).__name__):
                panel, events = panel_fixture()
                with patch("raspberry_pi.pi_browser_dashboard.snapshot", side_effect=error) as read:
                    panel.refresh()
                read.assert_called_once_with()
                self.assertEqual(panel.memory.text, "Unavailable")
                self.assertIn("unavailable", panel.advice.text.lower())
                self.assertEqual(events, [("schedule", 10000)])
                panel.stop()

    def test_stopped_callback_does_not_read_or_reschedule(self):
        panel, events = panel_fixture()
        callbacks = []
        panel.after = lambda interval, callback: callbacks.append(callback) or "timer"
        with patch("raspberry_pi.pi_browser_dashboard.snapshot", return_value=GOOD) as read:
            panel.refresh()
            panel.stop()
            callbacks[0]()
            self.assertEqual(read.call_count, 1)
        self.assertEqual(events, [("cancel", "timer")])


if __name__ == "__main__":
    unittest.main()
