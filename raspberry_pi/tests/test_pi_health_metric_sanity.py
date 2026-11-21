"""Offline regressions for malformed kernel metrics; no Pi hardware access."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pi_health_readonly import parse_meminfo, snapshot

GOOD = "MemTotal: 4096 kB\nMemAvailable: 2048 kB\nSwapTotal: 0 kB\nSwapFree: 0 kB\n"

class HealthSanityTests(unittest.TestCase):
    def test_valid_memory(self):
        self.assertEqual(parse_meminfo(GOOD)["MemAvailable"], 2048 * 1024)

    def test_negative_memory_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo(GOOD.replace("2048 kB", "-1 kB"))

    def test_available_above_total_rejected(self):
        with self.assertRaises(ValueError):
            parse_meminfo(GOOD.replace("2048 kB", "8192 kB"))

    def test_nonfinite_and_negative_load_rejected(self):
        for load in ("nan", "inf", "-1"):
            with self.subTest(load=load), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / "meminfo").write_text(GOOD, encoding="ascii")
                (root / "loadavg").write_text(f"{load} 0.1 0.2 1/10 99\n", encoding="ascii")
                with self.assertRaises(ValueError):
                    snapshot(proc=root, thermal=root / "missing")

    def test_valid_snapshot_missing_thermal(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "meminfo").write_text(GOOD, encoding="ascii")
            (root / "loadavg").write_text("0.1 0.2 0.3 1/10 99\n", encoding="ascii")
            result = snapshot(proc=root, thermal=root / "missing")
            self.assertIsNone(result["temperature_c"])
            self.assertFalse(result["hardware_control"])

if __name__ == "__main__":
    unittest.main()
