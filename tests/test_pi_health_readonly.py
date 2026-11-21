"""Synthetic tests only: no actual Pi device or hardware accessed."""
import tempfile
import unittest
from pathlib import Path
from raspberry_pi.pi_health_readonly import parse_meminfo, snapshot

class HealthTests(unittest.TestCase):
    def test_memory_bytes(self):
        self.assertEqual(parse_meminfo("MemTotal: 4096 kB\nMemAvailable: 1024 kB\n")["MemTotal"], 4194304)

    def test_missing_memory(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: 10 kB\n")

    def test_wrong_units(self):
        with self.assertRaises(ValueError):
            parse_meminfo("MemTotal: 10 MB\nMemAvailable: 4 kB\n")

    def test_snapshot_no_thermal(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "meminfo").write_text("MemTotal: 4000 kB\nMemAvailable: 2000 kB\n")
            (p / "loadavg").write_text("0.10 0.20 0.30 1/99 123\n")
            result = snapshot(p, p / "missing")
            self.assertEqual(result["load_averages"], [0.1, 0.2, 0.3])
            self.assertIsNone(result["temperature_c"])
            self.assertFalse(result["hardware_control"])

    def test_temperature(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "meminfo").write_text("MemTotal: 4000 kB\nMemAvailable: 2000 kB\n")
            (p / "loadavg").write_text("0.10 0.20 0.30\n")
            (p / "temp").write_text("42500\n")
            self.assertEqual(snapshot(p, p / "temp")["temperature_c"], 42.5)

if __name__ == "__main__":
    unittest.main()
