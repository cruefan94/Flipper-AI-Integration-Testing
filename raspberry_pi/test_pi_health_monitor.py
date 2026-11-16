import tempfile
import unittest
from pathlib import Path
from pi_health_monitor import parse_meminfo, parse_temperature, snapshot

class HealthTests(unittest.TestCase):
    def test_memory(self):
        self.assertEqual(parse_meminfo("MemTotal: 4096000 kB\nMemAvailable: 1024000 kB\n")["available_mib"], 1000)

    def test_temperature(self):
        self.assertEqual(parse_temperature("52345\n"), 52.3)
        self.assertIsNone(parse_temperature("invalid"))

    def test_fixture_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in {
                "proc/meminfo": "MemTotal: 4096000 kB\nMemAvailable: 2048000 kB\n",
                "proc/uptime": "123.45 67.8",
                "proc/pressure/memory": "some avg10=0.50 avg60=0.30 total=100",
                "sys/class/thermal/thermal_zone0/temp": "50000",
            }.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value)
            reading = snapshot(root)
            self.assertEqual(reading["uptime_seconds"], 123)
            self.assertEqual(reading["cpu_temp_c"], 50.0)
            self.assertEqual(reading["memory_pressure_some_avg10"], 0.5)
            self.assertEqual(reading["memory"]["available_mib"], 2000)

    def test_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(snapshot(Path(directory))["cpu_temp_c"])

if __name__ == "__main__":
    unittest.main()
