"""Offline, fail-closed voltage-domain review for a proposed Flipper/ESP32/Uno backpack.

Only consumes synthetic or owner-entered JSON; never accesses devices or ports.
This is not a substitute for board schematics or electrical measurement.
"""
import argparse
import json
from pathlib import Path

ALLOWED = {"flipper_gpio", "esp32_wroom", "esp32_s2", "arduino_uno"}
LOGIC = {"flipper_gpio": 3.3, "esp32_wroom": 3.3, "esp32_s2": 3.3, "arduino_uno": 5.0}


def review(plan):
    if not isinstance(plan, dict) or set(plan) != {"connections"}:
        return ["invalid plan structure"]
    links = plan["connections"]
    if not isinstance(links, list) or not links:
        return ["missing connections"]
    issues = []
    for i, link in enumerate(links):
        if not isinstance(link, dict) or set(link) != {"source", "target", "signal", "level_shifter_verified", "common_ground_verified"}:
            issues.append(f"link {i}: incomplete or extra fields")
            continue
        a, b, signal = link["source"], link["target"], link["signal"]
        if a not in ALLOWED or b not in ALLOWED or a == b:
            issues.append(f"link {i}: unknown or duplicate endpoints")
            continue
        if signal not in ("gpio", "uart", "i2c"):
            issues.append(f"link {i}: power and other signals require schematic review")
            continue
        if link["common_ground_verified"] is not True:
            issues.append(f"link {i}: common ground not verified")
        if LOGIC[a] > LOGIC[b] and link["level_shifter_verified"] is not True:
            issues.append(f"link {i}: source logic exceeds target; level shifting unverified")
        if LOGIC[a] <= LOGIC[b] and link["level_shifter_verified"] not in (True, False):
            issues.append(f"link {i}: invalid level shifter flag")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Offline wiring preflight; no hardware access")
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        issues = review(plan)
    except (OSError, ValueError) as exc:
        print("BLOCKED: cannot read valid JSON plan")
        return 2
    if issues:
        print("BLOCKED: " + "; ".join(issues))
        return 2
    print("REVIEW ONLY: logic-direction checks passed; board schematic, current limits, power rails, pin strapping and owner measurement still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
