"""Offline synthetic tests for 10-second monitor freshness policy."""
import unittest
from raspberry_pi.pi_monitor_freshness import classify_snapshot


class MonitorFreshnessTests(unittest.TestCase):
    def test_missing_sources_are_unknown(self):
        result = classify_snapshot({}, 100)
        self.assertEqual(set(result["sources"].values()), {"unknown"})
        self.assertFalse(result["hardware_verified"])

    def test_exact_boundary_and_stale(self):
        result = classify_snapshot({
            "pi": {"observed_at": 90, "connected": True},
            "flipper": {"observed_at": 89.99, "connected": True},
        }, 100)
        self.assertEqual(result["sources"]["pi"], "fresh_unverified")
        self.assertEqual(result["sources"]["flipper"], "stale")
        self.assertFalse(result["device_commands_authorized"])

    def test_future_invalid_and_bool_timestamp(self):
        result = classify_snapshot({
            "esp32": {"observed_at": 101},
            "pironman_oled": {"observed_at": True},
        }, 100)
        self.assertEqual(result["sources"]["esp32"], "invalid_future")
        self.assertEqual(result["sources"]["pironman_oled"], "unknown")
        self.assertFalse(result["cooling_control_authorized"])

    def test_nonfinite_clock_rejected(self):
        with self.assertRaises(ValueError):
            classify_snapshot({}, float("nan"))


if __name__ == "__main__":
    unittest.main()
