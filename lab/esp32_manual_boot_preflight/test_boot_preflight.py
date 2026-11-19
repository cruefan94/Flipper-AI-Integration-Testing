"""Public-safe synthetic fixtures for offline ESP32 preflight."""
import unittest
from boot_preflight import review

BASE = dict(chip="esp32", board_verified=True, voltage_verified_3v3=True,
            common_ground_verified=True, serial_adapter_3v3_logic=True,
            manual_boot_mode_confirmed=True, board_power_off_during_wiring=True)

class TestPreflight(unittest.TestCase):
    def test_wroom(self): self.assertTrue(review(BASE)["ready"])
    def test_s2(self): self.assertEqual(review(dict(BASE, chip="esp32s2"))["chip_family"], "ESP32-S2")
    def test_unknown(self): self.assertIn("unknown_chip", review(dict(BASE, chip="esp32c3"))["reasons"])
    def test_voltage(self): self.assertIn("logic_voltage_not_verified", review(dict(BASE, voltage_verified_3v3=False))["reasons"])
    def test_ground(self): self.assertIn("common_ground_not_verified", review(dict(BASE, common_ground_verified=False))["reasons"])
    def test_reset(self): self.assertIn("automatic_reset_not_allowed", review(dict(BASE, auto_reset_requested=True))["reasons"])
    def test_flash(self): self.assertIn("flashing_not_allowed", review(dict(BASE, flash_requested=True))["reasons"])
    def test_power(self): self.assertIn("power_off_not_confirmed", review(dict(BASE, board_power_off_during_wiring=False))["reasons"])
    def test_bad_input(self): self.assertFalse(review([])["ready"])
    def test_missing(self): self.assertFalse(review({})["ready"])

if __name__ == "__main__":
    unittest.main()
