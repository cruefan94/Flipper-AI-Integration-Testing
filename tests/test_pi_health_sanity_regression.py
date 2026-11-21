"""Offline regression coverage for Pi kernel-metric sanity checks; no hardware I/O."""
import math
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_health_readonly import parse_meminfo, snapshot


class MetricSanityTests(unittest.TestCase):
    def test_negative_total_memory_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: -1 kB\nMemAvailable: 0 kB\n")

    def test_available_exceeds_total_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: 100 kB\nMemAvailable: 101 kB\n")

    def test_negative_available_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: 100 kB\nMemAvailable: -1 kB\n")

    def test_negative_swap_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: 100 kB\nMemAvailable: 50 kB\nSwapTotal: -1 kB\n")

    def test_invalid_load_rejected(self):
        for invalid in ("-0.1", "nan", "inf", "-inf"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp)
                (p / "meminfo").write_text("MemTotal: 100 kB\nMemAvailable: 50 kB\n")
                (p / "loadavg").write_text(f"{invalid} 0.2 0.3\n")
                with self.assertRaises(ValueError):
                    snapshot(p, p / "missing")

    def test_zero_load_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "meminfo").write_text("MemTotal: 100 kB\nMemAvailable: 0 kB\n")
            (p / "loadavg").write_text("0 0 0\n")
            self.assertEqual(snapshot(p, p / "missing")["load_averages"], [0.0] * 3)


if __name__ == "__main__":
    unittest.main()
