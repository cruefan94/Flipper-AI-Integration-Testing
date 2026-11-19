"""Headless dashboard contract tests; never open Tk, touch GPIO, or call Pi hardware."""
import ast
import importlib
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / "raspberry_pi" / "pironman_readonly_dashboard.py"


class DashboardRefreshContractTests(unittest.TestCase):
    def test_source_parses_and_uses_ten_second_refresh(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertTrue(any(
            isinstance(call.func, ast.Attribute)
            and call.func.attr == "after"
            and call.args
            and isinstance(call.args[0], ast.Constant)
            and call.args[0].value == 10000
            for call in calls
        ))

    def load_module(self):
        try:
            return importlib.import_module("raspberry_pi.pironman_readonly_dashboard")
        except ImportError as exc:
            self.skipTest("Tkinter unavailable in test environment: " + str(exc))

    def make_dashboard(self, module):
        dashboard = module.Dashboard.__new__(module.Dashboard)
        dashboard.root = Mock()
        dashboard.snapshot = None
        dashboard.labels = {field: Mock() for field in module.FIELDS}
        dashboard.status = Mock()
        return dashboard

    def test_live_refresh_schedules_once_and_populates_all_fields(self):
        module = self.load_module()
        dashboard = self.make_dashboard(module)
        with patch.object(module, "read_live_snapshot", return_value={
            field: "not_probed" for field in module.FIELDS
        }) as read:
            dashboard.refresh()
        read.assert_called_once_with()
        for label in dashboard.labels.values():
            label.config.assert_called_once_with(text="not_probed")
        dashboard.root.after.assert_called_once_with(10000, dashboard.refresh)

    def test_read_failure_clears_old_values_and_keeps_refreshing(self):
        module = self.load_module()
        dashboard = self.make_dashboard(module)
        with patch.object(module, "read_live_snapshot", side_effect=OSError("offline")):
            dashboard.refresh()
        for label in dashboard.labels.values():
            label.config.assert_called_once_with(text="unavailable")
        dashboard.status.config.assert_called_once_with(text="Snapshot unavailable: OSError")
        dashboard.root.after.assert_called_once_with(10000, dashboard.refresh)

    def test_live_snapshot_uses_existing_read_only_monitor(self):
        module = self.load_module()
        with patch.object(module, "pi_snapshot", return_value={
            "temperature_c": 42.5, "uptime_s": 100,
            "memory_total_kib": 4194304, "memory_available_kib": 1048576,
            "pironman_oled": "not_probed", "flipper_usb": "not_probed",
            "esp32": "not_probed",
        }) as monitor:
            result = module.read_live_snapshot()
        monitor.assert_called_once_with()
        self.assertEqual(result["cpu_temp_c"], "42.5")
        self.assertEqual(result["memory_available_mb"], "1024.0")
        self.assertEqual(result["flipper_usb"], "not_probed")


if __name__ == "__main__":
    unittest.main()
