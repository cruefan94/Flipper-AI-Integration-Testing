"""Offline fail-closed ESP32 Pi flash preflight; never opens a port or flashes."""
import json
import re
import sys
import unittest

TARGETS = {"esp32-wroom-32": "esp32", "esp32-s2": "esp32s2"}
PORT = re.compile(r"^/dev/serial/by-id/[A-Za-z0-9_.:+-]+$")
SHA = re.compile(r"^[a-fA-F0-9]{64}$")

def inspect(config):
    if not isinstance(config, dict):
        return {"ready_for_manual_review": False, "errors": ["configuration must be an object"], "flashing_performed": False}
    errors = []
    board = config.get("board")
    if board not in TARGETS:
        errors.append("unsupported board")
    if config.get("chip_target") != TARGETS.get(board):
        errors.append("chip target does not match board")
    port = config.get("serial_port")
    if not isinstance(port, str) or not PORT.fullmatch(port):
        errors.append("stable /dev/serial/by-id/ path required")
    if config.get("voltage_logic") != 3.3:
        errors.append("ESP32 requires 3.3V logic")
    for key in ("common_ground_verified", "power_budget_verified", "serial_owner_exclusive", "boot_mode_verified", "owner_authorized"):
        if config.get(key) is not True:
            errors.append(key + " must be true")
    digest = config.get("firmware_sha256")
    if not isinstance(digest, str) or not SHA.fullmatch(digest):
        errors.append("full firmware SHA-256 required")
    if config.get("operation") != "preflight_only":
        errors.append("operation must be preflight_only")
    if config.get("erase_flash") is not False:
        errors.append("erase_flash must be false")
    return {"ready_for_manual_review": not errors, "errors": errors, "flashing_performed": False}

class Tests(unittest.TestCase):
    def setUp(self):
        self.valid = dict(board="esp32-wroom-32", chip_target="esp32",
            serial_port="/dev/serial/by-id/usb-Silicon_Labs_CP2102_1234",
            voltage_logic=3.3, common_ground_verified=True,
            power_budget_verified=True, serial_owner_exclusive=True,
            boot_mode_verified=True, owner_authorized=True,
            firmware_sha256="a" * 64, operation="preflight_only", erase_flash=False)
    def test_valid(self):
        self.assertTrue(inspect(self.valid)["ready_for_manual_review"])
    def test_s2(self):
        self.assertTrue(inspect(dict(self.valid, board="esp32-s2", chip_target="esp32s2"))["ready_for_manual_review"])
    def test_wrong_target(self):
        self.assertFalse(inspect(dict(self.valid, chip_target="esp32s2"))["ready_for_manual_review"])
    def test_unstable_port(self):
        self.assertFalse(inspect(dict(self.valid, serial_port="/dev/ttyUSB0"))["ready_for_manual_review"])
    def test_5v(self):
        self.assertFalse(inspect(dict(self.valid, voltage_logic=5))["ready_for_manual_review"])
    def test_serial_conflict(self):
        self.assertFalse(inspect(dict(self.valid, serial_owner_exclusive=False))["ready_for_manual_review"])
    def test_unauthorized(self):
        self.assertFalse(inspect(dict(self.valid, owner_authorized=False))["ready_for_manual_review"])
    def test_digest(self):
        self.assertFalse(inspect(dict(self.valid, firmware_sha256="bad"))["ready_for_manual_review"])
    def test_erase(self):
        self.assertFalse(inspect(dict(self.valid, erase_flash=True))["ready_for_manual_review"])
    def test_flash(self):
        self.assertFalse(inspect(dict(self.valid, operation="flash"))["ready_for_manual_review"])
    def test_missing(self):
        self.assertFalse(inspect({})["ready_for_manual_review"])
    def test_invalid_type(self):
        self.assertFalse(inspect([])["ready_for_manual_review"])

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as source:
            result = inspect(json.load(source))
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["ready_for_manual_review"] else 2)
    else:
        print("Usage: python pi_esp32_flash_preflight.py config.json | --self-test", file=sys.stderr)
        sys.exit(2)
