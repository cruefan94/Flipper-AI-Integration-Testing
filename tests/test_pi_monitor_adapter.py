"""Offline tests for Pi collector-to-monitor bridge; no host /proc reads."""
import unittest
from raspberry_pi.pi_monitor_adapter import sample_pi_monitor

MEM = "MemTotal: 4096000 kB\nMemAvailable: 1024000 kB\n"
UP = "123.5 45.0"


class AdapterTests(unittest.TestCase):
    def test_no_consent_never_collects(self):
        def fail(**_):
            raise AssertionError("collector called")
        r = sample_pi_monitor(now_seconds=100, collector=fail)
        self.assertEqual(r["sources"]["pi"], "unknown")
        self.assertIsNone(r["pi_health"])

    def test_valid_injected_sample_is_fresh_not_verified(self):
        def reader(path):
            return MEM if str(path) == "/proc/meminfo" else UP
        r = sample_pi_monitor(consent=True, now_seconds=100, reader=reader)
        self.assertEqual(r["sources"]["pi"], "fresh_unverified")
        self.assertEqual(r["pi_health"]["memory_used_percent"], 75.0)
        self.assertFalse(r["hardware_verified"])
        self.assertFalse(r["cooling_control_authorized"])

    def test_invalid_sample_never_becomes_fresh(self):
        r = sample_pi_monitor(consent=True, now_seconds=100, reader=lambda _: "bad")
        self.assertEqual(r["sources"]["pi"], "unknown")

    def test_other_sources_remain_unknown(self):
        r = sample_pi_monitor(consent=True, now_seconds=100, reader=lambda _: "bad")
        for source in ("pironman_oled", "flipper", "esp32"):
            self.assertEqual(r["sources"][source], "unknown")

    def test_bad_clock_rejected_without_collecting(self):
        with self.assertRaises(ValueError):
            sample_pi_monitor(consent=True, now_seconds=float("nan"),
                              collector=lambda **_: self.fail("collected"))

    def test_collector_error_fails_closed(self):
        def fail(**_):
            raise OSError("offline")
        r = sample_pi_monitor(consent=True, now_seconds=100, collector=fail)
        self.assertEqual(r["sources"]["pi"], "unknown")


if __name__ == "__main__":
    unittest.main()
