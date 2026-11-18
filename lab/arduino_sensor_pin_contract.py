"""Offline-only Arduino/ESP32/Flipper GPIO wiring preflight.

This is a conservative, illustrative safety fixture, not an electrical certification.
Never opens hardware devices, drives GPIO, or authorizes flashing.
"""
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Endpoint:
    board: str
    pin: str
    direction: str  # input, output, ground
    logic_high_v: float
    max_input_v: float

ALLOWED = {"arduino_uno", "esp32_wroom", "esp32_s2", "flipper_zero"}
DIRECTIONS = {"input", "output", "ground"}

def check_link(source: Endpoint, sink: Endpoint, common_ground: bool, level_shifter: bool = False):
    """Return (safe_to_review, reasons); never implies hardware approval."""
    reasons = []
    if source.board not in ALLOWED or sink.board not in ALLOWED:
        reasons.append("unknown_board")
    if source.direction not in DIRECTIONS or sink.direction not in DIRECTIONS:
        reasons.append("unknown_direction")
    if not common_ground:
        reasons.append("missing_common_ground")
    if source.direction != "output" or sink.direction != "input":
        reasons.append("invalid_signal_direction")
    if source.logic_high_v <= 0 or sink.max_input_v <= 0:
        reasons.append("invalid_voltage")
    if source.logic_high_v > sink.max_input_v and not level_shifter:
        reasons.append("overvoltage_requires_level_shifter")
    if level_shifter:
        reasons.append("level_shifter_specification_unverified")
    return (not reasons, tuple(reasons))

class WiringContractTests(unittest.TestCase):
    def setUp(self):
        self.uno = Endpoint("arduino_uno", "D2", "output", 5.0, 5.0)
        self.esp = Endpoint("esp32_wroom", "GPIO16", "input", 3.3, 3.3)
    def test_reject_uno_to_esp_without_shifter(self):
        self.assertIn("overvoltage_requires_level_shifter", check_link(self.uno, self.esp, True)[1])
    def test_shifter_needs_spec_review(self):
        self.assertIn("level_shifter_specification_unverified", check_link(self.uno, self.esp, True, True)[1])
    def test_safe_nominal_esp_to_uno_input(self):
        uno_in = Endpoint("arduino_uno", "D3", "input", 5.0, 5.0)
        self.assertTrue(check_link(Endpoint("esp32_wroom", "GPIO17", "output", 3.3, 3.3), uno_in, True)[0])
    def test_missing_ground(self):
        self.assertIn("missing_common_ground", check_link(self.uno, self.esp, False)[1])
    def test_output_conflict(self):
        self.assertIn("invalid_signal_direction", check_link(self.uno, self.uno, True)[1])
    def test_unknown_board(self):
        self.assertIn("unknown_board", check_link(Endpoint("mystery", "D1", "output", 3.3, 3.3), self.esp, True)[1])
    def test_s2_3v3_sensor(self):
        sensor = Endpoint("esp32_s2", "GPIO4", "output", 3.3, 3.3)
        self.assertTrue(check_link(sensor, self.esp, True)[0])
    def test_flipper_overvoltage(self):
        flipper = Endpoint("flipper_zero", "GPIO", "input", 3.3, 3.3)
        self.assertIn("overvoltage_requires_level_shifter", check_link(self.uno, flipper, True)[1])

if __name__ == "__main__":
    unittest.main()
