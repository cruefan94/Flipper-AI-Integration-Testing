"""Synthetic tests; no Tk display or Pi hardware required."""
import unittest
from unittest.mock import patch
from raspberry_pi.pi_readonly_dashboard import HealthPanel


class FakeLabel:
    def __init__(self, text="stale"):
        self.text = text
    def configure(self, **kwargs):
        self.text = kwargs["text"]


class DashboardTests(unittest.TestCase):
    def test_failure_clears_all_values_and_reschedules(self):
        panel = HealthPanel.__new__(HealthPanel)
        panel.closed = False
        panel.timer_id = None
        panel.interval_ms = 10000
        panel.labels = {"CPU temperature": FakeLabel(), "Available RAM": FakeLabel()}
        panel.status = FakeLabel()
        panel.after = lambda ms, callback: "scheduled"
        with patch("raspberry_pi.pi_readonly_dashboard.snapshot", side_effect=OSError("sensor")):
            panel.refresh()
        self.assertTrue(all(label.text == "Unavailable" for label in panel.labels.values()))
        self.assertEqual(panel.timer_id, "scheduled")

    def test_closed_panel_does_not_refresh(self):
        panel = HealthPanel.__new__(HealthPanel)
        panel.closed = True
        with patch("raspberry_pi.pi_readonly_dashboard.snapshot") as read:
            panel.refresh()
        read.assert_not_called()


if __name__ == "__main__":
    unittest.main()
