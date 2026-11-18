"""Offline-only ESP32 ROM evidence gate. Never opens ports or flashes devices."""
import json
import sys
import unittest

CHIPS = {"ESP32", "ESP32-S2"}

def evaluate(record):
    if not isinstance(record, dict):
        return False, "invalid-record"
    if record.get("chip") not in CHIPS:
        return False, "unknown-chip"
    if record.get("transport") != "usb-serial":
        return False, "unsupported-transport"
    if record.get("device_path_stable") is not True:
        return False, "unstable-device"
    if record.get("voltage_verified_3v3") is not True:
        return False, "voltage-unverified"
    if record.get("common_ground_verified") is not True:
        return False, "ground-unverified"
    if record.get("gpio0_low_during_reset") is not True:
        return False, "boot-sequence-unverified"
    if record.get("rom_download_mode_observed") is not True:
        return False, "rom-evidence-missing"
    if record.get("observed_chip") != record["chip"]:
        return False, "chip-mismatch"
    return True, "offline-evidence-consistent"

class GateTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(chip="ESP32", transport="usb-serial", device_path_stable=True,
            voltage_verified_3v3=True, common_ground_verified=True,
            gpio0_low_during_reset=True, rom_download_mode_observed=True, observed_chip="ESP32")
    def test_good(self): self.assertEqual(evaluate(self.good), (True,"offline-evidence-consistent"))
    def test_s2(self):
        self.good.update(chip="ESP32-S2", observed_chip="ESP32-S2")
        self.assertTrue(evaluate(self.good)[0])
    def test_not_dict(self): self.assertFalse(evaluate([])[0])
    def test_unknown_chip(self): self.good["chip"]="ESP32-C3"; self.assertFalse(evaluate(self.good)[0])
    def test_mismatched_chip(self): self.good["observed_chip"]="ESP32-S2"; self.assertFalse(evaluate(self.good)[0])
    def test_transport(self): self.good["transport"]="wifi"; self.assertFalse(evaluate(self.good)[0])
    def test_missing_evidence(self): self.good.pop("rom_download_mode_observed"); self.assertFalse(evaluate(self.good)[0])
    def test_no_ground(self): self.good["common_ground_verified"]=False; self.assertFalse(evaluate(self.good)[0])
    def test_wrong_voltage(self): self.good["voltage_verified_3v3"]="true"; self.assertFalse(evaluate(self.good)[0])
    def test_gpio0(self): self.good["gpio0_low_during_reset"]=False; self.assertFalse(evaluate(self.good)[0])
    def test_unstable_path(self): self.good["device_path_stable"]=False; self.assertFalse(evaluate(self.good)[0])

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding="utf-8") as f:
                result = evaluate(json.load(f))
            print(json.dumps({"ready":result[0], "reason":result[1]}))
            sys.exit(0 if result[0] else 2)
        except (OSError, ValueError):
            print(json.dumps({"ready":False,"reason":"invalid-input"}))
            sys.exit(2)
    else:
        print("Usage: rom_evidence_gate.py --self-test | observation.json", file=sys.stderr)
        sys.exit(2)
