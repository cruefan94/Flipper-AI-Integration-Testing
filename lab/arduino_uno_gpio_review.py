"""Offline Arduino Uno GPIO wiring-plan review. No serial, GPIO, or hardware I/O."""
from __future__ import annotations
import json
import sys

UNO_DIGITAL = set(range(14))
UNO_ANALOG = set(range(6))
RESERVED = {0, 1}  # UART RX/TX: avoid conflicts with serial upload/diagnostics

def review(plan: dict) -> list[str]:
    errors = []
    if not isinstance(plan, dict):
        return ["plan must be an object"]
    if plan.get("board") != "arduino-uno-r3":
        errors.append("unsupported board")
    if plan.get("mode") != "offline-review":
        errors.append("hardware operation not permitted")
    devices = plan.get("devices")
    if not isinstance(devices, list) or not devices:
        return errors + ["nonempty devices list required"]
    occupied = set()
    for index, device in enumerate(devices):
        prefix = f"devices[{index}]"
        if not isinstance(device, dict):
            errors.append(f"{prefix}: invalid device")
            continue
        pin = device.get("pin")
        kind = device.get("kind")
        voltage = device.get("signal_voltage")
        if kind not in ("digital-input", "analog-input"):
            errors.append(f"{prefix}: only passive input review supported")
            continue
        if type(pin) is not int or (kind == "digital-input" and pin not in UNO_DIGITAL) or (kind == "analog-input" and pin not in UNO_ANALOG):
            errors.append(f"{prefix}: invalid pin")
            continue
        key = ("D" if kind == "digital-input" else "A", pin)
        if key in occupied:
            errors.append(f"{prefix}: duplicate pin")
        occupied.add(key)
        if kind == "digital-input" and pin in RESERVED:
            errors.append(f"{prefix}: serial pins D0/D1 reserved")
        if type(voltage) not in (int, float) or not 0 <= voltage <= 5:
            errors.append(f"{prefix}: signal voltage outside 0..5V")
        if device.get("common_ground_verified") is not True:
            errors.append(f"{prefix}: common ground not verified")
    return errors

def main() -> int:
    try:
        plan = json.load(sys.stdin)
    except (ValueError, UnicodeError):
        print(json.dumps({"accepted": False, "errors": ["invalid JSON"]}))
        return 2
    errors = review(plan)
    print(json.dumps({"accepted": not errors, "errors": errors}, sort_keys=True))
    return 0 if not errors else 2

if __name__ == "__main__":
    raise SystemExit(main())
