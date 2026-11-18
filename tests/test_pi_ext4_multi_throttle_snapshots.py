"""Offline synthetic tests; no Raspberry Pi hardware access."""
import unittest
from raspberry_pi.ext4_storage_risk import classify


class MultiThrottleSnapshotTests(unittest.TestCase):
    def test_multiple_samples_same_line_preserve_prior_nonzero(self):
        result = classify("throttled=0x50000; throttled=0x0")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], True)

    def test_multiple_zero_samples_are_clear(self):
        result = classify("throttled=0x0; throttled=0x0")
        self.assertEqual(result["severity"], "NO_MATCH")
        self.assertIs(result["throttling_flag_nonzero"], False)

    def test_nonzero_second_sample_detected(self):
        result = classify("throttled=0x0 throttled=0x1")
        self.assertEqual(result["severity"], "REVIEW")
        self.assertIs(result["throttling_flag_nonzero"], True)


if __name__ == "__main__":
    unittest.main()
