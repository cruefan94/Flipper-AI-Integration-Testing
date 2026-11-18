"""Public-safe, offline Arduino/ESP32/Flipper GPIO connection contract tests.

No device access, serial ports, radio, flashing, or private project data.
"""
import unittest

VOLTAGES = {"uno": 5.0, "esp32-wroom": 3.3, "esp32-s2": 3.3, "flipper": 3.3, "pi4": 3.3}


def check_link(source, target, source_mode="output", target_mode="input", common_ground=True, level_shifter=False):
    if source not in VOLTAGES or target not in VOLTAGES:
        return "BLOCK:UNKNOWN_BOARD"
    if not common_ground:
        return "BLOCK:NO_COMMON_GROUND"
    if source_mode != "output" or target_mode != "input":
        return "BLOCK:DIRECTION"
    if VOLTAGES[source] > VOLTAGES[target]:
        return "REVIEW:LEVEL_SHIFTER" if level_shifter else "BLOCK:OVERVOLTAGE"
    if VOLTAGES[source] < VOLTAGES[target]:
        return "REVIEW:LOGIC_HIGH_THRESHOLD"
    return "REVIEW:PIN_SPECIFICATIONS"


class TestGpioContracts(unittest.TestCase):
    def test_uno_to_esp32_requires_shifter(self):
        self.assertEqual(check_link("uno", "esp32-wroom"), "BLOCK:OVERVOLTAGE")

    def test_uno_to_flipper_requires_shifter(self):
        self.assertEqual(check_link("uno", "flipper"), "BLOCK:OVERVOLTAGE")

    def test_uno_to_pi_requires_shifter(self):
        self.assertEqual(check_link("uno", "pi4"), "BLOCK:OVERVOLTAGE")

    def test_shifter_does_not_automatically_approve(self):
        self.assertEqual(check_link("uno", "esp32-s2", level_shifter=True), "REVIEW:LEVEL_SHIFTER")

    def test_esp32_to_uno_needs_input_threshold_review(self):
        self.assertEqual(check_link("esp32-wroom", "uno"), "REVIEW:LOGIC_HIGH_THRESHOLD")

    def test_same_voltage_requires_pin_review(self):
        self.assertEqual(check_link("esp32-s2", "flipper"), "REVIEW:PIN_SPECIFICATIONS")

    def test_missing_ground_blocks(self):
        self.assertEqual(check_link("esp32-wroom", "flipper", common_ground=False), "BLOCK:NO_COMMON_GROUND")

    def test_two_outputs_block(self):
        self.assertEqual(check_link("uno", "esp32-wroom", target_mode="output"), "BLOCK:DIRECTION")

    def test_unknown_board_blocks(self):
        self.assertEqual(check_link("sensor-unknown", "flipper"), "BLOCK:UNKNOWN_BOARD")

    def test_input_to_input_blocks(self):
        self.assertEqual(check_link("esp32-s2", "flipper", source_mode="input"), "BLOCK:DIRECTION")


if __name__ == "__main__":
    unittest.main()
