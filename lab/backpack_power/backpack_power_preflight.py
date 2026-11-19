"""Offline, conservative power-domain preflight for modular Flipper backpacks.

This tool never connects to hardware. Unknown board variants require schematic review.
Run: python3 -m unittest discover -s lab/backpack_power -p 'test_*.py'
"""
from dataclasses import dataclass

ALLOWED = {"flipper_zero", "esp32_wroom", "esp32_s2", "arduino_uno"}
MAX_MODULES = 8

@dataclass(frozen=True)
class Module:
    board: str
    supply_v: float
    gpio_v: float
    estimated_ma: int
    powered_from: str = "external"  # external or flipper_3v3

def preflight(modules, *, common_ground_confirmed=False, level_shifters_confirmed=False):
    """Return (approved_for_review, reason codes); never authorizes physical wiring."""
    errors = []
    if not isinstance(modules, (list, tuple)) or not 1 <= len(modules) <= MAX_MODULES:
        return False, ["invalid_module_count"]
    if not common_ground_confirmed:
        errors.append("ground_unconfirmed")
    for i, m in enumerate(modules):
        if not isinstance(m, Module) or m.board not in ALLOWED:
            errors.append(f"module_{i}_unknown")
            continue
        if m.supply_v not in (3.3, 5.0) or m.gpio_v not in (3.3, 5.0):
            errors.append(f"module_{i}_voltage_unknown")
        if type(m.estimated_ma) is not int or not 0 <= m.estimated_ma <= 2000:
            errors.append(f"module_{i}_current_unknown")
        if m.powered_from not in ("external", "flipper_3v3"):
            errors.append(f"module_{i}_power_source_unknown")
        if m.powered_from == "flipper_3v3":
            errors.append(f"module_{i}_flipper_power_requires_measurement")
        if m.board in ("esp32_wroom", "esp32_s2", "flipper_zero") and m.gpio_v != 3.3:
            errors.append(f"module_{i}_unsafe_gpio")
        if m.board == "arduino_uno" and m.gpio_v == 5.0 and not level_shifters_confirmed:
            errors.append(f"module_{i}_level_shift_required")
    # No inferred current capacity: even clean results are review-only.
    return not errors, errors

if __name__ == "__main__":
    print("Offline library only; use unittest to validate. No wiring approval.")
