"""Offline public-safe backpack manifest preflight; never touches hardware."""
import json
import unittest

BOARDS = {"flipper", "esp32-wroom", "esp32-s2", "arduino-uno", "raspberry-pi-4b"}
def check(raw):
    if not isinstance(raw, str) or len(raw) > 8192: return "invalid-size"
    try: data = json.loads(raw)
    except (ValueError, TypeError): return "invalid-json"
    if not isinstance(data, dict) or set(data) != {"connections"} or not isinstance(data["connections"], list): return "invalid-schema"
    if not 1 <= len(data["connections"]) <= 32: return "invalid-count"
    for c in data["connections"]:
        required = {"source", "target", "source_direction", "target_direction", "source_voltage", "target_max_voltage", "common_ground", "level_shift_verified", "schematic_verified"}
        if not isinstance(c, dict) or set(c) != required: return "invalid-connection"
        if not all(isinstance(c[k], str) and c[k] in BOARDS for k in ("source", "target")) or c["source"] == c["target"]: return "invalid-board"
        if c["source_direction"] != "output" or c["target_direction"] != "input": return "direction-unsafe"
        if any(type(c[k]) not in (int, float) or not 0 < c[k] <= 5.5 for k in ("source_voltage", "target_max_voltage")): return "invalid-voltage"
        if any(type(c[k]) is not bool for k in ("common_ground", "level_shift_verified", "schematic_verified")): return "invalid-boolean"
        if not c["common_ground"] or not c["schematic_verified"]: return "verification-missing"
        if c["source_voltage"] > c["target_max_voltage"] and not c["level_shift_verified"]: return "overvoltage"
    return "review-only"

class Tests(unittest.TestCase):
    def setUp(self):
        self.c = dict(source="arduino-uno", target="esp32-wroom", source_direction="output", target_direction="input", source_voltage=5, target_max_voltage=3.3, common_ground=True, level_shift_verified=True, schematic_verified=True)
    def verify(self, expected, **changes):
        self.assertEqual(check(json.dumps({"connections": [{**self.c, **changes}]})), expected)
    def test_safe_review(self): self.verify("review-only")
    def test_unsafe_voltage(self): self.verify("overvoltage", level_shift_verified=False)
    def test_missing_ground(self): self.verify("verification-missing", common_ground=False)
    def test_missing_schematic(self): self.verify("verification-missing", schematic_verified=False)
    def test_direction(self): self.verify("direction-unsafe", target_direction="output")
    def test_unknown_board(self): self.verify("invalid-board", target="unknown")
    def test_unhashable_board(self): self.verify("invalid-board", target=[])
    def test_boolean_voltage(self): self.verify("invalid-voltage", source_voltage=True)
    def test_invalid_boolean(self): self.verify("invalid-boolean", common_ground="yes")
    def test_extra_field(self): self.verify("invalid-connection", password="not allowed")
    def test_invalid_json(self): self.assertEqual(check("{"), "invalid-json")
    def test_invalid_root(self): self.assertEqual(check("[]"), "invalid-schema")
    def test_empty(self): self.assertEqual(check('{"connections":[]}'), "invalid-count")
    def test_oversize(self): self.assertEqual(check("x"*8193), "invalid-size")

if __name__ == "__main__": unittest.main()
