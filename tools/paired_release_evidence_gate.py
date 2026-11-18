#!/usr/bin/env python3
"""Offline, public-safe evidence gate. Input is sanitized metadata ONLY.

This tool does not inspect binaries or attest their contents. A PASS means the
provided evidence manifest meets the required shape and release prerequisites.
Never put private source, firmware binaries, credentials or device logs here.
"""
import json
import sys
from pathlib import Path

REQUIRED_JOBS = {
    "firmware": ("native_compile", "updater_package", "real_dfu_crc", "sha256_verify", "c2_memory_gate"),
    "android": ("apk_compile", "apk_integrity", "signer_match", "version_code_increase"),
    "paired": ("ai1_contract",),
}

def validate(evidence):
    errors = []
    if not isinstance(evidence, dict):
        return ["evidence must be a JSON object"]
    for component in ("firmware", "android"):
        data = evidence.get(component)
        if not isinstance(data, dict):
            errors.append(component + ": missing object")
            continue
        for field in ("repository", "commit_sha", "workflow_run_url"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(component + ": missing " + field)
        sha = data.get("commit_sha", "")
        if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha.lower()):
            errors.append(component + ": commit_sha must be full 40-hex SHA")
        url = data.get("workflow_run_url", "")
        if not isinstance(url, str) or not url.startswith("https://github.com/") or "/actions/runs/" not in url:
            errors.append(component + ": invalid workflow_run_url")
    for section, jobs in REQUIRED_JOBS.items():
        job_results = evidence.get(section, {}).get("jobs", {}) if isinstance(evidence.get(section), dict) else {}
        for job in jobs:
            if job_results.get(job) != "success":
                errors.append(section + "." + job + ": must be executed success (not skipped)")
    if evidence.get("hardware_verified") is not True:
        errors.append("hardware_verified: required for physical release acceptance")
    if evidence.get("owner_approved") is not True:
        errors.append("owner_approved: required for deployment")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 paired_release_evidence_gate.py sanitized-evidence.json", file=sys.stderr)
        return 2
    try:
        evidence = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("BLOCKED: invalid or missing evidence JSON: " + str(exc), file=sys.stderr)
        return 2
    errors = validate(evidence)
    if errors:
        print("HOLD: " + "; ".join(errors))
        return 1
    print("EVIDENCE GATE PASS: metadata only; verify artifact authenticity independently")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
