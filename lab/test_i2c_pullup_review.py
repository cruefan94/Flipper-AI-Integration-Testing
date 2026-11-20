"""Public-safe synthetic tests; no device access."""
import unittest
from i2c_pullup_review import review

BASE = dict(target="esp32-wroom", sda_pullup_v=3.3, scl_pullup_v=3.3, common_ground=True, level_shifter=False)

class PullupReviewTests(unittest.TestCase):
    def test_nominal_is_review_not_approval(self):
        self.assertEqual(review(BASE)["decision"], "REVIEW")
    def test_five_volts_blocks(self):
        for pin in ("sda_pullup_v", "scl_pullup_v"):
            self.assertEqual(review({**BASE, pin: 5})["decision"], "BLOCK")
    def test_no_ground_blocks(self):
        self.assertEqual(review({**BASE, "common_ground": False})["decision"], "BLOCK")
    def test_level_shifter_requires_review(self):
        self.assertEqual(review({**BASE, "level_shifter": True})["decision"], "BLOCK")
    def test_mismatch_blocks(self):
        self.assertEqual(review({**BASE, "scl_pullup_v": 2.7})["decision"], "BLOCK")
    def test_invalid_schema_blocks(self):
        self.assertEqual(review({**BASE, "extra": "x"})["decision"], "BLOCK")
        self.assertEqual(review({**BASE, "target": "unknown"})["decision"], "BLOCK")
    def test_invalid_numbers_block(self):
        for v in (float("nan"), float("inf"), -1, 0, "3.3", True, 25):
            self.assertEqual(review({**BASE, "sda_pullup_v": v})["decision"], "BLOCK")
    def test_other_targets_not_approved(self):
        for target in ("esp32-s2", "raspberry-pi-4b", "flipper-zero"):
            self.assertEqual(review({**BASE, "target": target})["decision"], "REVIEW")

if __name__ == "__main__":
    unittest.main()
