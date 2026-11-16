"""Host-only tests: no Pi hardware, USB ports, or Tk display required."""
import unittest
from unittest.mock import patch
from raspberry_pi.pi_usb_desktop import UsbInventoryPanel, format_devices


class FakeRows:
    def __init__(self):
        self.values = []
    def delete(self, *args):
        self.values.clear()
    def insert(self, _index, value):
        self.values.append(value)


class FakeStatus:
    def configure(self, **kwargs):
        self.text = kwargs["text"]


class UsbDesktopTests(unittest.TestCase):
    def test_unknown_identity_is_not_assumed(self):
        self.assertIn("Unidentified", format_devices([{"port": "/dev/ttyACM0"}])[0])

    def test_no_devices(self):
        self.assertIn("No ttyACM", format_devices([])[0])

    def test_refresh_failure_clears_stale_ports_and_reschedules(self):
        panel = UsbInventoryPanel.__new__(UsbInventoryPanel)
        panel.closed = False
        panel.timer_id = None
        panel.interval_ms = 10000
        panel.rows = FakeRows()
        panel.rows.values = ["stale /dev/ttyUSB0"]
        panel.status = FakeStatus()
        panel.after = lambda ms, fn: "timer"
        with patch("raspberry_pi.pi_usb_desktop.inventory", side_effect=OSError("unavailable")):
            panel.refresh()
        self.assertEqual(panel.rows.values, ["Unavailable — USB inventory failed."])
        self.assertIn("cleared", panel.status.text)
        self.assertEqual(panel.timer_id, "timer")


if __name__ == "__main__":
    unittest.main()
