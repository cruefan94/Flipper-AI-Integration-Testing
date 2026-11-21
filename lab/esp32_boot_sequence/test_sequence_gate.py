import unittest
from sequence_gate import Observation, evaluate

class SequenceGateTests(unittest.TestCase):
    def test_candidate(self):
        self.assertEqual(evaluate("esp32", [Observation("low","low",True),Observation("high","low",True)])["status"], "candidate")
    def test_gpio0_high(self):
        self.assertEqual(evaluate("esp32", [Observation("low","high",True),Observation("high","high",True)])["status"], "not-observed")
    def test_later_valid_release_after_invalid_release(self):
        observations = [
            Observation("low", "high", True),
            Observation("high", "high", True),
            Observation("low", "low", True),
            Observation("high", "low", True),
        ]
        self.assertEqual(evaluate("esp32", observations)["status"], "candidate")

    def test_multiple_invalid_releases(self):
        observations = [
            Observation("low", "high", True),
            Observation("high", "high", True),
            Observation("low", "high", True),
            Observation("high", "low", True),
        ]
        self.assertEqual(evaluate("esp32", observations)["status"], "not-observed")

    def test_later_candidate_is_not_proof(self):
        observations = [
            Observation("low", "high", True),
            Observation("high", "high", True),
            Observation("low", "low", True),
            Observation("high", "low", True),
        ]
        self.assertIn("ROM log", evaluate("esp32", observations)["reason"])

    def test_s2_separate(self):
        self.assertEqual(evaluate("esp32-s2", [Observation("low","low",True),Observation("high","low",True)])["status"], "manual-review")
    def test_unknown_family(self):
        self.assertEqual(evaluate("esp32-c3", [])["status"], "blocked")
    def test_missing_power(self):
        self.assertEqual(evaluate("esp32", [Observation("low","low",False)])["status"], "blocked")
    def test_unknown_pins(self):
        self.assertEqual(evaluate("esp32", [Observation("unknown","low",True)])["status"], "inconclusive")
    def test_no_transition(self):
        self.assertEqual(evaluate("esp32", [Observation("high","low",True)])["status"], "inconclusive")
    def test_empty(self):
        self.assertEqual(evaluate("esp32", [])["status"], "blocked")
    def test_bad_value(self):
        self.assertEqual(evaluate("esp32", [Observation("HIGH","low",True)])["status"], "blocked")
    def test_not_proof(self):
        self.assertIn("ROM log", evaluate("esp32", [Observation("low","low",True),Observation("high","low",True)])["reason"])

if __name__ == "__main__":
    unittest.main()
