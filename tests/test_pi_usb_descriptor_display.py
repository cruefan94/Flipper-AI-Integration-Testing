"""Synthetic, hardware-free USB display safety checks."""
import unittest
from raspberry_pi.pi_usb_desktop import format_devices, safe_label


class UsbDescriptorDisplayTests(unittest.TestCase):
    def test_control_characters_cannot_create_extra_lines(self):
        rows = format_devices([{"port": "/dev/ttyACM0\nFAKE", "vid": "12\x1b34",
                                "pid": "5678", "product": "Device\r\nWarning\x00"}])
        self.assertEqual(len(rows), 1)
        self.assertNotIn("\n", rows[0])
        self.assertNotIn("\r", rows[0])
        self.assertNotIn("\x1b", rows[0])
        self.assertIn("Device Warning", rows[0])

    def test_long_untrusted_descriptors_are_bounded(self):
        rows = format_devices([{"port": "p" * 200, "vid": "a" * 200,
                                "pid": "b" * 200, "product": "x" * 1000}])
        self.assertLessEqual(len(rows[0]), 48 + 2 + 1 + 12 + 1 + 12 + 3 + 96)

    def test_missing_and_empty_descriptors_have_fallback(self):
        self.assertEqual(safe_label(None, "Unknown"), "Unknown")
        self.assertEqual(safe_label("\x00\n", "Unknown"), "Unknown")
        self.assertEqual(format_devices([]), ["No ttyACM/ttyUSB serial ports detected."])


if __name__ == "__main__":
    unittest.main()
