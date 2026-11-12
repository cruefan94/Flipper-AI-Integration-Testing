#!/usr/bin/env python3
"""Conservative, offline unified release readiness verifier."""
import argparse
import json
from pathlib import Path

REQUIRED = ("firmware", "android", "protocol", "hardware_ble", "packaging")

def verify(report):
    failures = []
    for component in REQUIRED:
        item = report.get(component)
        if not isinstance(item, dict):
            failures.append(f"{component}: missing evidence")
            continue
        if item.get("verified") is not True:
            failures.append(f"{component}: not verified")
        if not isinstance(item.get("evidence_url"), str) or not item["evidence_url"].startswith("https://"):
            failures.append(f"{component}: missing HTTPS evidence URL")
    fw = report.get("firmware", {})
    android = report.get("android", {})
    for name, item in (("firmware", fw), ("android", android)):
        sha = item.get("commit_sha", "") if isinstance(item, dict) else ""
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower()):
            failures.append(f"{name}: immutable 40-character commit SHA required")
    return failures

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    failures = verify(report)
    print(json.dumps({"release_ready": not failures, "blockers": failures}, indent=2))
    raise SystemExit(1 if failures else 0)

if __name__ == "__main__":
    main()
