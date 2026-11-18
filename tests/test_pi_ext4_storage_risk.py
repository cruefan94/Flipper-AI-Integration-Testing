import unittest
from raspberry_pi.ext4_storage_risk import classify

class StorageRiskTests(unittest.TestCase):
    def test_observed_directory_read_failure(self):
        result = classify("EXT4-fs warning (device sda2): dx_probe:823: error -5 reading directory block")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["devices"], ["sda2"])

    def test_warning_alone_not_hardware_proof(self):
        result = classify("EXT4-fs warning (device sda2): benign unknown warning")
        self.assertEqual(result["severity"], "REVIEW")

    def test_clean_log(self):
        self.assertEqual(classify("temp=40.4'C").get("severity"), "NO_MATCH")

    def test_usb_and_power(self):
        result = classify("usb 2-1: USB disconnect\nthrottled=0x0")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], False)

    def test_nonzero_throttling_requires_review(self):
        result = classify("throttled=0x50000")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], True)
        self.assertIn("not proof of current undervoltage", result["guidance"])

    def test_zero_throttling_does_not_raise_alarm(self):
        result = classify("throttled=0x0")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertIs(result["throttling_flag_nonzero"], False)

    def test_io_without_ext4(self):
        self.assertEqual(classify("Buffer I/O error on dev sda").get("severity"), "CRITICAL_STORAGE_RISK")

    def test_earlier_throttle_not_erased_by_later_clean_snapshot(self):
        result = classify("throttled=0x50000\nthrottled=0x0")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], True)

    def test_zero_then_nonzero_throttle_requires_review(self):
        result = classify("throttled=0x0\nthrottled=0x1")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], True)

    def test_multiple_zero_throttle_snapshots_stay_clear(self):
        result = classify("throttled=0x0\nthrottled=0x0")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertIs(result["throttling_flag_nonzero"], False)

    def test_negated_io_status_not_critical(self):
        for line in ("no I/O errors", "0 I/O errors", "zero buffer I/O errors"):
            with self.subTest(line=line):
                result = classify(line)
                self.assertEqual(result["severity"], "NO_MATCH")
                self.assertEqual(result["io_error_lines"], 0)

    def test_real_io_error_remains_critical_after_clean_status(self):
        result = classify("no I/O errors\nBuffer I/O error on dev sda")
        self.assertEqual(result["severity"], "CRITICAL_STORAGE_RISK")
        self.assertEqual(result["io_error_lines"], 1)

if __name__ == "__main__":
    unittest.main()
