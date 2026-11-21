"""Offline synthetic tests; no Raspberry Pi or USB hardware needed."""
import json
import unittest
from raspberry_pi.pi_health_capture_validator import validate_sample, validate_text

def sample():
    return {"status":"read_only","hardware_control":False,
            "memory_bytes":{"MemTotal":4096,"MemAvailable":2048,"SwapTotal":1024,"SwapFree":512},
            "load_averages":[0.0,0.1,1.0],"temperature_c":42.5}

class CaptureTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_text(json.dumps(sample())),1)
    def test_multiple(self):
        self.assertEqual(validate_text("\n".join([json.dumps(sample())]*3)),3)
    def test_reject_hardware_control(self):
        s=sample();s["hardware_control"]=True
        with self.assertRaises(ValueError):validate_sample(s)
    def test_reject_extra_fields(self):
        s=sample();s["serial"]="secret"
        with self.assertRaises(ValueError):validate_sample(s)
    def test_reject_bad_memory(self):
        s=sample();s["memory_bytes"]["MemAvailable"]=5000
        with self.assertRaises(ValueError):validate_sample(s)
    def test_reject_nan_load(self):
        s=sample();s["load_averages"]=[float("nan"),0,0]
        with self.assertRaises(ValueError):validate_sample(s)
    def test_reject_swap(self):
        s=sample();s["memory_bytes"]["SwapFree"]=2048
        with self.assertRaises(ValueError):validate_sample(s)
    def test_reject_empty(self):
        with self.assertRaises(ValueError):validate_text("")
    def test_reject_too_many(self):
        with self.assertRaises(ValueError):validate_text("\n".join([json.dumps(sample())]*31))
    def test_reject_boolean_load(self):
        s=sample();s["load_averages"]=[True,0,0]
        with self.assertRaises(ValueError):validate_sample(s)

if __name__=="__main__":
    unittest.main()
