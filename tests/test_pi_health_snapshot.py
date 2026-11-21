"""Synthetic tests; never access the Pi or host /proc."""
import unittest
from raspberry_pi.pi_health_snapshot import parse_pi_health


class HealthParserTests(unittest.TestCase):
    def test_valid_sample(self):
        data = parse_pi_health("MemTotal: 4096000 kB\nMemAvailable: 1024000 kB\n", "123.5 45.0")
        self.assertEqual(data["status"], "parsed_unverified")
        self.assertEqual(data["memory_used_percent"], 75.0)
        self.assertFalse(data["hardware_verified"])
        self.assertFalse(data["cooling_control_authorized"])

    def test_missing_fields(self):
        self.assertEqual(parse_pi_health("MemTotal: 4096 kB", "10 5")["status"], "unknown")

    def test_invalid_memory(self):
        self.assertEqual(parse_pi_health("MemTotal: 100 kB\nMemAvailable: 101 kB", "10 5")["status"], "unknown")

    def test_nonfinite_uptime(self):
        self.assertEqual(parse_pi_health("MemTotal: 100 kB\nMemAvailable: 50 kB", "nan 5")["status"], "unknown")

    def test_duplicate_memory(self):
        self.assertEqual(parse_pi_health("MemTotal: 100 kB\nMemTotal: 100 kB\nMemAvailable: 50 kB", "10 5")["status"], "unknown")


if __name__ == "__main__":
    unittest.main()
