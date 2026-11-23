"""Offline, public-safe Arduino/ESP32 sensor wiring manifest preflight.

No GPIO, serial, network, or flashing operations. Input is operator-authored JSON.
Passing checks do not authorize physical connection or power-up.
"""
import json
import sys
import unittest

BOARDS = {"uno_r3": 5.0, "esp32_wroom": 3.3, "esp32_s2": 3.3, "flipper_zero": 3.3}
SIGNALS = {"digital", "analog", "i2c", "spi", "uart", "ground"}
MAX_BYTES = 8192


def validate(plan):
    if not isinstance(plan, dict) or set(plan) != {"modules"}:
        return ["invalid manifest"]
    modules = plan["modules"]
    if not isinstance(modules, list) or not 1 <= len(modules) <= 16:
        return ["module count must be 1..16"]
    errors, labels = [], set()
    for index, module in enumerate(modules):
        prefix = str(index)
        if not isinstance(module, dict) or set(module) != {"label", "host", "signal", "logic_voltage", "level_shifter", "common_ground"}:
            errors.append(prefix + ": invalid module fields")
            continue
        label, host, signal = module["label"], module["host"], module["signal"]
        volts = module["logic_voltage"]
        shift, ground = module["level_shifter"], module["common_ground"]
        if not isinstance(label, str) or not 1 <= len(label) <= 32 or not all(c.isascii() and (c.isalnum() or c in "-_") for c in label):
            errors.append(prefix + ": invalid label")
        elif label in labels:
            errors.append(prefix + ": duplicate label")
        else:
            labels.add(label)
        if host not in BOARDS if isinstance(host, str) else True:
            errors.append(prefix + ": unknown host")
            continue
        if not isinstance(signal, str) or signal not in SIGNALS:
            errors.append(prefix + ": unknown signal")
        if type(volts) not in (int, float) or not 0 <= volts <= 5.0:
            errors.append(prefix + ": invalid voltage")
            continue
        if type(shift) is not bool or type(ground) is not bool:
            errors.append(prefix + ": invalid safety declarations")
            continue
        if not ground:
            errors.append(prefix + ": common ground unverified")
        if volts > BOARDS[host] and not shift:
            errors.append(prefix + ": level conversion required")
        if signal == "ground" and volts != 0:
            errors.append(prefix + ": ground signal must be zero volts")
    return errors


def main():
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    try:
        errors = ["input too large"] if len(raw) > MAX_BYTES else validate(json.loads(raw))
    except (ValueError, UnicodeError):
        errors = ["invalid JSON"]
    print(json.dumps({"advisory_only": True, "safe_to_connect": False, "errors": errors,
                      "note": "Physical pinout, current, pull-ups, bus voltage and power rails remain unverified."}))
    return 1 if errors else 0


class Tests(unittest.TestCase):
    def setUp(self):
        self.module = dict(label="sensor_1", host="esp32_wroom", signal="i2c",
                           logic_voltage=3.3, level_shifter=False, common_ground=True)

    def test_valid_advisory(self):
        self.assertEqual(validate({"modules": [self.module]}), [])

    def test_empty_rejected(self):
        self.assertTrue(validate({"modules": []}))

    def test_5v_rejected(self):
        self.module["logic_voltage"] = 5
        self.assertIn("0: level conversion required", validate({"modules": [self.module]}))

    def test_shifter_declared_still_advisory(self):
        self.module.update(logic_voltage=5, level_shifter=True)
        self.assertEqual(validate({"modules": [self.module]}), [])

    def test_missing_ground(self):
        self.module["common_ground"] = False
        self.assertTrue(validate({"modules": [self.module]}))

    def test_duplicate(self):
        self.assertTrue(validate({"modules": [self.module, self.module.copy()]}))

    def test_unknown_board(self):
        self.module["host"] = "unknown"
        self.assertTrue(validate({"modules": [self.module]}))

    def test_bool_voltage(self):
        self.module["logic_voltage"] = True
        self.assertTrue(validate({"modules": [self.module]}))

    def test_invalid_fields(self):
        self.module["pin"] = "D1"
        self.assertTrue(validate({"modules": [self.module]}))

    def test_bad_ground_voltage(self):
        self.module.update(signal="ground", logic_voltage=3.3)
        self.assertTrue(validate({"modules": [self.module]}))


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        unittest.main(argv=[sys.argv[0]])
    else:
        sys.exit(main())
