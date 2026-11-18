"""Offline transport admission gate for optional Flipper/Pi/ESP32 peripherals.

Public-safe fixtures only. No radio, serial, network or device I/O.
"""
from dataclasses import dataclass
import unittest

TRANSPORTS = {"ble", "wifi", "usb"}
FAMILIES = {"esp32-wroom", "esp32-s2", "arduino-uno"}
READ_ONLY = {"identify", "diagnose", "telemetry"}
WRITE = {"program", "reset", "gpio-write"}

@dataclass(frozen=True)
class Request:
    family: str
    transport: str
    action: str
    owner_authorized: bool = False
    stable_identity: bool = False
    voltage_verified: bool = False
    common_ground_verified: bool = False
    bootloader_verified: bool = False
    physical_presence_verified: bool = False
    firmware_hash_verified: bool = False

def admit(request: Request) -> tuple[bool, str]:
    if request.family not in FAMILIES:
        return False, "unknown-family"
    if request.transport not in TRANSPORTS:
        return False, "unsupported-transport"
    if request.action not in READ_ONLY | WRITE:
        return False, "unknown-action"
    if not request.stable_identity:
        return False, "unstable-identity"
    if request.action in WRITE:
        # This lab gate NEVER authorizes write operations; future implementation
        # must require separate owner-reviewed physical execution controls.
        return False, "write-disabled-in-lab"
    if request.action == "diagnose" and request.transport == "wifi":
        return False, "wifi-diagnostics-not-validated"
    return True, "read-only-admitted"

class PolicyTests(unittest.TestCase):
    def base(self, **changes):
        data = dict(family="esp32-wroom", transport="usb",
                    action="identify", stable_identity=True)
        data.update(changes)
        return Request(**data)

    def test_read_only_usb(self):
        self.assertEqual(admit(self.base()), (True, "read-only-admitted"))

    def test_read_only_ble(self):
        self.assertTrue(admit(self.base(transport="ble"))[0])

    def test_wifi_diagnose_blocked(self):
        self.assertFalse(admit(self.base(transport="wifi", action="diagnose"))[0])

    def test_unknown_family(self):
        self.assertFalse(admit(self.base(family="esp8266"))[0])

    def test_unknown_transport(self):
        self.assertFalse(admit(self.base(transport="uart"))[0])

    def test_unknown_action(self):
        self.assertFalse(admit(self.base(action="transmit"))[0])

    def test_identity_required(self):
        self.assertFalse(admit(self.base(stable_identity=False))[0])

    def test_all_write_actions_denied_even_if_authorized(self):
        for action in WRITE:
            with self.subTest(action=action):
                req = self.base(action=action, owner_authorized=True,
                    voltage_verified=True, common_ground_verified=True,
                    bootloader_verified=True, physical_presence_verified=True,
                    firmware_hash_verified=True)
                self.assertEqual(admit(req), (False, "write-disabled-in-lab"))

    def test_arduino_read_only(self):
        self.assertTrue(admit(self.base(family="arduino-uno"))[0])

    def test_s2_read_only(self):
        self.assertTrue(admit(self.base(family="esp32-s2"))[0])

if __name__ == "__main__":
    unittest.main()
