#!/usr/bin/env python3
"""Offline, fail-closed I2C pull-up review. Never probes hardware."""
import json
import math
import sys

TARGETS = {"esp32-wroom", "esp32-s2", "raspberry-pi-4b", "flipper-zero"}
MAX_INPUT_V = 3.6  # conservative review threshold, NOT a board-specific rating

def review(record):
    if not isinstance(record, dict) or set(record) != {"target", "sda_pullup_v", "scl_pullup_v", "common_ground", "level_shifter"}:
        return {"decision": "BLOCK", "reasons": ["invalid or incomplete schema"]}
    if record["target"] not in TARGETS:
        return {"decision": "BLOCK", "reasons": ["unknown target"]}
    if type(record["common_ground"]) is not bool or type(record["level_shifter"]) is not bool:
        return {"decision": "BLOCK", "reasons": ["boolean flags required"]}
    for key in ("sda_pullup_v", "scl_pullup_v"):
        v = record[key]
        if type(v) not in (float, int) or not math.isfinite(v) or v <= 0 or v > 24:
            return {"decision": "BLOCK", "reasons": ["invalid " + key]}
    reasons = []
    if not record["common_ground"]:
        reasons.append("ground reference not confirmed")
    if any(record[k] > MAX_INPUT_V for k in ("sda_pullup_v", "scl_pullup_v")):
        reasons.append("pull-up exceeds conservative 3.6V review threshold")
    if record["level_shifter"]:
        reasons.append("level shifter topology and both-side pull-ups require schematic review")
    if abs(record["sda_pullup_v"] - record["scl_pullup_v"]) > 0.2:
        reasons.append("SDA/SCL pull-up rail mismatch")
    if not reasons:
        reasons.append("voltage screen passed; device electrical compatibility remains unverified")
    return {"decision": "BLOCK" if len(reasons) > 1 or reasons[0] != "voltage screen passed; device electrical compatibility remains unverified" else "REVIEW", "reasons": reasons}

def main():
    try:
        data = json.load(sys.stdin)
        print(json.dumps(review(data), sort_keys=True))
    except (ValueError, TypeError, RecursionError):
        print(json.dumps({"decision": "BLOCK", "reasons": ["invalid JSON"]}))
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
