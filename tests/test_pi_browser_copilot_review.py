"""Additional headless browser-panel regressions following independent review.

No Tk root, Pi hardware, process control or system configuration changes.
"""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from raspberry_pi.pi_browser_dashboard import BrowserAdvicePanel
from raspberry_pi.pi_browser_memory_advisor import browser_budget, snapshot
class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, *, text):
        self.text = text


def panel_fixture():
    panel = BrowserAdvicePanel.__new__(BrowserAdvicePanel)
    panel.closed = False
    panel.interval_ms = 10000
    panel.timer_id = None
    panel.memory = DummyLabel()
    panel.advice = DummyLabel()
    events = []
    panel.after = lambda interval, callback: events.append(("schedule", interval)) or "next"
    panel.after_cancel = lambda timer_id: events.append(("cancel", timer_id))
    return panel, events


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


class BrowserBudgetBoundaryRegressions(unittest.TestCase):
    def test_pressure_thresholds_and_read_only_contract(self):
        # Inputs are procfs KiB; thresholds are strict: <10%, <25%.
        for available, expected in (
            (0, "critical"), (999, "critical"), (1000, "constrained"),
            (2499, "constrained"), (2500, "comfortable"),
            (10000, "comfortable"),
        ):
            with self.subTest(available_kib=available):
                result = browser_budget({"MemTotal": 10000, "MemAvailable": available})
                self.assertEqual(result["status"], expected)
                self.assertIs(result["read_only"], True)
                self.assertTrue(result["recommendations"])

    def test_invalid_counters_fail_closed(self):
        for total, available in (
            (None, 100), (0, 0), (True, 0), (100, True),
            (100, -1), (100, 101), ("100", 50),
        ):
            with self.subTest(total=total, available=available):
                result = browser_budget({"MemTotal": total, "MemAvailable": available})
                self.assertEqual(result["status"], "unavailable")
                self.assertIs(result["read_only"], True)
                self.assertIsNone(result["available_mib"])

    def test_snapshot_reads_synthetic_meminfo_only(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "proc").mkdir()
            (root / "proc" / "meminfo").write_text(
                "MemTotal:       4194304 kB\n"
                "MemAvailable:   524288 kB\n", encoding="utf-8"
            )
            result = snapshot(root)
            self.assertEqual(result["status"], "constrained")
            self.assertEqual(result["total_mib"], 4096)
            self.assertEqual(result["available_mib"], 512)
            self.assertIs(result["read_only"], True)


if __name__ == "__main__":
    unittest.main()
