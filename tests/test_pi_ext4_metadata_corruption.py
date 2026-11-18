"""Offline regression coverage for EXT4 metadata corruption indicators."""
import unittest
from raspberry_pi.ext4_storage_risk import classify


class MetadataCorruptionTests(unittest.TestCase):
    def test_ext4_checksum_failure_is_critical(self):
        result = classify("EXT4-fs error (device sda2): metadata checksum failed")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["metadata_corruption_lines"], 1)

    def test_ext4_corrupt_inode_is_critical(self):
        result = classify("EXT4-fs error (device sda2): corrupt inode 441")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")

    def test_ext4_euclean_error_is_critical(self):
        result = classify("EXT4-fs error (device sda2): ext4_find_entry: error -117")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")

    def test_healthy_checksum_statement_not_critical(self):
        result = classify("EXT4-fs (sda2): metadata checksum verified")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertEqual(result["metadata_corruption_lines"], 0)

    def test_existing_directory_errors_still_critical(self):
        result = classify("EXT4-fs warning (device sda2): dx_probe:823")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")


if __name__ == "__main__":
    unittest.main()
