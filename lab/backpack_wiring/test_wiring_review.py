import unittest
from lab.backpack_wiring.wiring_review import review


class WiringReviewTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(review([]), [])

    def test_rejects_large_batch(self):
        self.assertEqual(review([{}] * 33), ["INVALID_EDGE_COLLECTION"])

    def test_rejects_invalid_input(self):
        self.assertEqual(review("wire"), ["INVALID_EDGE_COLLECTION"])

    def test_unknown_board(self):
        self.assertIn((0, "INVALID_BOARD_PAIR"), review([{"from_board": "unknown", "to_board": "esp32_s2"}]))

    def test_no_auto_approval(self):
        e = {"from_board": "flipper_zero", "to_board": "esp32_wroom",
             "signal": "uart", "direction": "a_to_b", "source_voltage": 3.3,
             "level_shift_verified": True, "common_ground_verified": True,
             "pinout_schematic_verified": True, "power_budget_verified": True}
        self.assertEqual(review([e]), [(0, "PHYSICAL_WIRING_REQUIRES_MANUAL_APPROVAL")])

    def test_five_volt(self):
        e = {"from_board": "arduino_uno", "to_board": "esp32_s2",
             "signal": "digital", "source_voltage": 5.0}
        self.assertIn((0, "FIVE_VOLT_SIGNAL_REQUIRES_ENGINEERING_REVIEW"), review([e]))

    def test_ground(self):
        e = {"from_board": "flipper_zero", "to_board": "esp32_s2",
             "signal": "ground", "direction": "passive"}
        self.assertEqual(review([e]), [])

    def test_ground_direction(self):
        e = {"from_board": "flipper_zero", "to_board": "esp32_s2",
             "signal": "ground", "direction": "a_to_b"}
        self.assertIn((0, "GROUND_DIRECTION_INVALID"), review([e]))

    def test_does_not_echo_sensitive_input(self):
        e = {"from_board": "arduino_uno", "to_board": "esp32_wroom",
             "signal": "uart", "pin": "PRIVATE_TOKEN=secret"}
        self.assertNotIn("secret", str(review([e])))


if __name__ == "__main__":
    unittest.main()
