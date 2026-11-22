"""Offline regression tests for the Pi meminfo snapshot parser.

Synthetic data only. No Pi, filesystem, hardware, network or secrets accessed.
"""
import unittest

from meminfo_snapshot_parser import parse_meminfo


class MeminfoBoundaryTests(unittest.TestCase):
    def test_zero_available_is_valid_critical(self):
        self.assertEqual(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 0 kB", 0).advice, "CRITICAL")

    def test_equal_total_and_available(self):
        self.assertEqual(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 4096000 kB", 1).advice, "OK")

    def test_reordered_fields(self):
        self.assertEqual(parse_meminfo("MemAvailable: 2048000 kB\nMemTotal: 4096000 kB", 1).advice, "OK")

    def test_duplicate_available_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 2048000 kB\nMemAvailable: 1 kB", 1))

    def test_trailing_non_numeric_value_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 2048000 kB extra", 1))

    def test_fractional_kib_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 2.5 kB", 1))

    def test_zero_total_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 0 kB\nMemAvailable: 0 kB", 1))

    def test_implausibly_large_total_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 17592186044417 kB\nMemAvailable: 1 kB", 1))

    def test_oversized_input_rejected(self):
        self.assertIsNone(parse_meminfo("X" * 65537, 1))

    def test_non_string_rejected(self):
        self.assertIsNone(parse_meminfo(b"MemTotal: 4096000 kB", 1))

    def test_negative_tab_count_rejected(self):
        self.assertIsNone(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 2048000 kB", -1))

    def test_unknown_sensitive_field_never_echoed(self):
        result = parse_meminfo("MemTotal: 4096000 kB\nPrivateToken: DO_NOT_ECHO\nMemAvailable: 2048000 kB", 1)
        self.assertNotIn("DO_NOT_ECHO", repr(result))
        self.assertEqual(result.advice, "OK")


if __name__ == "__main__":
    unittest.main()
