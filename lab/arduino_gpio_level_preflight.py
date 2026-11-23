"""Public-safe offline Arduino Uno / ESP32 GPIO level advisory; no hardware I/O.

Input JSON: {"connections":[{"source":"uno_r3","target":"esp32_wroom",
"signal":"digital","voltage":5.0}]}
Board names are abstract; this does NOT verify physical pinouts, current, power
rails, direction, or level-shifter specifications. Never authorizes wiring.
"""
import json
import sys
import unittest

LEVELS = {"uno_r3": 5.0, "esp32_wroom": 3.3, "esp32_s2": 3.3, "flipper_zero": 3.3}

def check(plan):
    if not isinstance(plan, dict) or set(plan) != {"connections"} or not isinstance(plan["connections"], list):
        return ["invalid plan"]
    if len(plan["connections"]) > 32:
        return ["too many connections"]
    issues = []
    for i, c in enumerate(plan["connections"]):
        if not isinstance(c, dict) or set(c) != {"source", "target", "signal", "voltage"}:
            issues.append(f"{i}: invalid connection fields")
            continue
        a, b, signal, v = c["source"], c["target"], c["signal"], c["voltage"]
        if not isinstance(a, str) or not isinstance(b, str) or a not in LEVELS or b not in LEVELS:
            issues.append(f"{i}: unknown board")
            continue
        if signal not in ("digital", "analog", "uart", "ground") or type(v) not in (int, float) or not 0 <= v <= 5.0:
            issues.append(f"{i}: invalid signal or voltage")
            continue
        if signal == "ground" and v != 0:
            issues.append(f"{i}: ground must be 0 V")
        if signal != "ground" and v > min(LEVELS[a], LEVELS[b]):
            issues.append(f"{i}: voltage exceeds lower-voltage board; level shifting required")
        if a == b:
            issues.append(f"{i}: same-board wiring needs separate review")
    return issues

def main():
    raw = sys.stdin.buffer.read(8193)
    if len(raw) > 8192:
        issues = ["input too large"]
    else:
        try:
            issues = check(json.loads(raw))
        except (ValueError, UnicodeError):
            issues = ["invalid JSON"]
    print(json.dumps({"safe_to_connect": False, "advisory_only": True, "errors": issues,
                      "note": "Passing checks NEVER authorizes physical wiring or power-up."}))
    return 1 if issues else 0

class Tests(unittest.TestCase):
    def setUp(self):
        self.c = {"source": "uno_r3", "target": "esp32_wroom", "signal": "digital", "voltage": 5.0}
    def test_reject_5v(self):
        self.assertTrue(check({"connections": [self.c]}))
    def test_3v3_advisory(self):
        self.c["voltage"] = 3.3
        self.assertEqual(check({"connections": [self.c]}), [])
    def test_bad_board(self):
        self.c["target"] = "unknown"
        self.assertTrue(check({"connections": [self.c]}))
    def test_bad_voltage_type(self):
        self.c["voltage"] = True
        self.assertTrue(check({"connections": [self.c]}))
    def test_ground_voltage(self):
        self.c.update(signal="ground", voltage=3.3)
        self.assertTrue(check({"connections": [self.c]}))
    def test_invalid_shape(self):
        self.assertTrue(check({"wrong": []}))
    def test_excess_connections(self):
        self.assertTrue(check({"connections": [self.c] * 33}))
    def test_s2_3v3(self):
        self.c.update(target="esp32_s2", voltage=3.3)
        self.assertEqual(check({"connections": [self.c]}), [])

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.argv = [sys.argv[0]]
        unittest.main()
    else:
        sys.exit(main())
