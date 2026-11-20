#!/usr/bin/env python3
"""Offline, public-safe two-failure routing evidence checker. No GitHub access."""
import argparse
import json
import sys

def evaluate(data):
    runs = data.get("runs")
    if not isinstance(runs, list):
        raise ValueError("runs must be an array")
    seen = set()
    groups = {}
    for r in runs:
        if not isinstance(r, dict):
            raise ValueError("run must be an object")
        required = ("id", "workflow", "branch", "status", "conclusion")
        if any(k not in r for k in required):
            raise ValueError("run missing required field")
        if not isinstance(r["id"], int) or isinstance(r["id"], bool) or r["id"] <= 0 or r["id"] in seen:
            raise ValueError("invalid or duplicate run id")
        seen.add(r["id"])
        if not all(isinstance(r[k], str) and r[k].strip() for k in required[1:]):
            raise ValueError("invalid run metadata")
        if r["status"] != "completed":
            continue
        groups.setdefault((r["workflow"], r["branch"]), []).append(r)
    results = []
    for (workflow, branch), records in sorted(groups.items()):
        # Input order is chronological. A success resets the consecutive-failure count.
        streak = []
        for r in records:
            if r["conclusion"] == "failure":
                streak.append(r["id"])
            else:
                streak = []
        if len(streak) >= 2:
            access = data.get("private_actions_read", "unknown")
            if access not in ("accessible", "blocked", "unknown"):
                raise ValueError("invalid private_actions_read")
            results.append({"workflow": workflow, "branch": branch,
                            "failing_run_ids": streak[-2:],
                            "decision": "FALLBACK_REQUIRED" if access == "accessible" else "BLOCKED",
                            "reason": "private Actions:read unavailable or unverified" if access != "accessible" else "approved public-safe route only"})
    return {"pairs": results, "dispatched": False, "native_build_verified": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="sanitized metadata JSON file")
    args = p.parse_args()
    try:
        with open(args.input, encoding="utf-8") as f:
            result = evaluate(json.load(f))
    except (OSError, ValueError, TypeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    sys.exit(main())
