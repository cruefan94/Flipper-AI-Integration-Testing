"""Offline regression matrix for Pi EXT4 risk triage. No hardware or network access."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "raspberry_pi" / "ext4_storage_risk.py"
spec = importlib.util.spec_from_file_location("pi_ext4_storage_risk", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PiStorageRiskMatrix(unittest.TestCase):
    def test_explicit_ext4_error_without_extra_keywords_is_critical(self):
        result = module.classify("EXT4-fs error (device sda2): ext4_lookup: issue")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["ext4_explicit_error_lines"], 1)
        self.assertEqual(result["devices"], ["sda2"])

    def test_negated_io_and_remount_are_not_critical(self):
        result = module.classify("no I/O errors\nnot remounting filesystem read-only")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertEqual(result["io_error_lines"], 0)
        self.assertEqual(result["readonly_remount_lines"], 0)

    def test_real_error_survives_negated_text_on_same_line(self):
        result = module.classify("no I/O errors; Buffer I/O error on dev sda2")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["io_error_lines"], 1)

    def test_readonly_remount_is_critical(self):
        result = module.classify("EXT4-fs (sda2): Remounting filesystem read-only")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["readonly_remount_lines"], 1)

    def test_throttle_union_keeps_prior_warning(self):
        result = module.classify("throttled=0x1 throttled=0x0")
        self.assertTrue(result["throttling_flag_nonzero"])
        self.assertEqual(result["severity"], "REVIEW")

    def test_metadata_corruption_is_critical(self):
        result = module.classify("EXT4-fs error (device sda2): metadata checksum invalid")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["metadata_corruption_lines"], 1)

    def test_no_raw_log_or_secrets_in_result(self):
        secret = "private-session-token-do-not-publish"
        result = module.classify("EXT4-fs error (device sda2): " + secret)
        self.assertNotIn(secret, repr(result))
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")

    def test_multiple_devices_are_deduplicated_and_sorted(self):
        result = module.classify(
            "EXT4-fs warning (device sdb1): check\n"
            "EXT4-fs error (device sda2): lookup\n"
            "EXT4-fs warning (device sdb1): check"
        )
        self.assertEqual(result["devices"], ["sda2", "sdb1"])
        self.assertEqual(result["ext4_explicit_error_lines"], 1)
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")

    def test_zero_throttle_snapshot_does_not_override_prior_warning(self):
        result = module.classify("throttled=0x50000\nthrottled=0x0")
        self.assertTrue(result["throttling_flag_nonzero"])
        self.assertEqual(result["severity"], "REVIEW")

    def test_kernel_prefix_ext4_error_is_critical(self):
        result = module.classify("EXT4-fs (sda2): error: ext4_find_entry failed")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["ext4_explicit_error_lines"], 1)
        self.assertEqual(result["devices"], ["sda2"])

    def test_kernel_prefix_ext4_warning_requires_review(self):
        result = module.classify("EXT4-fs (sdb1): warning: journal issue")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertEqual(result["devices"], ["sdb1"])
        self.assertEqual(result["ext4_warning_lines"], 1)

    def test_kernel_prefix_unrelated_text_does_not_match(self):
        result = module.classify("EXT4-fs (sda2): mounted filesystem")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertEqual(result["devices"], [])

    def test_empty_input_is_not_diagnosis(self):
        result = module.classify("")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertIn("not proof", result["limitations"])


if __name__ == "__main__":
    unittest.main()
