"""Synthetic tests only. No GPIO, serial, network, or radio access."""
import unittest
from i2c_evidence_gate import assess

BASE = dict(owner_approved=True, schematic_verified=True,
            common_ground_verified=True, power_rails_isolated=True,
            pullup_rails_verified=True, sda_pullup_v=3.3, scl_pullup_v=3.3,
            uno_5v_bus_connected=False, board_family="esp32-wroom")

class GateTests(unittest.TestCase):
    def test_valid_offline_evidence(self):
        self.assertEqual(assess(BASE), [])
    def test_missing_schematic(self):
        self.assertTrue(assess({**BASE, "schematic_verified": False}))
    def test_5v_sda(self):
        self.assertTrue(assess({**BASE, "sda_pullup_v": 5.0}))
    def test_5v_scl(self):
        self.assertTrue(assess({**BASE, "scl_pullup_v": 5.0}))
    def test_bool_voltage(self):
        self.assertTrue(assess({**BASE, "sda_pullup_v": True}))
    def test_unverified_5v_shifter(self):
        self.assertTrue(assess({**BASE, "uno_5v_bus_connected": True}))
    def test_verified_5v_shifter(self):
        x = {**BASE, "uno_5v_bus_connected": True,
             "bidirectional_level_shifter_verified": True,
             "shifter_direction_verified": True}
        self.assertEqual(assess(x), [])
    def test_unknown_board(self):
        self.assertTrue(assess({**BASE, "board_family": "other"}))
    def test_malformed(self):
        self.assertTrue(assess([]))
    def test_missing_owner_consent(self):
        self.assertTrue(assess({**BASE, "owner_approved": None}))

if __name__ == "__main__":
    unittest.main()
