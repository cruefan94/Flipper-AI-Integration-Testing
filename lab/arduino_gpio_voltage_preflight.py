"""Offline Arduino Uno / ESP32 / Flipper GPIO voltage-domain preflight.

Synthetic design records only. Never touches hardware.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Connection:
    source: str
    destination: str
    source_high_v: float
    destination_max_v: float
    common_ground: bool
    level_shifter_verified: bool = False
    output_to_output: bool = False
    power_pin: bool = False

def assess(c: Connection) -> tuple[bool, str]:
    if c.source not in {"uno", "esp32", "flipper", "sensor"} or c.destination not in {"uno", "esp32", "flipper", "sensor"}:
        return False, "unknown_device"
    if not c.common_ground:
        return False, "ground_unverified"
    if c.output_to_output:
        return False, "output_contention"
    if c.power_pin:
        return False, "power_path_requires_separate_review"
    if not (0 <= c.source_high_v <= 5.5 and 0 < c.destination_max_v <= 5.5):
        return False, "invalid_voltage"
    if c.source_high_v > c.destination_max_v and not c.level_shifter_verified:
        return False, "overvoltage"
    return True, "logic_voltage_preflight_only"

if __name__ == "__main__":
    import unittest
    class TestGPIO(unittest.TestCase):
        def test_uno_to_esp32_rejected(self):
            self.assertEqual(assess(Connection("uno", "esp32", 5, 3.3, True))[1], "overvoltage")
        def test_verified_shifter(self):
            self.assertTrue(assess(Connection("uno", "esp32", 5, 3.3, True, True))[0])
        def test_missing_ground(self):
            self.assertFalse(assess(Connection("esp32", "uno", 3.3, 5, False))[0])
        def test_output_contention(self):
            self.assertEqual(assess(Connection("uno", "esp32", 5, 3.3, True, True, True))[1], "output_contention")
        def test_power_path(self):
            self.assertFalse(assess(Connection("uno", "esp32", 5, 3.3, True, True, False, True))[0])
        def test_invalid_voltage(self):
            self.assertFalse(assess(Connection("sensor", "uno", -1, 5, True))[0])
        def test_safe_logic(self):
            self.assertTrue(assess(Connection("esp32", "uno", 3.3, 5, True))[0])
        def test_unknown_device(self):
            self.assertFalse(assess(Connection("mystery", "uno", 3.3, 5, True))[0])
    unittest.main()
