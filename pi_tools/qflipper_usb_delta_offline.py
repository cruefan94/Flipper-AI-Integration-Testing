"""Offline comparison of manually supplied USB snapshots. No hardware access.

Never prints raw device descriptions, serials, paths, or identifiers.
An ST vendor entry is NOT proof of a connected Flipper.
"""
from dataclasses import dataclass
import unittest

try:
    from qflipper_usb_inventory_offline import summarize_lsusb
except ModuleNotFoundError:
    from pi_tools.qflipper_usb_inventory_offline import summarize_lsusb


@dataclass(frozen=True)
class UsbDelta:
    before_count: int
    after_count: int
    count_change: int
    st_before: int
    st_after: int
    assessment: str


def compare_snapshots(before: object, after: object) -> UsbDelta:
    """Compare sanitized aggregates only; reject malformed snapshots closed."""
    first = summarize_lsusb(before)
    second = summarize_lsusb(after)
    if second.st_vendor_count > first.st_vendor_count:
        assessment = "ST_COUNT_INCREASED_NOT_FLIPPER_PROOF"
    elif second.st_vendor_count < first.st_vendor_count:
        assessment = "ST_COUNT_DECREASED_NOT_FLIPPER_PROOF"
    elif second.device_count != first.device_count:
        assessment = "DEVICE_COUNT_CHANGED_IDENTITY_UNVERIFIED"
    else:
        assessment = "NO_COUNT_CHANGE_IDENTITY_UNVERIFIED"
    return UsbDelta(first.device_count, second.device_count,
                    second.device_count - first.device_count,
                    first.st_vendor_count, second.st_vendor_count, assessment)


class OfflineDeltaTests(unittest.TestCase):
    def test_new_st_device_not_flipper_proof(self):
        result = compare_snapshots("", "Bus 001 Device 002: ID 0483:5740 PrivateSerial")
        self.assertEqual(result.assessment, "ST_COUNT_INCREASED_NOT_FLIPPER_PROOF")
        self.assertNotIn("PrivateSerial", repr(result))

    def test_generic_device_change(self):
        result = compare_snapshots("", "Bus 001 Device 002: ID 2109:3431 Hub")
        self.assertEqual(result.assessment, "DEVICE_COUNT_CHANGED_IDENTITY_UNVERIFIED")

    def test_no_change(self):
        self.assertEqual(compare_snapshots("", "").assessment,
                         "NO_COUNT_CHANGE_IDENTITY_UNVERIFIED")

    def test_st_decrease(self):
        result = compare_snapshots("Bus 001 Device 002: ID 0483:5740", "")
        self.assertEqual(result.st_after, 0)
        self.assertEqual(result.assessment, "ST_COUNT_DECREASED_NOT_FLIPPER_PROOF")

    def test_conflicting_snapshot_fails_closed(self):
        with self.assertRaises(ValueError):
            compare_snapshots("", "Bus 001 Device 002: ID 0483:5740\nBus 001 Device 002: ID 2109:3431")

    def test_malformed_snapshot_fails_closed(self):
        with self.assertRaises(ValueError):
            compare_snapshots("Bus 001 Device 002: ID missing", "")

    def test_duplicate_lines_do_not_inflate_delta(self):
        line = "Bus 001 Device 002: ID 0483:5740"
        self.assertEqual(compare_snapshots("", line + "\n" + line).count_change, 1)

    def test_reject_non_string(self):
        with self.assertRaises(ValueError):
            compare_snapshots(None, "")


if __name__ == "__main__":
    unittest.main()
