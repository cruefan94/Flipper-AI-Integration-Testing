"""Public-safe offline regression fixtures for Arduino Uno GPIO reviewer."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("gpio", Path(__file__).resolve().parents[1] / "lab" / "arduino_uno_gpio_review.py")
gpio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gpio)

def sample():
    return {"board": "arduino-uno-r3", "mode": "offline-review",
            "devices": [{"kind": "digital-input", "pin": 2, "signal_voltage": 3.3, "common_ground_verified": True}]}

class TestUnoGPIO(unittest.TestCase):
    def test_valid(self): self.assertEqual(gpio.review(sample()), [])
    def test_unsupported_board(self):
        p=sample(); p["board"]="esp32"; self.assertTrue(gpio.review(p))
    def test_no_hardware_mode(self):
        p=sample(); p["mode"]="flash"; self.assertTrue(gpio.review(p))
    def test_serial_pin_reserved(self):
        p=sample(); p["devices"][0]["pin"]=0; self.assertTrue(gpio.review(p))
    def test_duplicate_pin(self):
        p=sample(); p["devices"].append(dict(p["devices"][0])); self.assertTrue(gpio.review(p))
    def test_overvoltage(self):
        p=sample(); p["devices"][0]["signal_voltage"]=5.1; self.assertTrue(gpio.review(p))
    def test_negative_voltage(self):
        p=sample(); p["devices"][0]["signal_voltage"]=-1; self.assertTrue(gpio.review(p))
    def test_nan(self):
        p=sample(); p["devices"][0]["signal_voltage"]=float("nan"); self.assertTrue(gpio.review(p))
    def test_boolean_pin(self):
        p=sample(); p["devices"][0]["pin"]=True; self.assertTrue(gpio.review(p))
    def test_missing_ground(self):
        p=sample(); p["devices"][0]["common_ground_verified"]=False; self.assertTrue(gpio.review(p))
    def test_analog_input(self):
        p=sample(); p["devices"][0]["kind"]="analog-input"; p["devices"][0]["pin"]=0; self.assertEqual(gpio.review(p), [])
    def test_output_forbidden(self):
        p=sample(); p["devices"][0]["kind"]="digital-output"; self.assertTrue(gpio.review(p))
    def test_empty_devices(self):
        p=sample(); p["devices"]=[]; self.assertTrue(gpio.review(p))
    def test_invalid_plan(self): self.assertTrue(gpio.review(None))

if __name__ == "__main__":
    unittest.main()
