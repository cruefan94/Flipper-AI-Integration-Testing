"""Offline, fail-closed wiring review for Arduino/ESP32/Flipper GPIO prototypes.

This is NOT an electrical certification or permission to connect hardware.
No device access, imports from hardware libraries, or flashing operations.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Pin:
    board: str
    name: str
    voltage: Optional[float]
    direction: str  # "out", "in", "bidirectional", "power", "ground"
    verified: bool = False

def review_connection(source: Pin, target: Pin, level_shifter_verified: bool = False) -> dict:
    reasons = []
    if source.board not in {"arduino_uno", "esp32_wroom", "esp32_s2", "flipper_zero"} or target.board not in {"arduino_uno", "esp32_wroom", "esp32_s2", "flipper_zero"}:
        reasons.append("unknown_board")
    if not source.verified or not target.verified:
        reasons.append("pin_identity_unverified")
    if source.direction not in {"out", "in", "bidirectional", "power", "ground"} or target.direction not in {"out", "in", "bidirectional", "power", "ground"}:
        reasons.append("unknown_direction")
    if source.direction == "power" or target.direction == "power":
        reasons.append("power_connection_requires_separate_review")
    if source.direction == "ground" or target.direction == "ground":
        reasons.append("grounding_requires_separate_review")
    if source.direction not in {"out", "bidirectional"} or target.direction not in {"in", "bidirectional"}:
        reasons.append("direction_mismatch")
    if source.voltage is None or target.voltage is None or source.voltage < 0 or target.voltage <= 0:
        reasons.append("voltage_unknown")
    elif source.voltage > target.voltage and not level_shifter_verified:
        reasons.append("overvoltage_without_verified_level_shifter")
    if source.direction == "bidirectional" or target.direction == "bidirectional":
        reasons.append("bidirectional_interface_requires_review")
    # Even a passing static review is only a candidate for manual electrical review.
    return {"static_review_pass": not reasons, "hardware_authorized": False, "reasons": reasons}
