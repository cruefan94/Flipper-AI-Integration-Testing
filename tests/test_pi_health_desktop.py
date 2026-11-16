"""Offline formatting tests for the read-only Pi desktop viewer."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "raspberry_pi"))
from pi_health_desktop import format_snapshot


class DesktopFormattingTests(unittest.TestCase):
    def test_known_values(self):
        values = format_snapshot({
            "cpu_temp_c": 42.5,
            "memory": {"total_mib": 4096, "available_mib": 2048,
                       "swap_total_mib": 512, "swap_free_mib": 256},
            "uptime_seconds": 7260,
            "memory_pressure_some_avg10": 1.25,
        })
        self.assertEqual(values["CPU temperature"], "42.5 °C")
        self.assertEqual(values["Available RAM"], "2048 / 4096 MiB")
        self.assertEqual(values["Uptime"], "2h 1m")
        self.assertEqual(values["Memory pressure (10 s)"], "1.25%")

    def test_missing_values(self):
        values = format_snapshot({})
        self.assertEqual(values["CPU temperature"], "Unavailable")
        self.assertEqual(values["Uptime"], "Unavailable")


if __name__ == "__main__":
    unittest.main()
