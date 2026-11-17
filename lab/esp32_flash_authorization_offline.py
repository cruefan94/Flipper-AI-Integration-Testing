"""Offline ESP32 flash authorization policy. No serial or subprocess operations."""
from dataclasses import dataclass
import unittest

SUPPORTED = {"esp32-wroom", "esp32-s2"}

@dataclass(frozen=True)
class Evidence:
    board: str
    port_identity_verified: bool
    rom_handshake_verified: bool
    image_sha256_verified: bool
    explicit_owner_approval: bool
    power_and_voltage_reviewed: bool
    requested_operation: str

def assess(e: Evidence) -> tuple[bool, tuple[str, ...]]:
    """Fail closed; a positive result is review eligibility, NOT flash permission."""
    blockers = []
    if e.board not in SUPPORTED:
        blockers.append("unknown_board")
    if not e.port_identity_verified:
        blockers.append("unverified_port")
    if not e.rom_handshake_verified:
        blockers.append("missing_rom_handshake")
    if not e.image_sha256_verified:
        blockers.append("unverified_image")
    if not e.explicit_owner_approval:
        blockers.append("no_owner_approval")
    if not e.power_and_voltage_reviewed:
        blockers.append("power_review_missing")
    if e.requested_operation != "offline_review":
        blockers.append("operation_not_permitted")
    return not blockers, tuple(blockers)

class Tests(unittest.TestCase):
    def good(self, **changes):
        fields = dict(board="esp32-wroom", port_identity_verified=True,
                      rom_handshake_verified=True, image_sha256_verified=True,
                      explicit_owner_approval=True, power_and_voltage_reviewed=True,
                      requested_operation="offline_review")
        fields.update(changes)
        return Evidence(**fields)

    def test_complete_evidence_only_allows_offline_review(self):
        self.assertEqual(assess(self.good()), (True, ()))

    def test_missing_approval(self):
        self.assertIn("no_owner_approval", assess(self.good(explicit_owner_approval=False))[1])

    def test_unverified_identity(self):
        self.assertIn("unverified_port", assess(self.good(port_identity_verified=False))[1])

    def test_no_rom_handshake(self):
        self.assertIn("missing_rom_handshake", assess(self.good(rom_handshake_verified=False))[1])

    def test_unverified_image(self):
        self.assertIn("unverified_image", assess(self.good(image_sha256_verified=False))[1])

    def test_unknown_board(self):
        self.assertIn("unknown_board", assess(self.good(board="esp8266"))[1])

    def test_s2_supported_for_review(self):
        self.assertTrue(assess(self.good(board="esp32-s2"))[0])

    def test_flash_operation_always_denied(self):
        self.assertIn("operation_not_permitted", assess(self.good(requested_operation="flash"))[1])

    def test_power_review_required(self):
        self.assertIn("power_review_missing", assess(self.good(power_and_voltage_reviewed=False))[1])

    def test_multiple_failures_retained(self):
        ok, reasons = assess(self.good(port_identity_verified=False, explicit_owner_approval=False))
        self.assertFalse(ok)
        self.assertEqual(set(reasons), {"unverified_port", "no_owner_approval"})

if __name__ == "__main__":
    unittest.main()
