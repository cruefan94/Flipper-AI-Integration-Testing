"""Offline Arduino Uno R3 input-only sensor wiring review; no hardware I/O."""
import math

VALID = {f"D{i}" for i in range(2, 14)} | {f"A{i}" for i in range(6)}
ANALOG = {f"A{i}" for i in range(6)}

def review(plan):
    if not isinstance(plan, dict) or plan.get("board") != "arduino-uno-r3":
        return ["unsupported board"]
    errors = []
    if plan.get("operation") != "review-only":
        errors.append("review-only required")
    if plan.get("common_ground_verified") is not True:
        errors.append("common ground unverified")
    sensors = plan.get("sensors")
    if not isinstance(sensors, list) or not sensors:
        return errors + ["nonempty sensors required"]
    seen = set()
    for i, s in enumerate(sensors):
        if not isinstance(s, dict):
            errors.append(f"{i}: invalid sensor")
            continue
        pin = s.get("pin")
        if not isinstance(pin, str) or pin not in VALID:
            errors.append(f"{i}: invalid/reserved pin")
        elif pin in seen:
            errors.append(f"{i}: duplicate pin")
        else:
            seen.add(pin)
        mode = s.get("mode")
        if mode not in ("digital-input", "analog-input"):
            errors.append(f"{i}: output/unknown mode")
        if mode == "analog-input" and pin not in ANALOG:
            errors.append(f"{i}: analog input requires A0-A5")
        voltage = s.get("signal_voltage")
        if isinstance(voltage, bool) or not isinstance(voltage, (int, float)) or not math.isfinite(voltage) or not 0 <= voltage <= 5:
            errors.append(f"{i}: invalid signal voltage")
    return errors
