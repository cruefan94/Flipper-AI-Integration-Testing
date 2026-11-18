"""Regression tests for explicit EXT4 error severity; offline and synthetic only."""
import unittest
from raspberry_pi.ext4_storage_risk import classify


class ExplicitExt4ErrorTests(unittest.TestCase):
    def test_generic_ext4_error_is_critical(self):
        result = classify("EXT4-fs error (device sda2): ext4_lookup:123: inode 9")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["ext4_explicit_error_lines"], 1)
        self.assertEqual(result["devices"], ["sda2"])

    def test_warning_without_error_is_review(self):
        result = classify("EXT4-fs warning (device sda2): mount option noted")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertEqual(result["ext4_explicit_error_lines"], 0)

    def test_unrelated_error_not_misclassified(self):
        result = classify("Network error (device eth0): timeout")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertEqual(result["ext4_explicit_error_lines"], 0)

    def test_no_raw_log_exposure(self):
        secret = "PRIVATE_DIAGNOSTIC_TOKEN"
        result = classify(f"EXT4-fs error (device sda2): {secret}")
        self.assertNotIn(secret, str(result))


if __name__ == "__main__":
    unittest.main()
