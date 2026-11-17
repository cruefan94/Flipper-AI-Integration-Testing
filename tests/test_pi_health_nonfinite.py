"""Synthetic tests: nonfinite and out-of-range Pi health metrics are unavailable."""
import tempfile
import unittest
from pathlib import Path

from raspberry_pi.pi_health_monitor import snapshot


class PiHealthNonfiniteTests(unittest.TestCase):
    def test_uptime_rejects_invalid_float_values(self):
        for value in ("nan", "inf", "-inf", "-1", "not-a-number"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "proc" / "uptime"
                path.parent.mkdir(parents=True)
                path.write_text(value + " 0\n", encoding="utf-8")
                self.assertIsNone(snapshot(Path(tmp))["uptime_seconds"])

    def test_memory_pressure_rejects_nonfinite_and_out_of_range(self):
        for value in ("nan", "inf", "-inf", "-1", "101", "garbage"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "proc" / "pressure" / "memory"
                path.parent.mkdir(parents=True)
                path.write_text("some avg10=" + value + " avg60=0 avg300=0 total=0\n", encoding="utf-8")
                self.assertIsNone(snapshot(Path(tmp))["memory_pressure_some_avg10"])

    def test_valid_boundary_metrics(self):
        for value in ("0", "100"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                for relative, data in (("proc/uptime", "0.5 0\n"),
                                       ("proc/pressure/memory", "some avg10=" + value + " avg60=0\n")):
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(data, encoding="utf-8")
                result = snapshot(root)
                self.assertEqual(result["uptime_seconds"], 0)
                self.assertEqual(result["memory_pressure_some_avg10"], float(value))


if __name__ == "__main__":
    unittest.main()
