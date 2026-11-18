"""Synthetic tests only: no hardware or secret access."""
import copy
import unittest
from backpack_power_budget import evaluate

GOOD = {"rails": [{"name": "isolated_3v3", "voltage_v": 3.3, "continuous_limit_ma": 1000, "loads": [{"name": "ESP32", "peak_ma": 450}], "backfeed_isolation_verified": True, "common_ground_reviewed": True}]}

class TestBudget(unittest.TestCase):
    def test_valid(self): self.assertEqual(evaluate(GOOD), [])
    def test_empty(self): self.assertTrue(evaluate({}))
    def test_duplicate_rail(self):
        x = copy.deepcopy(GOOD); x["rails"].append(copy.deepcopy(x["rails"][0])); self.assertTrue(evaluate(x))
    def test_overload(self):
        x = copy.deepcopy(GOOD); x["rails"][0]["loads"][0]["peak_ma"] = 900; self.assertTrue(evaluate(x))
    def test_boolean_not_current(self):
        x = copy.deepcopy(GOOD); x["rails"][0]["loads"][0]["peak_ma"] = True; self.assertTrue(evaluate(x))
    def test_missing_isolation(self):
        x = copy.deepcopy(GOOD); x["rails"][0].pop("backfeed_isolation_verified"); self.assertTrue(evaluate(x))
    def test_missing_ground_review(self):
        x = copy.deepcopy(GOOD); x["rails"][0].pop("common_ground_reviewed"); self.assertTrue(evaluate(x))
    def test_negative_voltage(self):
        x = copy.deepcopy(GOOD); x["rails"][0]["voltage_v"] = -1; self.assertTrue(evaluate(x))
    def test_missing_peak(self):
        x = copy.deepcopy(GOOD); x["rails"][0]["loads"][0].pop("peak_ma"); self.assertTrue(evaluate(x))
    def test_nonobject(self): self.assertTrue(evaluate([]))

if __name__ == "__main__": unittest.main()
