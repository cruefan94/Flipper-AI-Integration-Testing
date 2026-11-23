import unittest
from pi_lab.qflipper_usb_evidence import parse_lsusb, matches_vid_pid


class UsbEvidenceTests(unittest.TestCase):
    def test_normal_lsusb_description(self):
        devices = parse_lsusb("Bus 002 Device 005: ID 0483:5740 STMicroelectronics Device")
        self.assertEqual((devices[0].bus, devices[0].device), ("002", "005"))

    def test_without_description(self):
        self.assertEqual(len(parse_lsusb("Bus 002 Device 005: ID 0483:5740")), 1)

    def test_reject_literal_backslash_s(self):
        with self.assertRaises(ValueError):
            parse_lsusb(r"Bus 002 Device 005: ID 0483:5740\sSpoof")

    def test_empty(self):
        self.assertEqual(parse_lsusb(""), ())

    def test_parse_and_match(self):
        devices = parse_lsusb("Bus 001 Device 002: ID 1234:ABcd Example device")
        self.assertEqual((devices[0].vid, devices[0].pid), ("1234", "abcd"))
        self.assertTrue(matches_vid_pid(devices, "1234", "abcd"))
        self.assertFalse(matches_vid_pid(devices, "1234", "0000"))

    def test_descriptions_not_retained(self):
        self.assertNotIn("SERIAL-SENSITIVE", repr(parse_lsusb("Bus 001 Device 002: ID 1234:abcd SERIAL-SENSITIVE")))

    def test_reject_malformed(self):
        with self.assertRaises(ValueError):
            parse_lsusb("Bus 001 Device 002: ID invalid")

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            parse_lsusb("Bus 001 Device 002: ID 1234:abcd\nBus 001 Device 002: ID 4321:dcba")

    def test_limit(self):
        with self.assertRaises(ValueError):
            parse_lsusb("x" * 32769)

    def test_invalid_id(self):
        with self.assertRaises(ValueError):
            matches_vid_pid((), "ZZZZ", "0001")

    def test_no_command_execution(self):
        self.assertEqual(parse_lsusb("Bus 001 Device 001: ID 1d6b:0002 Linux Foundation"), parse_lsusb("Bus 001 Device 001: ID 1d6b:0002 Other description"))


if __name__ == "__main__":
    unittest.main()
