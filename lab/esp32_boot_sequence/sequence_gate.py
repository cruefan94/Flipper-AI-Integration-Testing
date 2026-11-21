"""Offline ESP32 classic BOOT/EN observation sequence checker.

Public-safe synthetic observations only. No GPIO, USB, serial or flashing access.
ESP32-S2 is intentionally not interpreted using classic ESP32 assumptions.
Run: python3 -m unittest discover -s lab/esp32_boot_sequence -p 'test_*.py'
"""
from dataclasses import dataclass

STATES = {"high", "low", "unknown"}

@dataclass(frozen=True)
class Observation:
    en: str
    gpio0: str
    power_confirmed: bool


def evaluate(family: str, observations: list[Observation]) -> dict:
    if family not in {"esp32", "esp32-s2"}:
        return {"status": "blocked", "reason": "unknown chip family"}
    if family != "esp32":
        return {"status": "manual-review", "reason": "ESP32-S2 needs its own verified strap specification"}
    if not observations or len(observations) > 16:
        return {"status": "blocked", "reason": "missing or excessive observations"}
    for item in observations:
        if not isinstance(item, Observation) or item.en not in STATES or item.gpio0 not in STATES or type(item.power_confirmed) is not bool:
            return {"status": "blocked", "reason": "invalid observation"}
        if not item.power_confirmed:
            return {"status": "blocked", "reason": "power not confirmed"}
    if any(x.en == "unknown" or x.gpio0 == "unknown" for x in observations):
        return {"status": "inconclusive", "reason": "unknown pin state"}
    # BOOT strap must be low when EN rises. Observations are not a timing trace:
    # they cannot prove the chip entered download mode or that USB is functional.
    for previous, current in zip(observations, observations[1:]):
        if previous.en == "low" and current.en == "high":
            if current.gpio0 == "low" and previous.gpio0 == "low":
                return {"status": "candidate", "reason": "observed low GPIO0 across EN release; ROM log verification required"}
            return {"status": "not-observed", "reason": "GPIO0 low across EN release not observed"}
    return {"status": "inconclusive", "reason": "EN low-to-high transition not observed"}
