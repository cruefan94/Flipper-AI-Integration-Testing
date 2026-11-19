"""Synthetic tests: no serial devices opened, no real home inspected."""
import tempfile
import unittest
from pathlib import Path
from raspberry_pi.qflipper_readonly_usb_inventory import snapshot


class QFlipperInventoryTests(unittest.TestCase):
    def test_empty_environment(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            report = snapshot(root / "sys", root / "home")
            self.assertEqual(report["usb_serial_port_names"], [])
            self.assertFalse(report["qflipper_config_present"])
            self.assertFalse(report["device_connection_verified"])
            self.assertFalse(report["backup_verified"])

    def test_detects_only_supported_port_names_with_device(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tty = root / "sys"
            for name in ("ttyACM0", "ttyUSB2", "ttyS0", "ttyACM1"):
                (tty / name).mkdir(parents=True)
            (tty / "ttyACM0" / "device").mkdir()
            (tty / "ttyUSB2" / "device").mkdir()
            result = snapshot(tty, root / "home")
            self.assertEqual(result["usb_serial_port_names"], ["ttyACM0", "ttyUSB2"])

    def test_counts_log_filenames_without_reading_contents(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            logs = root / "home" / ".local" / "share" / "qFlipper"
            logs.mkdir(parents=True)
            (logs / "qFlipper-20261119.txt").write_text("private content")
            (logs / "other.txt").write_text("ignored")
            cfg = root / "home" / ".config" / "Flipper Devices Inc" / "qFlipper.ini"
            cfg.parent.mkdir(parents=True)
            cfg.write_text("private settings")
            result = snapshot(root / "sys", root / "home")
            self.assertEqual(result["qflipper_log_file_count"], 1)
            self.assertTrue(result["qflipper_config_present"])
            self.assertNotIn("private content", str(result))
            self.assertNotIn("private settings", str(result))


if __name__ == "__main__":
    unittest.main()
