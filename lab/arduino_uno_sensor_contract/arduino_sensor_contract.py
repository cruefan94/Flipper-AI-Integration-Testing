"""Offline public-safe Arduino Uno sensor manifest gate; never accesses devices."""
import json
import sys

def validate(m):
    if not isinstance(m, dict) or m.get("board") != "arduino_uno_5v":
        return ["board must be arduino_uno_5v"]
    sensors = m.get("sensors")
    if not isinstance(sensors, list) or not sensors:
        return ["sensors must be nonempty"]
    errors, used = [], set()
    for i, s in enumerate(sensors):
        p = f"sensors[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{p}: invalid entry")
            continue
        pin = s.get("pin")
        valid = (type(pin) is int and 2 <= pin <= 13) or (isinstance(pin, str) and pin in {f"A{j}" for j in range(6)})
        if not valid:
            errors.append(f"{p}: invalid/reserved pin")
            continue
        if pin in used:
            errors.append(f"{p}: duplicate pin")
        used.add(pin)
        if s.get("direction") != "input":
            errors.append(f"{p}: only input permitted")
        v = s.get("signal_max_v")
        if type(v) not in (int, float) or not 0 <= v <= 5:
            errors.append(f"{p}: voltage out of range")
        if s.get("externally_powered") is True and s.get("common_ground_verified") is not True:
            errors.append(f"{p}: ground not verified")
        if s.get("connected_to_3v3_device") is True and s.get("level_shifter_verified") is not True:
            errors.append(f"{p}: level shifter not verified")
    return errors

def main():
    if len(sys.argv) != 2:
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return 2
    errors = validate(data)
    print(json.dumps({"status": "REJECT" if errors else "PASS_OFFLINE_ONLY", "errors": errors}))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
