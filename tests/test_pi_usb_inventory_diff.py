"""Offline synthetic tests; no USB devices, sysfs, or Pi hardware."""
import unittest
from raspberry_pi.usb_inventory_diff import compare

def snap(devices):
    return {"status": "read_only_inventory", "devices": devices}

def dev(v="0483", p="5740"):
    return {"vendor_id": v, "product_id": p}

class TestDiff(unittest.TestCase):
    def test_no_change(self):
        self.assertEqual(compare(snap([dev()]), snap([dev()]))["added"], [])
    def test_added(self):
        self.assertEqual(compare(snap([]), snap([dev()]))["added"][0]["count"], 1)
    def test_removed(self):
        self.assertEqual(compare(snap([dev()]), snap([]))["removed"][0]["count"], 1)
    def test_duplicates(self):
        self.assertEqual(compare(snap([dev()]), snap([dev(),dev()]))["added"][0]["count"], 1)
    def test_no_consent(self):
        with self.assertRaises(ValueError):
            compare({"status": "not_authorized", "devices":[]}, snap([]))
    def test_malformed(self):
        with self.assertRaises(ValueError):
            compare(snap([{"vendor_id":"../a","product_id":"0000"}]), snap([]))
    def test_size_limit(self):
        with self.assertRaises(ValueError):
            compare(snap([dev()]*257), snap([]))
    def test_no_identity_claim(self):
        self.assertEqual(compare(snap([]),snap([]))["identity"], "unverified")

if __name__ == "__main__":
    unittest.main()
