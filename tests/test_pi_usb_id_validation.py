"""Hardware-free USB identifier display regression tests."""
import unittest

from raspberry_pi.pi_usb_desktop import format_devices, safe_usb_id


class UsbIdValidationTests(unittest.TestCase):
    def test_valid_four_digit_hex_normalized(self):
        self.assertEqual(safe_usb_id(" 1A2b "), "1a2b")
        self.assertEqual(safe_usb_id("0000"), "0000")

    def test_invalid_and_malicious_values_masked(self):
        for value in (None, 1234, "", "123", "12345", "0x1234",
                      "12G4", "12\u202e34", "1234\nSpoofed", "１２３４"):
            with self.subTest(value=value):
                self.assertEqual(safe_usb_id(value), "????")

    def test_bad_ids_cannot_spoof_device_row(self):
        row = format_devices([{"port": "/dev/ttyUSB0", "vid": "ABCD\nFlipper",
                               "pid": "1234", "product": "USB serial"}])[0]
        self.assertIn("[????:1234]", row)
        self.assertNotIn("Flipper", row)


if __name__ == "__main__":
    unittest.main()
