"""Offline backpack power-budget preflight. Never opens hardware or serial ports."""
import json
import sys


def evaluate(spec):
    errors = []
    if not isinstance(spec, dict):
        return ["spec must be an object"]
    rails = spec.get("rails")
    if not isinstance(rails, list) or not rails:
        return ["nonempty rails list required"]
    names = set()
    for rail in rails:
        if not isinstance(rail, dict):
            errors.append("rail must be object")
            continue
        name = rail.get("name")
        if not isinstance(name, str) or not name.strip() or name in names:
            errors.append("rail name missing or duplicated")
            continue
        names.add(name)
        voltage = rail.get("voltage_v")
        limit = rail.get("continuous_limit_ma")
        loads = rail.get("loads")
        if type(voltage) not in (int, float) or not 0 < voltage <= 24:
            errors.append(f"{name}: invalid voltage")
        if type(limit) not in (int, float) or not 0 < limit <= 10000:
            errors.append(f"{name}: invalid continuous limit")
        if not isinstance(loads, list) or not loads:
            errors.append(f"{name}: load list required")
            continue
        total = 0
        for load in loads:
            if not isinstance(load, dict) or not isinstance(load.get("name"), str) or not load["name"].strip():
                errors.append(f"{name}: invalid load identity")
                continue
            draw = load.get("peak_ma")
            if type(draw) not in (int, float) or not 0 <= draw <= 10000:
                errors.append(f"{name}: {load['name']} missing/invalid peak_ma")
            else:
                total += draw
        if type(limit) in (int, float) and total > limit * 0.8:
            errors.append(f"{name}: peak load {total:g}mA exceeds 80% planning allowance {limit * .8:g}mA")
        if rail.get("backfeed_isolation_verified") is not True:
            errors.append(f"{name}: backfeed isolation unverified")
        if rail.get("common_ground_reviewed") is not True:
            errors.append(f"{name}: ground topology unreviewed")
    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python backpack_budget.py proposed_wiring.json", file=sys.stderr)
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            spec = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"BLOCK: invalid input: {exc}", file=sys.stderr)
        return 2
    errors = evaluate(spec)
    print("BLOCKED: " + "; ".join(errors) if errors else "PASS: offline planning checks only; physical review still required")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
