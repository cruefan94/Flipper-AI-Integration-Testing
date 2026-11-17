import unittest
from usb_topology_guard import compare

A = {"port":"/dev/ttyUSB0","vid":"10C4","pid":"EA60","serial":"esp-a"}
B = {"port":"/dev/ttyACM0","vid":"0483","pid":"5740","serial":"flipper-a"}

class TopologyTests(unittest.TestCase):
    def test_stable(self): self.assertTrue(compare([A,B],[B,A])["stable"])
    def test_removed(self): self.assertEqual(compare([A],[])["changes"][0]["kind"],"removed")
    def test_added(self): self.assertEqual(compare([],[A])["changes"][0]["kind"],"added")
    def test_changed(self): self.assertEqual(compare([A],[dict(A,serial="esp-b")])["changes"][0]["kind"],"identity_changed")
    def test_duplicate_port(self):
        with self.assertRaises(ValueError): compare([A,dict(A,serial="other")],[])
    def test_duplicate_identity(self):
        with self.assertRaises(ValueError): compare([A,dict(A,port="/dev/ttyUSB1")],[])
    def test_missing_serial(self):
        with self.assertRaises(ValueError): compare([dict(A,serial="")],[])
    def test_bad_vid(self):
        with self.assertRaises(ValueError): compare([dict(A,vid="zzzz")],[])
    def test_bad_port(self):
        with self.assertRaises(ValueError): compare([dict(A,port="/tmp/fake")],[])
    def test_no_authorization(self): self.assertFalse(compare([A],[A])["flash_authorized"])

if __name__ == "__main__": unittest.main()
