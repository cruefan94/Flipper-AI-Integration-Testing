"""Regression tests for missing Pi memory readings (no Tk window required)."""
import unittest

try:
    from raspberry_pi.pi_health_desktop import format_snapshot
except ImportError:
    from pi_health_desktop import format_snapshot


class MissingMemoryTests(unittest.TestCase):
    def test_missing_meminfo_is_not_reported_as_zero(self):
        values = format_snapshot({"memory": {}})
        self.assertEqual(values["Available RAM"], "Unavailable")
        self.assertEqual(values["Free swap"], "Unavailable")

    def test_actual_zero_swap_is_unavailable_without_total(self):
        values = format_snapshot({"memory": {"swap_free_mib": 0, "swap_total_mib": 0}})
        self.assertEqual(values["Free swap"], "Unavailable")

    def test_real_values_are_preserved(self):
        values = format_snapshot({"memory": {"available_mib": 512, "total_mib": 4096,
                                              "swap_free_mib": 0, "swap_total_mib": 1024}})
        self.assertEqual(values["Available RAM"], "512 / 4096 MiB")
        self.assertEqual(values["Free swap"], "0 / 1024 MiB")


if __name__ == "__main__":
    unittest.main()
