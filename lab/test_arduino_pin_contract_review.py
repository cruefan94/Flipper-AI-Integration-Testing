import unittest
from arduino_pin_contract_review import Pin, review_connection

def pin(board, voltage, direction, verified=True):
    return Pin(board, "fixture", voltage, direction, verified)

class PinContractTests(unittest.TestCase):
    def test_uno_five_volts_to_esp32_rejected(self):
        result = review_connection(pin("arduino_uno", 5, "out"), pin("esp32_wroom", 3.3, "in"))
        self.assertIn("overvoltage_without_verified_level_shifter", result["reasons"])
        self.assertFalse(result["hardware_authorized"])

    def test_verified_shifter_only_passes_static_review(self):
        result = review_connection(pin("arduino_uno", 5, "out"), pin("esp32_s2", 3.3, "in"), True)
        self.assertTrue(result["static_review_pass"])
        self.assertFalse(result["hardware_authorized"])

    def test_unverified_pin_rejected(self):
        result = review_connection(pin("esp32_wroom", 3.3, "out", False), pin("flipper_zero", 3.3, "in"))
        self.assertIn("pin_identity_unverified", result["reasons"])

    def test_unknown_voltage_rejected(self):
        result = review_connection(pin("arduino_uno", None, "out"), pin("flipper_zero", 3.3, "in"))
        self.assertIn("voltage_unknown", result["reasons"])

    def test_power_rail_rejected(self):
        result = review_connection(pin("arduino_uno", 5, "power"), pin("esp32_wroom", 3.3, "in"), True)
        self.assertIn("power_connection_requires_separate_review", result["reasons"])

    def test_bidirectional_needs_review(self):
        result = review_connection(pin("esp32_wroom", 3.3, "bidirectional"), pin("esp32_s2", 3.3, "bidirectional"))
        self.assertIn("bidirectional_interface_requires_review", result["reasons"])

    def test_unknown_board_rejected(self):
        result = review_connection(pin("unknown", 3.3, "out"), pin("flipper_zero", 3.3, "in"))
        self.assertIn("unknown_board", result["reasons"])

if __name__ == "__main__":
    unittest.main()
