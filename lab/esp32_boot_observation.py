#!/usr/bin/env python3
"""Offline ESP32-WROOM EN/BOOT observation validator. Never accesses hardware."""
import json
import sys
import unittest

STATES = {"released", "pressed", "unknown"}
OUTCOMES = {"rom_download_banner", "normal_boot_banner", "no_serial_output", "unknown"}

def classify(record):
    """Fail closed: observations do not establish wiring, chip identity, or flash readiness."""
    if not isinstance(record, dict) or set(record) != {"board", "steps", "observed"}:
        raise ValueError("Expected board, steps and observed only")
    if record["board"] != "ESP32-WROOM-32":
        raise ValueError("Board identity must be explicitly ESP32-WROOM-32")
    steps = record["steps"]
    if not isinstance(steps, list) or len(steps) != 3:
        raise ValueError("Exactly three manually observed steps required")
    expected = [("pressed", "released"), ("pressed", "pressed"), ("released", "pressed")]
    sequence_matches = True
    for step, (boot, en) in zip(steps, expected):
        if not isinstance(step, dict) or set(step) != {"boot", "en"}:
            raise ValueError("Each step must contain only boot and en")
        if any(type(step[k]) is not str or step[k] not in STATES for k in ("boot", "en")):
            raise ValueError("Invalid switch state")
        if (step["boot"], step["en"]) != (boot, en):
            sequence_matches = False
    outcome = record["observed"]
    if type(outcome) is not str or outcome not in OUTCOMES:
        raise ValueError("Invalid observation")
    if not sequence_matches:
        return {"status": "INCONCLUSIVE", "reason": "sequence_not_observed",
                "flash_authorized": False}
    if outcome == "rom_download_banner":
        return {"status": "OBSERVED_ROM_BANNER_ONLY", "reason": "manual_evidence_unverified",
                "flash_authorized": False}
    return {"status": "INCONCLUSIVE", "reason": outcome, "flash_authorized": False}

class OfflineTests(unittest.TestCase):
    def fixture(self, observed="rom_download_banner"):
        return {"board": "ESP32-WROOM-32",
                "steps": [{"boot": "pressed", "en": "released"},
                          {"boot": "pressed", "en": "pressed"},
                          {"boot": "released", "en": "pressed"}],
                "observed": observed}

    def test_rom_banner_is_not_flash_permission(self):
        self.assertFalse(classify(self.fixture())["flash_authorized"])

    def test_normal_boot_inconclusive(self):
        self.assertEqual(classify(self.fixture("normal_boot_banner"))["status"], "INCONCLUSIVE")

    def test_missing_serial_output_inconclusive(self):
        self.assertEqual(classify(self.fixture("no_serial_output"))["status"], "INCONCLUSIVE")

    def test_sequence_mismatch(self):
        f = self.fixture()
        f["steps"][0]["boot"] = "released"
        self.assertEqual(classify(f)["reason"], "sequence_not_observed")

    def test_unknown_switch_state(self):
        f = self.fixture()
        f["steps"][0]["en"] = "unknown"
        self.assertEqual(classify(f)["status"], "INCONCLUSIVE")

    def test_late_invalid_step_rejected_even_after_sequence_mismatch(self):
        f = self.fixture()
        f["steps"][0]["boot"] = "released"
        f["steps"][2]["en"] = []
        with self.assertRaises(ValueError): classify(f)

    def test_invalid_observation_rejected_even_after_sequence_mismatch(self):
        f = self.fixture()
        f["steps"][0]["boot"] = "released"
        f["observed"] = {"private": "data"}
        with self.assertRaises(ValueError): classify(f)

    def test_valid_mismatch_still_inconclusive_and_not_authorized(self):
        f = self.fixture()
        f["steps"][0]["boot"] = "released"
        result = classify(f)
        self.assertEqual(result["reason"], "sequence_not_observed")
        self.assertIs(result["flash_authorized"], False)

    def test_wrong_board_rejected(self):
        f = self.fixture()
        f["board"] = "ESP32-S2"
        with self.assertRaises(ValueError): classify(f)

    def test_malformed_steps_rejected(self):
        f = self.fixture()
        f["steps"] = "not a list"
        with self.assertRaises(ValueError): classify(f)

    def test_extra_keys_rejected(self):
        f = self.fixture()
        f["serial"] = "private-device-id"
        with self.assertRaises(ValueError): classify(f)

    def test_boolean_state_rejected(self):
        f = self.fixture()
        f["steps"][0]["boot"] = True
        with self.assertRaises(ValueError): classify(f)

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 1:
        try:
            payload = json.load(sys.stdin)
            print(json.dumps(classify(payload), sort_keys=True))
        except (ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "REJECTED", "reason": str(exc),
                              "flash_authorized": False}))
            sys.exit(2)
    else:
        print("Usage: python3 esp32_boot_observation.py [--test]", file=sys.stderr)
        sys.exit(2)
