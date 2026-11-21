"""Synthetic tests: no actual USB devices or Pi hardware are touched."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "raspberry_pi"))
from usb_vidpid_inventory import inventory


class UsbInventoryTests(unittest.TestCase):
    def test_no_consent_never_reads_root(self):
        self.assertEqual(inventory(root=Path("/nonexistent"), consent=False)["status"], "not_authorized")

    def test_empty_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = inventory(root=Path(tmp), consent=True)
            self.assertEqual(result["devices"], [])
            self.assertEqual(result["device_identity"], "unverified")

    def test_valid_and_invalid_identifiers(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "1-1"
            good.mkdir()
            (good / "idVendor").write_text("0483\n")
            (good / "idProduct").write_text("5740\n")
            bad = Path(tmp) / "1-2"
            bad.mkdir()
            (bad / "idVendor").write_text("nothex")
            (bad / "idProduct").write_text("5740")
            result = inventory(root=Path(tmp), consent=True)
            self.assertEqual(result["devices"], [{"vendor_id": "0483", "product_id": "5740"}])
            self.assertEqual(result["usb_access"], "not_tested")

    def test_missing_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(inventory(root=Path(tmp) / "missing", consent=True)["status"], "sysfs_unavailable")

    def test_invalid_consent(self):
        with self.assertRaises(ValueError):
            inventory(consent=1)


if __name__ == "__main__":
    unittest.main()
