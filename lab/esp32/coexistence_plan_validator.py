#!/usr/bin/env python3
"""Offline ESP32-S2/WROOM coexistence plan validator. No device I/O."""
import argparse
import json
import sys
import unittest

ALLOWED_ROLES = {"wroom": "pi-uart", "s2": "flipperhttp-usart"}
ALLOWED_LOGIC = "3.3V"

def validate(plan):
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    boards = plan.get("boards")
    if not isinstance(boards, list) or len(boards) != 2:
        return ["exactly two board entries required"]
    seen = set()
    ports = set()
    for item in boards:
        if not isinstance(item, dict):
            errors.append("board entry must be an object")
            continue
        board = item.get("board")
        if not isinstance(board, str) or board not in ALLOWED_ROLES or board in seen:
            errors.append("unknown or duplicate board")
            continue
        seen.add(board)
        if item.get("role") != ALLOWED_ROLES[board]:
            errors.append("incorrect role for " + board)
        if item.get("uart_logic") != ALLOWED_LOGIC:
            errors.append("3.3V UART logic required for " + board)
        port = item.get("port")
        if not isinstance(port, str) or not port or port in ports:
            errors.append("missing or shared UART port")
        else:
            ports.add(port)
        if item.get("power_verified") is not True:
            errors.append("power verification required for " + board)
    if seen != set(ALLOWED_ROLES):
        errors.append("WROOM and S2 must both be present")
    if plan.get("flipperhttp_private_ai_enabled") is not False:
        errors.append("FlipperHTTP private AI must remain disabled pending TLS review")
    if plan.get("shared_power_rail") is not False:
        errors.append("shared power rail requires separate engineering review")
    return errors

class Tests(unittest.TestCase):
    def setUp(self):
        self.plan = {"boards": [
            {"board": "wroom", "role": "pi-uart", "uart_logic": "3.3V", "port": "pi-uart0", "power_verified": True},
            {"board": "s2", "role": "flipperhttp-usart", "uart_logic": "3.3V", "port": "flipper-usart", "power_verified": True}],
            "flipperhttp_private_ai_enabled": False, "shared_power_rail": False}
    def test_valid(self): self.assertEqual(validate(self.plan), [])
    def test_5v(self):
        self.plan["boards"][0]["uart_logic"] = "5V"
        self.assertTrue(validate(self.plan))
    def test_duplicate_port(self):
        self.plan["boards"][1]["port"] = "pi-uart0"
        self.assertTrue(validate(self.plan))
    def test_wrong_role(self):
        self.plan["boards"][1]["role"] = "pi-uart"
        self.assertTrue(validate(self.plan))
    def test_missing_power_confirmation(self):
        self.plan["boards"][0]["power_verified"] = False
        self.assertTrue(validate(self.plan))
    def test_private_ai(self):
        self.plan["flipperhttp_private_ai_enabled"] = True
        self.assertTrue(validate(self.plan))
    def test_shared_rail(self):
        self.plan["shared_power_rail"] = True
        self.assertTrue(validate(self.plan))
    def test_unhashable_board(self):
        self.plan["boards"][0]["board"] = ["wroom"]
        self.assertIn("unknown or duplicate board", validate(self.plan))
    def test_unhashable_port(self):
        self.plan["boards"][0]["port"] = ["pi-uart0"]
        self.assertIn("missing or shared UART port", validate(self.plan))
    def test_null_board(self):
        self.plan["boards"][0]["board"] = None
        self.assertTrue(validate(self.plan))
    def test_missing_board(self):
        self.plan["boards"].pop()
        self.assertTrue(validate(self.plan))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", help="Offline JSON file; never connects to hardware")
    args = parser.parse_args()
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.plan:
        parser.error("provide --self-test or --plan")
    with open(args.plan, encoding="utf-8") as fh:
        errors = validate(json.load(fh))
    print(json.dumps({"safe_for_review": not errors, "errors": errors}, sort_keys=True))
    return 0 if not errors else 2

if __name__ == "__main__":
    sys.exit(main())
