#!/usr/bin/env python3
"""Fail-closed, offline, public-safe CI fallback evidence validator.

Usage: python scripts/validate_fallback_evidence.py evidence.json
Only sanitized run IDs, branch names, workflow names and status fields belong
in input. Never include private logs, tokens, source, artifacts or diagnostics.
"""
import json
import sys
from pathlib import Path


def validate(record):
    errors = []
    failures = record.get("failures")
    if not isinstance(failures, list) or len(failures) < 2:
        return ["at least two completed failures are required"]
    pair = failures[-2:]
    for index, item in enumerate(pair):
        if not isinstance(item, dict):
            return ["failure entries must be objects"]
        if item.get("status") != "completed" or item.get("conclusion") != "failure":
            errors.append(f"failure {index + 1} is not a completed failure")
        if not isinstance(item.get("run_id"), int) or item["run_id"] <= 0:
            errors.append(f"failure {index + 1} lacks a valid run ID")
        if not item.get("workflow") or not item.get("branch"):
            errors.append(f"failure {index + 1} lacks workflow/branch")
    if pair[0].get("workflow") != pair[1].get("workflow"):
        errors.append("failure workflow mismatch")
    if pair[0].get("branch") != pair[1].get("branch"):
        errors.append("failure branch mismatch")
    if pair[0].get("run_id") == pair[1].get("run_id"):
        errors.append("failure run IDs must be distinct")
    fallback = record.get("fallback")
    if not isinstance(fallback, dict):
        return errors + ["fallback object is required"]
    state = fallback.get("state")
    if state not in ("BLOCKED", "DISPATCHED", "COMPLETED"):
        errors.append("fallback state must be BLOCKED, DISPATCHED or COMPLETED")
    if state == "BLOCKED":
        if fallback.get("run_id"):
            errors.append("blocked fallback must not claim a run ID")
        if not fallback.get("reason"):
            errors.append("blocked fallback needs a reason")
    elif state in ("DISPATCHED", "COMPLETED"):
        if not isinstance(fallback.get("run_id"), int) or fallback["run_id"] <= 0:
            errors.append("dispatched fallback needs a real run ID")
        if not fallback.get("url", "").startswith("https://github.com/"):
            errors.append("dispatched fallback needs an Actions URL")
        if state == "COMPLETED" and fallback.get("conclusion") not in ("success", "failure", "cancelled"):
            errors.append("completed fallback needs a terminal conclusion")
    if record.get("release_ready") is True:
        errors.append("fallback evidence alone cannot authorize release readiness")
    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: validate_fallback_evidence.py <sanitized.json>", file=sys.stderr)
        return 2
    try:
        record = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        errors = validate(record)
    except (OSError, ValueError, TypeError) as exc:
        print(f"invalid evidence: {type(exc).__name__}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}", file=sys.stderr)
        return 1
    print("Evidence structure valid; no source, artifact, hardware or release verification implied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
