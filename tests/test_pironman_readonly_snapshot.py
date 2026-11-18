"""Offline regression tests for the first-generation Pironman read-only parser.

Run: python3 -m unittest discover -s tests -p 'test_pironman_readonly_snapshot.py' -v
No GPIO, subprocess, system service or real device required.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "raspberry_pi" / "pironman_readonly_snapshot.py"
spec = importlib.util.spec_from_file_location("pironman_readonly_snapshot", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VALID = """temp_unit=C
fan_temp=40
screen_always_on=True
screen_off_time=60
rgb_switch=True
rgb_style=colorful
rgb_color=4682B4
rgb_blink_speed=100
rgb_pwm_freq=1600
"""

class PironmanSnapshotTests(unittest.TestCase):
    def test_owner_observed_configuration(self):
        result = module.parse_config(VALID)
        self.assertEqual(result["fan_temp"], 40)
        self.assertEqual(result["rgb_color"], "4682B4")
        self.assertEqual(len(result), 9)

    def test_unknown_keys_ignored_without_execution(self):
        self.assertEqual(module.parse_config("unknown=$(touch /tmp/should-not-exist)"), {})

    def test_invalid_values_and_duplicates_rejected(self):
        for value in ("fan_temp=29", "fan_temp=81", "rgb_color=GGGGGG",
                      "rgb_style=invalid", "rgb_switch=1",
                      "fan_temp=40\nfan_temp=41"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.parse_config(value)

    def test_file_snapshot_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.txt"
            path.write_text(VALID, encoding="utf-8")
            before = path.read_bytes()
            self.assertEqual(module.snapshot(path)["fan_temp"], 40)
            self.assertEqual(path.read_bytes(), before)

    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "config.txt"
            target.write_text(VALID, encoding="utf-8")
            link = Path(directory) / "link.txt"
            link.symlink_to(target)
            with self.assertRaises(ValueError):
                module.snapshot(link)

    def test_oversize_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.txt"
            path.write_text("x" * 65537, encoding="utf-8")
            with self.assertRaises(ValueError):
                module.snapshot(path)

if __name__ == "__main__":
    unittest.main()
