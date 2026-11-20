"""Offline, public-safe USB inventory delta classifier. Never probes hardware."""
import re
from collections import Counter
import unittest

ID = re.compile(r"^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$")

def classify(before, after):
    """Accept only anonymous VID:PID entries; never infer flashing authorization."""
    for entries in (before, after):
        if not isinstance(entries, list) or len(entries) > 64:
            raise ValueError("inventory must be a bounded list")
        if any(not isinstance(v, str) or not ID.fullmatch(v) for v in entries):
            raise ValueError("only anonymous VID:PID accepted; no paths or serials")
    old = Counter(x.lower() for x in before)
    new = Counter(x.lower() for x in after)
    added = sorted((new - old).elements())
    removed = sorted((old - new).elements())
    return {"added": added, "removed": removed,
            "classification": "AMBIGUOUS" if len(added) != 1 or removed else "REVIEW_REQUIRED",
            "authorized_to_flash": False}

class TestInventoryDelta(unittest.TestCase):
    def test_single_addition(self):
        self.assertEqual(classify([], ["10c4:ea60"])["classification"], "REVIEW_REQUIRED")
    def test_never_authorize(self):
        self.assertFalse(classify([], ["303a:1001"])["authorized_to_flash"])
    def test_multiple_added_ambiguous(self):
        self.assertEqual(classify([], ["10c4:ea60", "2341:0043"])["classification"], "AMBIGUOUS")
    def test_removal_ambiguous(self):
        self.assertEqual(classify(["10c4:ea60"], [])["classification"], "AMBIGUOUS")
    def test_duplicate_counts(self):
        self.assertEqual(classify(["10c4:ea60"], ["10c4:ea60", "10c4:ea60"])["added"], ["10c4:ea60"])
    def test_case_normalization(self):
        self.assertEqual(classify(["10C4:EA60"], ["10c4:ea60"])["added"], [])
    def test_reject_serial(self):
        with self.assertRaises(ValueError):
            classify([], ["10c4:ea60 SERIAL123"])
    def test_reject_path(self):
        with self.assertRaises(ValueError):
            classify([], ["/dev/ttyUSB0"])
    def test_reject_invalid_type(self):
        with self.assertRaises(ValueError):
            classify([], ["10c4:ea60", None])
    def test_reject_unbounded(self):
        with self.assertRaises(ValueError):
            classify([], ["10c4:ea60"] * 65)

if __name__ == "__main__":
    unittest.main()
