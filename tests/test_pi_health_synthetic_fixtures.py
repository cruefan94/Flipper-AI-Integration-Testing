"""Hardware-free Pi OS health snapshot regression tests.

All filesystem inputs are temporary synthetic procfs/sysfs fixtures.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from raspberry_pi.pi_health_monitor import parse_temperature, snapshot


class PiHealthFixtureTests(unittest.TestCase):
    def test_complete_synthetic_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative, data in {
                "proc/uptime": "1234.50 2000.00\n",
                "proc/meminfo": (
                    "MemTotal: 4194304 kB\nMemAvailable: 2097152 kB\n"
                    "SwapTotal: 1048576 kB\nSwapFree: 524288 kB\n"
                ),
                "proc/pressure/memory": (
                    "some avg10=1.25 avg60=0.50 avg300=0.20 total=10\n"
                    "full avg10=0.00 avg60=0.00 avg300=0.00 total=0\n"
                ),
                "sys/class/thermal/thermal_zone0/temp": "40500\n",
            }.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(data, encoding="utf-8")
            result = snapshot(root)
        self.assertEqual(result["uptime_seconds"], 1234)
        self.assertEqual(result["cpu_temp_c"], 40.5)
        self.assertEqual(result["memory"]["total_mib"], 4096)
        self.assertEqual(result["memory"]["available_mib"], 2048)
        self.assertEqual(result["memory"]["swap_free_mib"], 512)
        self.assertEqual(result["memory_pressure_some_avg10"], 1.25)

    def test_missing_files_fail_closed_without_hardware(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = snapshot(Path(tmp))
        self.assertIsNone(result["cpu_temp_c"])
        self.assertIsNone(result["uptime_seconds"])
        self.assertIsNone(result["memory_pressure_some_avg10"])
        self.assertEqual(result["memory"]["total_mib"], 0)

    def test_malformed_uptime_and_pressure_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "proc/pressure").mkdir(parents=True)
            (root / "proc/uptime").write_text("not-a-number", encoding="utf-8")
            (root / "proc/pressure/memory").write_text(
                "some avg10=not-a-number avg60=0.1\n", encoding="utf-8"
            )
            result = snapshot(root)
        self.assertIsNone(result["uptime_seconds"])
        self.assertIsNone(result["memory_pressure_some_avg10"])

    def test_temperature_bounds_and_invalid_values(self):
        for raw, expected in [
            ("40500", 40.5), ("125000", 125.0),
            ("-20000", -20.0), ("125001", None),
            ("-20001", None), ("garbage", None), (None, None),
        ]:
            with self.subTest(raw=raw):
                self.assertEqual(parse_temperature(raw), expected)

    def test_snapshot_never_reads_real_procfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("raspberry_pi.pi_health_monitor.read_text", return_value=None) as read:
                snapshot(root)
            self.assertGreaterEqual(read.call_count, 4)
            for call in read.call_args_list:
                self.assertTrue(call.args[0].is_relative_to(root))


if __name__ == "__main__":
    unittest.main()
