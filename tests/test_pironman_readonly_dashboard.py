"""Offline tests for Pironman snapshot viewer; no GUI or Pi hardware needed."""
import json
import tempfile
import unittest
from pathlib import Path
from raspberry_pi.pironman_readonly_dashboard import normalize, read_snapshot

class DashboardTests(unittest.TestCase):
    def test_missing_hardware_not_probed(self):
        result = normalize({"cpu_temp_c": 44.5})
        self.assertEqual(result["pironman_oled"], "not_probed")
        self.assertEqual(result["cpu_temp_c"], "44.5")

    def test_non_object_rejected(self):
        with self.assertRaises(ValueError):
            normalize([])

    def test_nested_values_not_displayed(self):
        self.assertEqual(normalize({"flipper_usb": {"secret": "private"}})["flipper_usb"], "not_probed")

    def test_local_snapshot_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps({"uptime_seconds": 123}), encoding="utf-8")
            self.assertEqual(read_snapshot(path)["uptime_seconds"], "123")

    def test_oversized_snapshot_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(" " * 65537)
            with self.assertRaises(ValueError):
                read_snapshot(path)

if __name__ == "__main__":
    unittest.main()
