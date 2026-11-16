"""Offline ESP32 boot evidence classification. No serial I/O or flashing."""
from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    INSUFFICIENT = "insufficient_evidence"
    BOOT_REQUESTED = "download_mode_requested_not_verified"
    ROM_CONFIRMED = "rom_handshake_observed_not_flash_authorized"


@dataclass(frozen=True)
class BootEvidence:
    board: str
    gpio0_low_at_reset: bool | None
    reset_observed: bool
    rom_sync_reply: bool
    port_identity_verified: bool


def classify(e: BootEvidence) -> Verdict:
    if e.board not in {"esp32", "esp32s2"}:
        return Verdict.INSUFFICIENT
    if not e.port_identity_verified or not e.reset_observed:
        return Verdict.INSUFFICIENT
    if e.gpio0_low_at_reset is not True:
        return Verdict.INSUFFICIENT
    if e.rom_sync_reply:
        return Verdict.ROM_CONFIRMED
    return Verdict.BOOT_REQUESTED


if __name__ == "__main__":
    import unittest

    class OfflineTests(unittest.TestCase):
        def test_no_evidence(self):
            self.assertEqual(classify(BootEvidence("esp32", None, False, False, False)), Verdict.INSUFFICIENT)

        def test_boot_request_not_handshake(self):
            self.assertEqual(classify(BootEvidence("esp32", True, True, False, True)), Verdict.BOOT_REQUESTED)

        def test_rom_reply(self):
            self.assertEqual(classify(BootEvidence("esp32s2", True, True, True, True)), Verdict.ROM_CONFIRMED)

        def test_unverified_port_blocks_confirmation(self):
            self.assertEqual(classify(BootEvidence("esp32", True, True, True, False)), Verdict.INSUFFICIENT)

        def test_gpio_high_blocks_confirmation(self):
            self.assertEqual(classify(BootEvidence("esp32", False, True, True, True)), Verdict.INSUFFICIENT)

        def test_unknown_board(self):
            self.assertEqual(classify(BootEvidence("unknown", True, True, True, True)), Verdict.INSUFFICIENT)

    unittest.main()
