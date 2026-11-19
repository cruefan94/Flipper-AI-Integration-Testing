import unittest
from backpack_power_preflight import Module, preflight

class PowerPreflightTests(unittest.TestCase):
    def setUp(self):
        self.esp = Module("esp32_wroom", 5.0, 3.3, 250)
    def check(self, modules, expected, **kwargs):
        self.assertEqual(preflight(modules, **kwargs)[0], expected)
    def test_safe_external_review(self):
        self.check([self.esp], True, common_ground_confirmed=True)
    def test_missing_ground(self):
        self.check([self.esp], False)
    def test_flipper_power_not_assumed(self):
        self.check([Module("esp32_s2",3.3,3.3,100,"flipper_3v3")],False,common_ground_confirmed=True)
    def test_five_volt_gpio(self):
        self.check([Module("esp32_wroom",5,5,100)],False,common_ground_confirmed=True)
    def test_uno_requires_level_shift(self):
        self.check([Module("arduino_uno",5,5,50)],False,common_ground_confirmed=True)
    def test_uno_with_level_shift_review(self):
        self.check([Module("arduino_uno",5,5,50)],True,common_ground_confirmed=True,level_shifters_confirmed=True)
    def test_unknown_board(self):
        self.check([Module("unknown",5,3.3,50)],False,common_ground_confirmed=True)
    def test_bad_current(self):
        self.check([Module("esp32_s2",5,3.3,-1)],False,common_ground_confirmed=True)
    def test_empty(self):
        self.check([],False,common_ground_confirmed=True)
    def test_too_many(self):
        self.check([self.esp]*9,False,common_ground_confirmed=True)

if __name__ == "__main__":
    unittest.main()
