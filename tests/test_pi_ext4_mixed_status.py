"""Synthetic offline regression: no device access or private logs."""
import unittest
from raspberry_pi.ext4_storage_risk import classify

class MixedStatusTests(unittest.TestCase):
    def test_real_error_after_negated_status_same_line(self):
        result = classify('no I/O errors; Buffer I/O error on dev sda')
        self.assertEqual(result['severity'], 'CRITICAL_STORAGE_RISK')
        self.assertEqual(result['io_error_lines'], 1)

    def test_only_negated_status_stays_clear(self):
        result = classify('no I/O errors; zero buffer I/O errors')
        self.assertEqual(result['severity'], 'NO_MATCH')
        self.assertEqual(result['io_error_lines'], 0)

if __name__ == '__main__':
    unittest.main()
