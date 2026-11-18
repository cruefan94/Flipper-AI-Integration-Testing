"""Offline regression tests for negated read-only remount statements."""
import unittest
from raspberry_pi.ext4_storage_risk import classify

class NegatedRemountTests(unittest.TestCase):
    def test_negated_remount_not_critical(self):
        result = classify("EXT4-fs warning (device sda2): not remounting filesystem read-only")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertEqual(result["readonly_remount_lines"], 0)

    def test_negated_generic_message_not_critical(self):
        result = classify("never remounted filesystem read-only")
        self.assertEqual(result["severity"], "NO_MATCH")

    def test_actual_remount_remains_critical(self):
        result = classify("EXT4-fs error (device sda2): Remounting filesystem read-only")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["readonly_remount_lines"], 1)

    def test_mixed_positive_and_negated_still_critical(self):
        result = classify("not remounting filesystem read-only; Remounting filesystem read-only")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")

if __name__ == "__main__":
    unittest.main()
