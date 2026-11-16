"""Public-safe, hardware-free regression tests for ESP32 Pi serial preflight."""
import importlib.util
from pathlib import Path
import stat
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "raspberry_pi" / "esp32_preflight.py"
spec = importlib.util.spec_from_file_location("esp32_preflight", SOURCE)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class SerialSafetyTests(unittest.TestCase):
    def test_disappearing_device_fails_closed(self):
        with patch.object(preflight.Path, "stat", side_effect=FileNotFoundError):
            result = preflight.inspect_port("/dev/ttyUSB0")
        self.assertFalse(result["exists"])
        self.assertFalse(result["safe_to_flash"])
        self.assertEqual(result["inspection_error"], "FileNotFoundError")

    def test_permission_error_fails_closed(self):
        with patch.object(preflight.Path, "stat", side_effect=PermissionError):
            result = preflight.inspect_port("/dev/ttyACM0")
        self.assertFalse(result["safe_to_flash"])
        self.assertEqual(result["inspection_error"], "PermissionError")

    def test_regular_file_is_not_serial_port(self):
        with patch.object(preflight.Path, "stat", return_value=type("S", (), {"st_mode": stat.S_IFREG})()):
            result = preflight.inspect_port("/dev/ttyUSB0")
        self.assertFalse(result["character_device"])
        self.assertFalse(result["read_write_access"])
        self.assertFalse(result["safe_to_flash"])

    def test_character_device_is_still_not_flash_authorized(self):
        with patch.object(preflight.Path, "stat", return_value=type("S", (), {"st_mode": stat.S_IFCHR})()):
            with patch.object(preflight.os, "access", return_value=True):
                result = preflight.inspect_port("/dev/ttyUSB0")
        self.assertTrue(result["character_device"])
        self.assertTrue(result["read_write_access"])
        self.assertFalse(result["safe_to_flash"])


if __name__ == "__main__":
    unittest.main()
