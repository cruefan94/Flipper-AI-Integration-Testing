#!/usr/bin/env python3
"""PUBLIC-SAFE offline I2C wiring evidence gate. No hardware access."""
import json
import sys

def assess(evidence):
    if not isinstance(evidence, dict):
        return ["evidence must be an object"]
    errors = []
    def require_bool(name):
        if evidence.get(name) is not True:
            errors.append(name + " must be explicitly true")
    require_bool("owner_approved")
    require_bool("schematic_verified")
    require_bool("common_ground_verified")
    require_bool("power_rails_isolated")
    require_bool("pullup_rails_verified")
    rails = evidence.get("sda_pullup_v"), evidence.get("scl_pullup_v")
    for name, value in zip(("sda_pullup_v", "scl_pullup_v"), rails):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 < value <= 3.6):
            errors.append(name + " must be a measured numeric value in (0, 3.6] V")
    if evidence.get("uno_5v_bus_connected") is True:
        require_bool("bidirectional_level_shifter_verified")
        require_bool("shifter_direction_verified")
    elif evidence.get("uno_5v_bus_connected") is not False:
        errors.append("uno_5v_bus_connected must be explicit boolean")
    if evidence.get("board_family") not in ("esp32-wroom", "esp32-s2", "flipper-zero"):
        errors.append("board_family not allowlisted")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: i2c_evidence_gate.py evidence.json", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as exc:
        print("REJECT: invalid or unreadable evidence", file=sys.stderr)
        return 2
    errors = assess(data)
    print(json.dumps({"status": "REJECT" if errors else "OFFLINE_PRECHECK_ONLY",
                      "errors": errors}, sort_keys=True))
    return 2 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
