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

    def test_io_without_ext4(self):
        self.assertEqual(classify("Buffer I/O error on dev sda").get("severity"), "CRITICAL_STORAGE_RISK")

if __name__ == "__main__":
    unittest.main()
