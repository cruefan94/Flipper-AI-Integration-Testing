import unittest
from arduino_sensor_contract import review

def plan():
    return {"board":"arduino-uno-r3","operation":"review-only","common_ground_verified":True,"sensors":[{"pin":"A0","mode":"analog-input","signal_voltage":3.3}]}

class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(review(plan()), [])
    def test_board(self):
        p=plan();p["board"]="esp32";self.assertTrue(review(p))
    def test_operation(self):
        p=plan();p["operation"]="flash";self.assertTrue(review(p))
    def test_ground(self):
        p=plan();p["common_ground_verified"]=False;self.assertTrue(review(p))
    def test_reserved(self):
        p=plan();p["sensors"][0]["pin"]="D0";self.assertTrue(review(p))
    def test_duplicate(self):
        p=plan();p["sensors"].append(dict(p["sensors"][0]));self.assertTrue(review(p))
    def test_analog_pin(self):
        p=plan();p["sensors"][0]["pin"]="D2";self.assertTrue(review(p))
    def test_output(self):
        p=plan();p["sensors"][0]["mode"]="digital-output";self.assertTrue(review(p))
    def test_nan(self):
        p=plan();p["sensors"][0]["signal_voltage"]=float("nan");self.assertTrue(review(p))
    def test_inf(self):
        p=plan();p["sensors"][0]["signal_voltage"]=float("inf");self.assertTrue(review(p))
    def test_bool(self):
        p=plan();p["sensors"][0]["signal_voltage"]=True;self.assertTrue(review(p))
    def test_overvoltage(self):
        p=plan();p["sensors"][0]["signal_voltage"]=5.1;self.assertTrue(review(p))
    def test_empty(self):
        p=plan();p["sensors"]=[];self.assertTrue(review(p))
    def test_bad_sensor(self):
        p=plan();p["sensors"]=[None];self.assertTrue(review(p))

if __name__ == "__main__": unittest.main()
