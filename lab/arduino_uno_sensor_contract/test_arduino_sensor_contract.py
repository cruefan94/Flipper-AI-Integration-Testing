import unittest
from arduino_sensor_contract import validate

BASE = {"board": "arduino_uno_5v", "sensors": [{"pin": "A0", "direction": "input", "signal_max_v": 3.3}]}
def sample(**kwargs):
    return {"board": "arduino_uno_5v", "sensors": [dict(BASE["sensors"][0], **kwargs)]}

class ContractTests(unittest.TestCase):
    def test_safe(self): self.assertEqual(validate(BASE), [])
    def test_digital(self): self.assertEqual(validate(sample(pin=2)), [])
    def test_wrong_board(self): self.assertTrue(validate({"board":"esp32","sensors":[]}))
    def test_empty(self): self.assertTrue(validate({"board":"arduino_uno_5v","sensors":[]}))
    def test_uart(self): self.assertTrue(validate(sample(pin=0)))
    def test_duplicate(self): self.assertTrue(validate({"board":"arduino_uno_5v","sensors":[BASE["sensors"][0]]*2}))
    def test_overvoltage(self): self.assertTrue(validate(sample(signal_max_v=5.1)))
    def test_boolean_voltage(self): self.assertTrue(validate(sample(signal_max_v=True)))
    def test_output(self): self.assertTrue(validate(sample(direction="output")))
    def test_external_ground(self): self.assertTrue(validate(sample(externally_powered=True)))
    def test_level_shift(self): self.assertTrue(validate(sample(connected_to_3v3_device=True)))

if __name__ == "__main__":
    unittest.main()
