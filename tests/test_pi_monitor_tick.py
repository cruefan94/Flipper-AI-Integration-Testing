"""Offline tests: no /proc, hardware, timers, network, or device I/O."""
import unittest

from raspberry_pi.pi_monitor_tick import monitor_tick


class MonitorTickTests(unittest.TestCase):
    def test_no_consent_never_calls_sampler(self):
        result = monitor_tick(consent=False, now_seconds=0,
                              sampler=lambda **_: self.fail("sampled"))
        self.assertEqual(result["reason"], "not_authorized")
        self.assertIsNone(result["next_last_sample_at"])

    def test_first_opt_in_sample(self):
        calls = []
        def sample(**kwargs):
            calls.append(kwargs)
            return {"sources": {"pi": "fresh_unverified"}, "hardware_verified": False}
        result = monitor_tick(consent=True, now_seconds=2, sampler=sample)
        self.assertTrue(result["sampled"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["next_last_sample_at"], 2)

    def test_interval_is_strict(self):
        def fail(**_):
            self.fail("sampled too early")
        result = monitor_tick(consent=True, now_seconds=19.99, last_sample_at=10, sampler=fail)
        self.assertEqual(result["reason"], "interval_pending")

    def test_ten_second_boundary_samples(self):
        result = monitor_tick(consent=True, now_seconds=20, last_sample_at=10,
                              sampler=lambda **_: {"sources": {}})
        self.assertTrue(result["sampled"])

    def test_clock_regression_resets_without_sample(self):
        result = monitor_tick(consent=True, now_seconds=5, last_sample_at=8,
                              sampler=lambda **_: self.fail("sampled"))
        self.assertEqual(result["reason"], "clock_regressed")
        self.assertIsNone(result["next_last_sample_at"])

    def test_invalid_timestamps_rejected(self):
        for clock in (float("nan"), float("inf"), -1, True, "12"):
            with self.subTest(clock=clock), self.assertRaises(ValueError):
                monitor_tick(consent=True, now_seconds=clock)

    def test_sampler_failure_is_unknown_not_healthy(self):
        def fail(**_):
            raise OSError("offline")
        result = monitor_tick(consent=True, now_seconds=10, sampler=fail)
        self.assertEqual(result["monitor"]["sources"]["pi"], "unknown")
        self.assertFalse(result["monitor"]["cooling_control_authorized"])

    def test_revoked_consent_discards_previous_timestamp(self):
        result = monitor_tick(consent=False, now_seconds=20, last_sample_at=10)
        self.assertIsNone(result["next_last_sample_at"])


if __name__ == "__main__":
    unittest.main()
