"""Offline ESP32-WROOM EN/GPIO0 trace review. No hardware access or flash authority."""
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Sample:
    en: float
    gpio0: float
    uart_voltage: float
    ground_verified: bool
    board: str = "ESP32-WROOM"

def review(samples):
    if not isinstance(samples, (tuple, list)) or len(samples) < 2:
        return "REJECT: insufficient observations"
    for s in samples:
        if not isinstance(s, Sample) or s.board != "ESP32-WROOM":
            return "REJECT: unsupported board or observation"
        if not s.ground_verified:
            return "REJECT: ground not verified"
        if any(type(v) not in (float, int) or not math.isfinite(v) or v < 0 or v > 3.6 for v in (s.en, s.gpio0, s.uart_voltage)):
            return "REJECT: voltage out of supported range"
        if not 2.0 <= s.uart_voltage <= 3.6:
            return "REJECT: UART level requires review"
    reset_seen = any(s.en < 0.8 for s in samples)
    released = [s for s in samples if s.en >= 2.0]
    if not reset_seen or not released:
        return "INDETERMINATE: reset sequence not observed"
    if any(0.8 <= s.en < 2.0 for s in samples):
        return "INDETERMINATE: EN transition unclear"
    if released[-1].gpio0 < 0.8:
        return "REVIEW: download strap indicated; ROM response unverified"
    if released[-1].gpio0 >= 2.0:
        return "REVIEW: normal boot strap indicated; ROM response unverified"
    return "INDETERMINATE: GPIO0 transition unclear"
