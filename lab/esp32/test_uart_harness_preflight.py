"""Offline, public-safe classic ESP32 UART harness preflight. No device I/O.

Symbolic host signals are intentional: verify actual board labels and voltage
with a meter before connecting anything. Not an ESP32-S2 wiring specification.
"""
import unittest

EXPECTED = {'GND':'GND','U0RXD':'TX','U0TXD':'RX','EN':'RESET_3V3','GPIO0':'BOOT_3V3'}

def check_wiring(wires, supply_voltage, logic_voltage):
    if type(supply_voltage) not in (int,float) or type(logic_voltage) not in (int,float):
        raise ValueError('voltages must be numeric')
    if not 3.0 <= supply_voltage <= 3.6:
        raise ValueError('ESP32 supply outside 3.0-3.6 V')
    if not 0 <= logic_voltage <= 3.6:
        raise ValueError('GPIO logic above permitted maximum')
    if not isinstance(wires,dict) or wires != EXPECTED:
        raise ValueError('missing, unsafe or incorrectly crossed signals')
    return True

class TestWiring(unittest.TestCase):
    def setUp(self): self.w = dict(EXPECTED)
    def test_nominal(self): self.assertTrue(check_wiring(self.w,3.3,3.3))
    def test_supply_overvoltage(self):
        with self.assertRaises(ValueError): check_wiring(self.w,5,3.3)
    def test_logic_overvoltage(self):
        with self.assertRaises(ValueError): check_wiring(self.w,3.3,5)
    def test_uart_uncrossed(self):
        self.w['U0RXD']='RX'
        with self.assertRaises(ValueError): check_wiring(self.w,3.3,3.3)
    def test_missing_ground(self):
        del self.w['GND']
        with self.assertRaises(ValueError): check_wiring(self.w,3.3,3.3)
    def test_wrong_reset(self):
        self.w['EN']='RESET_5V'
        with self.assertRaises(ValueError): check_wiring(self.w,3.3,3.3)
    def test_bool_voltage(self):
        with self.assertRaises(ValueError): check_wiring(self.w,True,3.3)
    def test_extra_pin(self):
        self.w['GPIO2']='TX'
        with self.assertRaises(ValueError): check_wiring(self.w,3.3,3.3)

if __name__ == '__main__': unittest.main()
