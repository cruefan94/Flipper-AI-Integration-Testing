"""Offline wiring contract for Arduino Uno ↔ ESP32 / Flipper lab prototypes.

No GPIO access, serial IO, flashing, or device control. Voltage is evaluated
at the RECEIVING pin. Unknown hardware is deliberately rejected.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Pin:
    board: str
    name: str
    direction: str
    high_volts: float
    tolerant_volts: float

def check_signal(source: Pin, sink: Pin, *, level_shifter: bool = False) -> dict:
    """Return a conservative wiring verdict, never a hardware authorization."""
    if source.direction != "out" or sink.direction != "in":
        return {"safe": False, "reason": "direction_mismatch"}
    if source.board not in {"uno", "esp32", "flipper"} or sink.board not in {"uno", "esp32", "flipper"}:
        return {"safe": False, "reason": "unknown_board"}
    if source.high_volts <= 0 or sink.tolerant_volts <= 0:
        return {"safe": False, "reason": "unknown_voltage"}
    if source.high_volts > sink.tolerant_volts:
        return {"safe": False, "reason": "requires_verified_level_shifter" if level_shifter else "overvoltage"}
    return {"safe": True, "reason": "signal_voltage_within_declared_limit"}

UNO_DIGITAL_OUT = Pin("uno", "D2", "out", 5.0, 5.0)
ESP32_GPIO_IN = Pin("esp32", "GPIO16", "in", 3.3, 3.3)
FLIPPER_GPIO_IN = Pin("flipper", "GPIO", "in", 3.3, 3.3)

# IMPORTANT: This checks only logic high voltage, not wiring correctness,
# current draw, shared ground, power rails, bootstrapping, or pin availability.
# Flipper GPIO and ESP32 GPIO are NOT 5 V tolerant. Do not connect Uno 5 V
# outputs directly. A level_shifter=True flag never bypasses the voltage gate.
