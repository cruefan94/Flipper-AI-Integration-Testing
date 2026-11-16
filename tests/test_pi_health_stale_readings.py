"""Regression: a failed sensor read must not retain stale live numbers."""
import unittest
from unittest.mock import patch

from raspberry_pi.pi_health_desktop import PiHealthWindow


class FakeLabel:
    def __init__(self, value=""):
        self.text = value

    def configure(self, *, text):
        self.text = text


class FakeRoot:
    def __init__(self):
        self.scheduled = []

    def after(self, interval, callback):
        self.scheduled.append((interval, callback))
        return "next-timer"

    def after_cancel(self, timer):
        raise AssertionError("unexpected timer cancellation")


class StaleReadingTests(unittest.TestCase):
    def test_failed_refresh_clears_previous_values_and_reschedules(self):
        window = PiHealthWindow.__new__(PiHealthWindow)
        window.root = FakeRoot()
        window.interval_ms = 10_000
        window.timer_id = None
        window.labels = {"CPU temperature": FakeLabel("41.0 °C"),
                         "Available RAM": FakeLabel("100 / 200 MiB")}
        window.status = FakeLabel()
        with patch("raspberry_pi.pi_health_desktop.snapshot",
                   side_effect=OSError("sensor read failed")):
            window.refresh()
        self.assertTrue(all(v.text == "Unavailable" for v in window.labels.values()))
        self.assertIn("OSError", window.status.text)
        self.assertEqual(window.root.scheduled[0][0], 10_000)
        self.assertEqual(window.timer_id, "next-timer")


if __name__ == "__main__":
    unittest.main()
