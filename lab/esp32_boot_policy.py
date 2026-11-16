"""Offline ESP32 ROM-download strap-state review. Never accesses GPIO or serial hardware.

This is a planning aid, not a wiring, voltage, or flashing authorization.
GPIO0 must be LOW at the reset sampling instant to request UART download mode
on classic ESP32 and ESP32-S2; other strapping pins and board circuits matter.
"""
from dataclasses import dataclass

SUPPORTED = frozenset({"esp32", "esp32s2"})
STATES = frozenset({"LOW", "HIGH", "RELEASED", "UNKNOWN"})

@dataclass(frozen=True)
class Observation:
    chip: str
    gpio0_at_reset: str
    reset_was_asserted: bool
    reset_was_released: bool
    uart_port_identified: bool

def review(observation: Observation) -> dict:
    """Return a conservative, non-authorizing diagnosis of recorded states."""
    if not isinstance(observation, Observation):
        raise TypeError("Observation required")
    if observation.chip not in SUPPORTED:
        return {"status": "BLOCKED", "reason": "unsupported chip family"}
    if observation.gpio0_at_reset not in STATES:
        return {"status": "BLOCKED", "reason": "invalid GPIO0 observation"}
    if not observation.reset_was_asserted or not observation.reset_was_released:
        return {"status": "INCOMPLETE", "reason": "complete reset pulse not observed"}
    if observation.gpio0_at_reset != "LOW":
        return {"status": "NOT_CONFIRMED", "reason": "GPIO0 LOW at reset release not confirmed"}
    if not observation.uart_port_identified:
        return {"status": "INCOMPLETE", "reason": "UART adapter identity unverified"}
    return {"status": "POSSIBLE", "reason": "strap observations consistent with ROM download request; no chip handshake verified"}
