"""Synthetic-only ESP32-WROOM trace review regression tests."""
import unittest
from esp32_boot_trace_review import Sample, review
R = Sample(0, 0, 3.3, True)
D = Sample(3.3, 0, 3.3, True)
N = Sample(3.3, 3.3, 3.3, True)
class ReviewTests(unittest.TestCase):
    def test_download(self): self.assertIn("download strap", review([R,D]))
    def test_normal(self): self.assertIn("normal boot", review([R,N]))
    def test_no_reset(self): self.assertIn("INDETERMINATE", review([D,D]))
    def test_no_samples(self): self.assertIn("REJECT", review([]))
    def test_one_sample(self): self.assertIn("REJECT", review([R]))
    def test_unsupported(self): self.assertIn("REJECT", review([R,Sample(3.3,0,3.3,True,"ESP32-S2")]))
    def test_no_ground(self): self.assertIn("REJECT", review([R,Sample(3.3,0,3.3,False)]))
    def test_nan(self): self.assertIn("REJECT", review([R,Sample(3.3,float("nan"),3.3,True)]))
    def test_inf(self): self.assertIn("REJECT", review([R,Sample(3.3,0,float("inf"),True)]))
    def test_5v(self): self.assertIn("REJECT", review([R,Sample(3.3,0,5,True)]))
    def test_bool(self): self.assertIn("REJECT", review([R,Sample(True,0,3.3,True)]))
    def test_ambiguous_gpio(self): self.assertIn("INDETERMINATE", review([R,Sample(3.3,1.4,3.3,True)]))
    def test_ambiguous_en(self): self.assertIn("INDETERMINATE", review([R,Sample(1.4,0,3.3,True),D]))
    def test_low_uart(self): self.assertIn("REJECT", review([R,Sample(3.3,0,1.8,True)]))
if __name__ == "__main__": unittest.main()
