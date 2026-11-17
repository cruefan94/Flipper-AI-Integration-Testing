"""Offline ESP32-WROOM boot-strap review. Never opens ports or flashes hardware.

Input is an operator-observed snapshot, not a hardware command. GPIO0 low
during reset selects UART download mode on classic ESP32; EN must be high
after reset release. ESP32-S2 is intentionally not covered by this model.
"""
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Snapshot:
    board: str
    en: str
    gpio0: str
    supply_v: float
    ground_shared: bool
    uart_voltage_v: float
    serial_identity_confirmed: bool

def review(s: Snapshot) -> tuple[str, tuple[str, ...]]:
    reasons = []
    if s.board != "ESP32-WROOM":
        reasons.append("unsupported board; separate S2 procedure required")
    if s.en not in ("high", "low", "unknown") or s.gpio0 not in ("high", "low", "unknown"):
        reasons.append("invalid logic observation")
    if not 3.0 <= s.supply_v <= 3.6:
        reasons.append("supply outside nominal 3.3V domain; verify board regulator")
    if not 0 <= s.uart_voltage_v <= 3.6:
        reasons.append("UART level unsafe or unknown")
    if not s.ground_shared:
        reasons.append("common ground unverified")
    if not s.serial_identity_confirmed:
        reasons.append("serial device identity unverified")
    if s.en == "unknown" or s.gpio0 == "unknown":
        reasons.append("boot strap observation incomplete")
    if reasons:
        return ("BLOCKED", tuple(reasons))
    if s.en == "low":
        return ("RESET_HELD", ("EN low keeps chip in reset",))
    if s.gpio0 == "low":
        return ("DOWNLOAD_MODE_EXPECTED", ("GPIO0 low at reset release requests ROM download mode; no flash authorization",))
    return ("NORMAL_BOOT_EXPECTED", ("GPIO0 high at reset release requests normal boot; no flash authorization",))

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(board="ESP32-WROOM", en="high", gpio0="low",
                         supply_v=3.3, ground_shared=True, uart_voltage_v=3.3,
                         serial_identity_confirmed=True)
    def check(self, status, **changes):
        self.assertEqual(review(Snapshot(**(self.good | changes)))[0], status)
    def test_download(self): self.check("DOWNLOAD_MODE_EXPECTED")
    def test_normal(self): self.check("NORMAL_BOOT_EXPECTED", gpio0="high")
    def test_reset(self): self.check("RESET_HELD", en="low")
    def test_s2(self): self.check("BLOCKED", board="ESP32-S2")
    def test_5v_uart(self): self.check("BLOCKED", uart_voltage_v=5.0)
    def test_5v_supply(self): self.check("BLOCKED", supply_v=5.0)
    def test_no_ground(self): self.check("BLOCKED", ground_shared=False)
    def test_unknown_identity(self): self.check("BLOCKED", serial_identity_confirmed=False)
    def test_unknown_gpio0(self): self.check("BLOCKED", gpio0="unknown")
    def test_unknown_en(self): self.check("BLOCKED", en="unknown")
    def test_invalid_logic(self): self.check("BLOCKED", gpio0="floating")
    def test_negative_uart(self): self.check("BLOCKED", uart_voltage_v=-1)

if __name__ == "__main__":
    unittest.main()
