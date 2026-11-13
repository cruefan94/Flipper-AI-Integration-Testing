"""Standalone policy tests. No Flipper hardware and no Android APK required."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from battery_optimizer import Analysis, Profile, Telemetry, analyze, to_public_dict


class BatteryOptimizerTests(unittest.TestCase):
    def t(self, **overrides):
        args = dict(battery_pct=67, charging=False, ble_connected=True)
        args.update(overrides)
        return Telemetry(**args)

    def keys(self, result):
        return {s.key for s in result.suggestions}

    def test_default_is_read_only(self):
        a = analyze(self.t())
        self.assertEqual(a.status, "advice_only")
        self.assertFalse(a.can_apply_changes)
        self.assertEqual(a.profile, Profile.BALANCED)
        self.assertTrue(all(s.approval_required for s in a.suggestions))

    def test_ble_is_preserved(self):
        self.assertIn("preserve_ble", self.keys(analyze(self.t())))
        self.assertNotIn("no_forced_reconnect", self.keys(analyze(self.t())))

    def test_no_reconnect_for_disconnected_flipper(self):
        a = analyze(self.t(ble_connected=False))
        self.assertIn("no_forced_reconnect", self.keys(a))
        self.assertGreaterEqual(a.suggested_poll_seconds, 900)

    def test_stale_telemetry_blocks_optimization(self):
        a = analyze(self.t(sample_age_seconds=121, battery_pct=5))
        self.assertEqual(a.status, "stale_telemetry")
        self.assertEqual(self.keys(a), {"refresh_when_available"})

    def test_recent_boundary_is_accepted(self):
        self.assertEqual(analyze(self.t(sample_age_seconds=120)).status, "advice_only")

    def test_active_operation_is_not_interrupted(self):
        a = analyze(self.t(battery_pct=17, idle_seconds=400,
                           active_operations=("nfc_read",)))
        self.assertIn("preserve_active_task", self.keys(a))
        self.assertNotIn("idle_backlight", self.keys(a))
        self.assertNotIn("optional_accessory_standby", self.keys(a))

    def test_eco_suggests_idle_accessory_standby_only(self):
        a = analyze(self.t(idle_seconds=200), Profile.ECO)
        self.assertIn("idle_backlight", self.keys(a))
        self.assertIn("optional_accessory_standby", self.keys(a))
        self.assertEqual(a.suggested_poll_seconds, 900)

    def test_charging_avoids_low_battery_warning(self):
        a = analyze(self.t(battery_pct=9, charging=True), Profile.ECO)
        self.assertNotIn("low_battery", self.keys(a))
        self.assertNotIn("optional_accessory_standby", self.keys(a))

    def test_critical_battery_warns_even_performance(self):
        a = analyze(self.t(battery_pct=12), Profile.PERFORMANCE)
        self.assertIn("low_battery", self.keys(a))
        self.assertNotIn("prefer_eco", self.keys(a))

    def test_warm_battery_is_warning_not_power_write(self):
        a = analyze(self.t(temperature_c=46))
        self.assertIn("elevated_temperature", self.keys(a))
        self.assertFalse(a.can_apply_changes)

    def test_invalid_percentage(self):
        for pct in (-1, 101, float("nan"), float("inf")):
            with self.subTest(pct=pct), self.assertRaises(ValueError):
                self.t(battery_pct=pct)

    def test_invalid_elapsed(self):
        with self.assertRaises(ValueError):
            self.t(sample_age_seconds=-1)
        with self.assertRaises(ValueError):
            self.t(idle_seconds=-1)

    def test_invalid_temperature(self):
        with self.assertRaises(ValueError):
            self.t(temperature_c=float("nan"))

    def test_invalid_activity_input(self):
        with self.assertRaises(ValueError):
            self.t(active_operations=("nfc_read", ""))
        with self.assertRaises(ValueError):
            self.t(active_operations="nfc_read")

    def test_serialized_output_contains_no_device_commands(self):
        payload = to_public_dict(analyze(self.t(battery_pct=10)))
        self.assertFalse(payload["can_apply_changes"])
        self.assertEqual(set(payload), {
            "profile", "status", "suggested_poll_seconds",
            "can_apply_changes", "suggestions",
        })
        self.assertTrue(all(x["approval_required"] for x in payload["suggestions"]))


if __name__ == "__main__":
    unittest.main()
