"""Synthetic offline tests: remount detection must not write to any hardware."""
import unittest
from raspberry_pi.ext4_storage_risk import classify

class ReadonlyRemountTests(unittest.TestCase):
    def test_ext4_readonly_remount_is_critical_without_io_error(self):
        r = classify("EXT4-fs error (device sda2): Remounting filesystem read-only")
        self.assertEqual(r["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(r["readonly_remount_lines"], 1)
        self.assertEqual(r["io_error_lines"], 0)

    def test_generic_remount_readonly_is_critical(self):
        r = classify("Remounting filesystem read-only")
        self.assertEqual(r["severity"], "CRITICAL_STORAGE_RISK")

    def test_normal_ext4_mount_is_not_critical(self):
        r = classify("EXT4-fs (sda2): mounted filesystem with ordered data mode")
        self.assertEqual(r["severity"], "NO_MATCH")
        self.assertEqual(r["readonly_remount_lines"], 0)

    def test_negated_io_status_stays_harmless(self):
        r = classify("no I/O errors; throttled=0x0")
        self.assertEqual(r["severity"], "NO_MATCH")

if __name__ == "__main__":
    unittest.main()
