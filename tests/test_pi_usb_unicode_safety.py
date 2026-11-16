"""Hardware-free checks for Unicode formatting attacks in USB labels."""
import unittest
from raspberry_pi.pi_usb_desktop import safe_label, format_devices


class UsbUnicodeSafetyTests(unittest.TestCase):
    def test_bidi_override_removed(self):
        label = safe_label("USB\u202eREVERSED\u202c", "Unknown")
        self.assertEqual(label, "USB REVERSED")

    def test_zero_width_and_isolates_removed(self):
        label = safe_label("ESP\u200b32\u2066Board\u2069", "Unknown")
        self.assertEqual(label, "ESP 32 Board")

    def test_port_row_stays_single_line(self):
        rows = format_devices([{"port": "/dev/ttyACM0\u202e", "vid": "1234",
                                "pid": "5678", "product": "Board\u200bTest"}])
        self.assertEqual(len(rows), 1)
        self.assertNotIn("\u202e", rows[0])
        self.assertNotIn("\u200b", rows[0])
        self.assertIn("Board Test", rows[0])


if __name__ == "__main__":
    unittest.main()
