import unittest
from pi_lab.qflipper_usb_evidence import parse_lsusb, UsbDevice
from pi_lab.qflipper_usb_report import summarize_usb


class UsbSummaryTests(unittest.TestCase):
    def test_empty(self):
        result = summarize_usb(())
        self.assertEqual((result.device_count, result.unique_vid_pid_count), (0, 0))
        self.assertIn("unverified", result.conclusion)

    def test_deduplicated_vid_pid(self):
        devices = parse_lsusb("Bus 002 Device 004: ID 1234:abcd private-description\\nBus 001 Device 002: ID 1234:abcd other")
        result = summarize_usb(devices)
        self.assertEqual((result.device_count, result.unique_vid_pid_count), (2, 1))
        self.assertEqual(result.entries[0], "Bus 001 Device 002: 1234:abcd")
        self.assertNotIn("private-description", repr(result))

    def test_duplicate_location_rejected(self):
        device = UsbDevice("001", "002", "1234", "abcd")
        with self.assertRaises(ValueError):
            summarize_usb((device, device))

    def test_malformed_evidence_rejected(self):
        for device in (UsbDevice("a01", "002", "1234", "abcd"),
                       UsbDevice("001", "002", "1234", "ABCD"),
                       UsbDevice("001", "002", "1234", "zzzz")):
            with self.subTest(device=device), self.assertRaises(ValueError):
                summarize_usb((device,))

    def test_reject_non_tuple(self):
        with self.assertRaises(ValueError):
            summarize_usb([])

    def test_reject_oversized(self):
        with self.assertRaises(ValueError):
            summarize_usb((UsbDevice("001", "001", "1234", "abcd"),) * 257)


if __name__ == "__main__":
    unittest.main()
