"""Offline, public-safe backpack power budget gate. No hardware access."""
from dataclasses import dataclass
import math
import unittest

@dataclass(frozen=True)
class Load:
    name: str
    voltage_v: float
    peak_current_a: float

def assess(supply_voltage_v, continuous_current_a, loads, reserve_fraction=0.25):
    """Conservative estimate; NOT approval of physical wiring or USB power delivery."""
    values = (supply_voltage_v, continuous_current_a, reserve_fraction)
    if any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError("finite numeric supply values required")
    if supply_voltage_v <= 0 or continuous_current_a <= 0 or not 0 <= reserve_fraction < 1:
        raise ValueError("invalid supply or reserve")
    if not loads:
        raise ValueError("no loads")
    names = set()
    watts = 0.0
    for load in loads:
        if not isinstance(load, Load) or not load.name or load.name in names:
            raise ValueError("invalid or duplicate load")
        names.add(load.name)
        if any(not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0
               for v in (load.voltage_v, load.peak_current_a)):
            raise ValueError("invalid load ratings")
        watts += load.voltage_v * load.peak_current_a
    capacity_w = supply_voltage_v * continuous_current_a * (1 - reserve_fraction)
    return {
        "load_peak_w": round(watts, 4),
        "derated_capacity_w": round(capacity_w, 4),
        "status": "REVIEW_REQUIRED" if watts <= capacity_w else "OVER_BUDGET",
        "physical_wiring_approved": False,
        "notes": "Separate regulators, converter losses, USB negotiation, grounds, cables, fusing, battery protection and board datasheets require review.",
    }

class PowerBudgetTests(unittest.TestCase):
    def test_under_budget_still_requires_review(self):
        x = assess(5, 3, [Load("pi", 5, 1), Load("esp32", 3.3, .3)])
        self.assertEqual(x["status"], "REVIEW_REQUIRED")
        self.assertFalse(x["physical_wiring_approved"])
    def test_over_budget(self):
        self.assertEqual(assess(5, 1, [Load("pi", 5, 1)])["status"], "OVER_BUDGET")
    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            assess(5, 3, [Load("x", 5, 1), Load("x", 5, 1)])
    def test_reject_nan(self):
        with self.assertRaises(ValueError):
            assess(float("nan"), 3, [Load("x", 5, 1)])
    def test_reject_zero(self):
        with self.assertRaises(ValueError):
            assess(5, 3, [Load("x", 5, 0)])
    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            assess(5, 3, [])
    def test_reserve_changes_result(self):
        loads = [Load("a", 5, 1.5)]
        self.assertEqual(assess(5, 2, loads, .1)["status"], "REVIEW_REQUIRED")
        self.assertEqual(assess(5, 2, loads, .3)["status"], "OVER_BUDGET")

if __name__ == "__main__":
    unittest.main()
