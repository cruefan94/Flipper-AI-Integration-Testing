"""Offline, redacted qFlipper USB inventory classifier. No device access.

Input: manually supplied lines from lsusb; do not upload unredacted system logs.
This module never executes commands or writes to the Pi/Flipper.
"""
from dataclasses import dataclass
import re
import unittest

USB_LINE = re.compile(r"^Bus\s+\d{3}\s+Device\s+\d{3}:\s+ID\s+([0-9a-fA-F]{4}):([0-9a-fA-F]{4})(?:\s|$)")
USB_ADDRESS_PREFIX = re.compile(r"^Bus\s+\d{3}\s+Device\s+\d{3}:")
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
    seen = {}
    for line in snapshot.splitlines():
        match = USB_LINE.match(line)
        if not match and USB_ADDRESS_PREFIX.match(line):
            # A recognizable address with a missing/broken ID is not a safe
            # complete snapshot; do not silently undercount devices.
            raise ValueError("malformed USB identity at recognized address")
        if match:
            # A pasted inventory may repeat the same USB address; do not
            # report repeated lines as additional physical devices.
            address = tuple(line.split()[:4])
            identity = (match.group(1).lower(), match.group(2).lower())
            if address in seen:
                if seen[address] != identity:
                    raise ValueError("conflicting USB identities for one address")
                continue
            seen[address] = identity
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

    def test_duplicate_inventory_line_is_not_a_second_device(self):
        line = "Bus 001 Device 003: ID 0483:5740 redacted"
        result = summarize_lsusb(line + "\n" + line)
        self.assertEqual((result.device_count, result.st_vendor_count), (1, 1))

    def test_same_vendor_on_distinct_usb_addresses(self):
        result = summarize_lsusb(
            "Bus 001 Device 003: ID 0483:5740\n"
            "Bus 001 Device 004: ID 0483:5740"
        )
        self.assertEqual((result.device_count, result.st_vendor_count), (2, 2))

    def test_repeated_address_with_different_description(self):
        result = summarize_lsusb(
            "Bus 001 Device 003: ID 0483:5740 First\n"
            "Bus 001 Device 003: ID 0483:5740 Second"
        )
        self.assertEqual(result.device_count, 1)

    def test_conflicting_vendor_at_same_address_rejected(self):
        with self.assertRaisesRegex(ValueError, "conflicting USB identities"):
            summarize_lsusb("Bus 001 Device 003: ID 0483:5740\nBus 001 Device 003: ID 2109:3431")

    def test_conflicting_product_at_same_address_rejected(self):
        with self.assertRaises(ValueError):
            summarize_lsusb("Bus 001 Device 003: ID 0483:5740\nBus 001 Device 003: ID 0483:df11")

    def test_same_identity_different_case_deduplicates(self):
        result = summarize_lsusb("Bus 001 Device 003: ID 0483:ABCD\nBus 001 Device 003: ID 0483:abcd")
        self.assertEqual((result.device_count, result.st_vendor_count), (1, 1))

    def test_missing_id_at_recognized_address_rejected(self):
        with self.assertRaisesRegex(ValueError, "malformed USB identity"):
            summarize_lsusb("Bus 001 Device 003: Product description only")

    def test_invalid_hex_at_recognized_address_rejected(self):
        with self.assertRaises(ValueError):
            summarize_lsusb("Bus 001 Device 003: ID 0483:ZZZZ")

    def test_mixed_valid_and_malformed_address_rejected(self):
        with self.assertRaises(ValueError):
            summarize_lsusb("Bus 001 Device 002: ID 2109:3431\nBus 001 Device 003: ID missing")

    def test_no_usb_commands(self):
        self.assertFalse(hasattr(__import__(__name__), "scan_hardware"))


if __name__ == "__main__":
    unittest.main()
