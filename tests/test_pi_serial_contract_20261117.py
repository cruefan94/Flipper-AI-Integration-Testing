"""Synthetic regression tests: no Pi, Flipper, ESP32 or Arduino required."""
import unittest
from lab.pi_serial_contract_20261117 import review

A = {"board":"flipper_zero","port":"/dev/ttyACM0","vid":"0483","pid":"5740","serial":"FZ-A","topology":"1-1"}
B = {"board":"esp32_wroom","port":"/dev/ttyUSB0","vid":"10c4","pid":"ea60","serial":"ESP-A","topology":"1-2"}

class SerialContractTests(unittest.TestCase):
    def check(self, before, after, target="ESP-A", expected="BLOCKED"):
        result = review(before, after, target)
        self.assertEqual(result["review"], expected)
        self.assertFalse(result["flash_allowed"])

    def test_stable(self): self.check([A,B],[A.copy(),B.copy()],expected="REVIEW_ONLY")
    def test_missing_target(self): self.check([A,B],[A],"ESP-A")
    def test_changed_port(self): self.check([A,B],[A,{**B,"port":"/dev/ttyUSB1"}])
    def test_changed_topology(self): self.check([A,B],[A,{**B,"topology":"1-3"}])
    def test_changed_vid(self): self.check([A,B],[A,{**B,"vid":"1234"}])
    def test_duplicate_port(self): self.check([A,B],[A,{**B,"port":"/dev/ttyACM0"}])
    def test_duplicate_serial(self): self.check([A,B],[A,{**B,"serial":"FZ-A"}])
    def test_duplicate_topology(self): self.check([A,B],[A,{**B,"topology":"1-1"}])
    def test_invalid_usb_id(self): self.check([A,B],[A,{**B,"pid":"ZZZZ"}])
    def test_unsupported_board(self): self.check([A,B],[A,{**B,"board":"unknown"}])
    def test_empty_snapshot(self): self.check([],[A,B])
    def test_missing_serial(self): self.check([A,B],[A,{**B,"serial":""}])
    def test_no_target(self): self.check([A,B],[A,B],"")
    def test_invalid_port(self): self.check([A,B],[A,{**B,"port":"/tmp/fake"}])

if __name__ == "__main__":
    unittest.main()
