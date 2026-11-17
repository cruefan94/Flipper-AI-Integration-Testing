"""Public-safe, offline peripheral transport contract gate. No I/O or device access."""
from __future__ import annotations
import unittest

ALLOWED = {"ble", "wifi", "usb"}
BOARDS = {"esp32-wroom", "esp32-s2", "arduino-uno", "raspberry-pi-4b"}

def validate_plan(plan: dict) -> list[str]:
    """Return violations; passing is not permission to connect or flash."""
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    if plan.get("schema_version") != 1:
        errors.append("unsupported schema version")
    if plan.get("board") not in BOARDS:
        errors.append("unsupported board")
    if plan.get("transport") not in ALLOWED:
        errors.append("unsupported transport")
    if plan.get("operation") != "diagnostics-read-only":
        errors.append("only offline diagnostics-read-only is supported")
    if plan.get("hardware_access") is not False:
        errors.append("hardware access must be explicitly disabled")
    if plan.get("radio_tx") is not False:
        errors.append("radio transmission must be explicitly disabled")
    if plan.get("flash") is not False:
        errors.append("flashing must be explicitly disabled")
    if plan.get("transport") == "ble" and plan.get("board") == "arduino-uno":
        errors.append("Uno has no built-in BLE; external adapter needs separate review")
    if plan.get("transport") == "wifi" and plan.get("board") == "arduino-uno":
        errors.append("Uno has no built-in Wi-Fi; external adapter needs separate review")
    if plan.get("transport") == "ble" and plan.get("board") == "esp32-s2":
        errors.append("ESP32-S2 has no built-in Bluetooth radio")
    if any(k in plan for k in ("credentials", "token", "private_key", "firmware", "command", "device_path")):
        errors.append("secret, firmware or executable/device fields forbidden")
    return errors

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(schema_version=1, board="esp32-wroom", transport="ble", operation="diagnostics-read-only", hardware_access=False, radio_tx=False, flash=False)

    def test_valid_wroom_ble(self): self.assertEqual(validate_plan(self.base), [])
    def test_valid_s2_usb(self): self.assertEqual(validate_plan({**self.base, "board":"esp32-s2", "transport":"usb"}), [])
    def test_s2_ble_rejected(self): self.assertIn("ESP32-S2 has no built-in Bluetooth radio", validate_plan({**self.base, "board":"esp32-s2"}))
    def test_uno_wifi_rejected(self): self.assertTrue(validate_plan({**self.base, "board":"arduino-uno", "transport":"wifi"}))
    def test_uno_ble_rejected(self): self.assertTrue(validate_plan({**self.base, "board":"arduino-uno"}))
    def test_uno_usb_allowed(self): self.assertEqual(validate_plan({**self.base, "board":"arduino-uno", "transport":"usb"}), [])
    def test_flash_rejected(self): self.assertTrue(validate_plan({**self.base, "flash":True}))
    def test_radio_tx_rejected(self): self.assertTrue(validate_plan({**self.base, "radio_tx":True}))
    def test_hardware_access_rejected(self): self.assertTrue(validate_plan({**self.base, "hardware_access":True}))
    def test_secret_rejected(self): self.assertTrue(validate_plan({**self.base, "token":"fake"}))
    def test_command_rejected(self): self.assertTrue(validate_plan({**self.base, "command":"noop"}))
    def test_unknown_version_rejected(self): self.assertTrue(validate_plan({**self.base, "schema_version":2}))
    def test_unknown_board_rejected(self): self.assertTrue(validate_plan({**self.base, "board":"unknown"}))
    def test_non_object_rejected(self): self.assertTrue(validate_plan(None))

if __name__ == "__main__":
    unittest.main()
