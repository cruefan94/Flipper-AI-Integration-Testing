"""Synthetic tests only: no Pi device, /proc read, or privileged operations."""
import unittest
from pi_lab.offline_memory_health import assess_meminfo


class MemoryHealthTests(unittest.TestCase):
    def test_low_pressure(self):
        result = assess_meminfo("MemTotal: 4000000 kB\nMemAvailable: 2400000 kB\n")
        self.assertEqual((result.available_percent, result.pressure), (60, "LOW"))

    def test_moderate_pressure(self):
        self.assertEqual(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 240 kB").pressure, "MODERATE")

    def test_high_pressure(self):
        self.assertEqual(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 90 kB").pressure, "HIGH")

    def test_zero_available(self):
        self.assertEqual(assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 0 kB").pressure, "HIGH")

    def test_ignores_other_fields(self):
        self.assertEqual(assess_meminfo("Hostname: secret\nMemTotal: 1000 kB\nMemAvailable: 500 kB").available_kib, 500)

    def test_rejects_duplicate(self):
        with self.assertRaises(ValueError):
            assess_meminfo("MemTotal: 1000 kB\nMemTotal: 900 kB\nMemAvailable: 500 kB")

    def test_rejects_invalid_units(self):
        with self.assertRaises(ValueError):
            assess_meminfo("MemTotal: 1000 MB\nMemAvailable: 500 kB")

    def test_rejects_impossible_available(self):
        with self.assertRaises(ValueError):
            assess_meminfo("MemTotal: 1000 kB\nMemAvailable: 1001 kB")

    def test_rejects_missing(self):
        with self.assertRaises(ValueError):
            assess_meminfo("MemTotal: 1000 kB")

    def test_rejects_oversize(self):
        with self.assertRaises(ValueError):
            assess_meminfo("x" * 16385)


if __name__ == "__main__":
    unittest.main()
