"""Public-safe, offline Arduino Uno -> ESP32 voltage-domain review. No hardware I/O."""
from dataclasses import dataclass
from math import isfinite
import unittest

@dataclass(frozen=True)
class Pin:
    name: str
    output_high_v: float
    input_max_v: float

def review_connection(source: Pin, sink: Pin, *, common_ground: bool,
                      level_shifter_output_v: float | None = None) -> tuple[bool, str]:
    values = (source.output_high_v, source.input_max_v, sink.output_high_v, sink.input_max_v)
    if not all(isinstance(v, (float, int)) and not isinstance(v, bool) and isfinite(v) and v > 0 for v in values):
        return False, "invalid or missing pin voltage rating"
    if not common_ground:
        return False, "common ground not verified"
    delivered = source.output_high_v
    if level_shifter_output_v is not None:
        v = level_shifter_output_v
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not isfinite(v) or v <= 0:
            return False, "invalid shifter output rating"
        if v > source.output_high_v:
            return False, "shifter output exceeds supplied input: unsupported model"
        delivered = v
    if delivered > sink.input_max_v:
        return False, "overvoltage at destination GPIO"
    return True, "voltage ceiling review only; logic thresholds, current, pin modes and hardware unverified"

UNO = Pin("Uno 5V GPIO", 5.0, 5.0)
ESP = Pin("ESP32 GPIO", 3.3, 3.6)

class VoltageReviewTests(unittest.TestCase):
    def test_direct_5v_rejected(self):
        self.assertFalse(review_connection(UNO, ESP, common_ground=True)[0])
    def test_shifted_3v3_review_only(self):
        ok, reason = review_connection(UNO, ESP, common_ground=True, level_shifter_output_v=3.3)
        self.assertTrue(ok)
        self.assertIn("review only", reason)
    def test_ground_required(self):
        self.assertFalse(review_connection(ESP, ESP, common_ground=False)[0])
    def test_direct_3v3(self):
        self.assertTrue(review_connection(ESP, ESP, common_ground=True)[0])
    def test_bad_shifter(self):
        self.assertFalse(review_connection(UNO, ESP, common_ground=True, level_shifter_output_v=float("nan"))[0])
    def test_shifter_boost_unsupported(self):
        self.assertFalse(review_connection(ESP, UNO, common_ground=True, level_shifter_output_v=5)[0])
    def test_invalid_voltage(self):
        self.assertFalse(review_connection(Pin("bad", -1, 3.3), ESP, common_ground=True)[0])
    def test_boolean_rating_rejected(self):
        self.assertFalse(review_connection(Pin("bad", True, 3.3), ESP, common_ground=True)[0])

if __name__ == "__main__":
    unittest.main()
