"""Contract tests between the existing Pi monitor and desktop view."""
import unittest
from unittest.mock import patch
from raspberry_pi.pironman_readonly_dashboard import normalize, read_live_snapshot


class MonitorDashboardContractTests(unittest.TestCase):
    def test_monitor_field_aliases(self):
        actual = normalize({"temperature_c": 45.2, "uptime_s": 75,
                            "memory_total_kib": 4194304, "memory_available_kib": 1048576})
        self.assertEqual(actual["cpu_temp_c"], "45.2")
        self.assertEqual(actual["uptime_seconds"], "75")
        self.assertEqual(actual["memory_total_mb"], "4096.0")
        self.assertEqual(actual["memory_available_mb"], "1024.0")

    def test_unknown_hardware_not_claimed(self):
        actual = normalize({"temperature_c": None, "pironman_oled": "not_probed"})
        self.assertEqual(actual["cpu_temp_c"], "not_probed")
        self.assertEqual(actual["flipper_usb"], "not_probed")

    def test_bad_memory_does_not_crash(self):
        self.assertEqual(normalize({"memory_total_kib": "private"})["memory_total_mb"], "not_probed")
        self.assertEqual(normalize({"memory_total_kib": -5})["memory_total_mb"], "not_probed")

    def test_direct_monitor_integration(self):
        with patch("raspberry_pi.pironman_readonly_dashboard.pi_snapshot",
                   return_value={"temperature_c": 42, "uptime_s": 123}):
            self.assertEqual(read_live_snapshot()["cpu_temp_c"], "42")


if __name__ == "__main__":
    unittest.main()
