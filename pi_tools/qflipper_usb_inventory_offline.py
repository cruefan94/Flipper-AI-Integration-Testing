"""Offline, redacted qFlipper USB inventory classifier. No device access.

Input: manually supplied lines from lsusb; do not upload unredacted system logs.
This module never executes commands or writes to the Pi/Flipper.
"""
from dataclasses import dataclass
import re
import unittest

USB_LINE = re.compile(r"^Bus\s+\d{3}\s+Device\s+\d{3}:\s+ID\s+([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s|$)")
FLIPPER_VENDOR_ID = "0483"  # STMicroelectronics; not sufficient to identify Flipper
MAX_INPUT_CHARS = 65536


@dataclass(frozen=True)
class UsbInventory:
    device_count: int
    st_vendor_count: int
    status: str


def summarize_lsusb(snapshot: object) -> UsbInventory:
    """Classify a supplied USB snapshot without returning serials or descriptions.

    ST's vendor ID is shared by many devices; 'POSSIBLE_ST_DEVICE' is
    deliberately not proof of a connected Flipper or qFlipper RPC.
    """
    if type(snapshot) is not str or len(snapshot) > MAX_INPUT_CHARS:
        raise ValueError("invalid USB snapshot")
    count = st = 0
    for line in snapshot.splitlines():
        match = USB_LINE.match(line)
        if match:
            count += 1
            if match.group(1).lower() == FLIPPER_VENDOR_ID:
                st += 1
    return UsbInventory(count, st, "POSSIBLE_ST_DEVICE" if st else "NO_ST_VENDOR_SEEN")


class UsbInventoryTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_lsusb("").status, "NO_ST_VENDOR_SEEN")

    def test_generic_hub(self):
        self.assertEqual(summarize_lsusb("Bus 001 Device 002: ID 2109:3431 VIA Labs Hub").device_count, 1)

    def test_st_is_not_flipper_proof(self):
        r = summarize_lsusb("Bus 001 Device 003: ID 0483:5740 SecretSerial")
        self.assertEqual((r.st_vendor_count, r.status), (1, "POSSIBLE_ST_DEVICE"))
        self.assertNotIn("SecretSerial", repr(r))

    def test_case_insensitive_vendor(self):
        self.assertEqual(summarize_lsusb("Bus 001 Device 003: ID 0483:ABCD").st_vendor_count, 1)

    def test_reject_malformed_lines(self):
        self.assertEqual(summarize_lsusb("ID 0483:5740\nBus x Device y: ID 0483:5740").device_count, 0)

    def test_reject_non_string(self):
        with self.assertRaises(ValueError):
            summarize_lsusb(None)

    def test_reject_excessive_input(self):
        with self.assertRaises(ValueError):
            summarize_lsusb("x" * (MAX_INPUT_CHARS + 1))

    def test_no_usb_commands(self):
        self.assertFalse(hasattr(__import__(__name__), "scan_hardware"))


if __name__ == "__main__":
    unittest.main()
