"""Offline advisory current-budget estimator. Never authorizes wiring or hardware use."""
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass

@dataclass(frozen=True)
class Load:
    name: str
    max_ma: str

def check_budget(source_limit_ma: str, loads: list[Load], reserve_percent: str = "25") -> dict:
    def rating(value, allow_zero=False):
        try:
            n = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("invalid or unverified rating") from None
        if not n.is_finite() or (n < 0 if allow_zero else n <= 0):
            raise ValueError("invalid or unverified rating")
        return n
    try:
        limit = rating(source_limit_ma)
        reserve = rating(reserve_percent, True)
        if reserve >= 100 or not loads:
            raise ValueError("invalid reserve or empty loads")
        names = [x.name for x in loads]
        if any(not isinstance(n, str) or not n.strip() for n in names) or len(set(names)) != len(names):
            raise ValueError("load names must be unique and nonempty")
        total = sum((rating(x.max_ma) for x in loads), Decimal(0))
        available = limit * (100 - reserve) / 100
        return {"status": "WITHIN_ESTIMATED_BUDGET" if total <= available else "OVER_BUDGET",
                "load_ma": str(total), "reserved_limit_ma": str(available),
                "wiring_authorized": False, "hardware_verified": False}
    except (AttributeError, TypeError) as exc:
        raise ValueError("invalid load specification") from exc

if __name__ == "__main__":
    import unittest
    class Tests(unittest.TestCase):
        def test_within(self):
            self.assertEqual(check_budget("500", [Load("board", "200")])["status"], "WITHIN_ESTIMATED_BUDGET")
        def test_over(self):
            self.assertEqual(check_budget("500", [Load("board", "400")])["status"], "OVER_BUDGET")
        def test_boundary(self):
            self.assertEqual(check_budget("100", [Load("board", "75")])["status"], "WITHIN_ESTIMATED_BUDGET")
        def test_missing(self):
            with self.assertRaises(ValueError): check_budget("500", [Load("board", "")])
        def test_nan(self):
            with self.assertRaises(ValueError): check_budget("NaN", [Load("board", "20")])
        def test_duplicate(self):
            with self.assertRaises(ValueError): check_budget("500", [Load("x", "20"), Load("x", "30")])
        def test_empty(self):
            with self.assertRaises(ValueError): check_budget("500", [])
        def test_never_authorized(self):
            self.assertFalse(check_budget("500", [Load("board", "20")])["wiring_authorized"])
    unittest.main(verbosity=2)
