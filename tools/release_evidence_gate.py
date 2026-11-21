#!/usr/bin/env python3
"""Offline PUBLIC-SAFE release-evidence validator. No GitHub/network/device access.

Input must be an explicitly sanitized metadata manifest. Never supply private
firmware hashes, firmware binaries, credentials, or device logs to public CI.
"""
import argparse
import json
import re
import sys

SHA = re.compile(r"^[0-9a-f]{40}$")
HEX256 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = ("source_commit", "ci_run_url", "artifact_sha256", "artifact_kind",
            "real_artifact_crc_verified", "recovery_verified", "hardware_verified")
KINDS = {"android-test-apk", "f7-native-tgz"}

def validate(m):
    if not isinstance(m, dict):
        return ["manifest must be an object"]
    errors = ["missing " + k for k in REQUIRED if k not in m]
    if errors:
        return errors
    if not isinstance(m["source_commit"], str) or not SHA.fullmatch(m["source_commit"]):
        errors.append("source_commit must be a full lowercase commit SHA")
    if not isinstance(m["artifact_sha256"], str) or not HEX256.fullmatch(m["artifact_sha256"]):
        errors.append("artifact_sha256 must be lowercase SHA256")
    url = m["ci_run_url"]
    if not isinstance(url, str) or not re.fullmatch(
        r"https://github\.com/[^/]+/[^/]+/actions/runs/[0-9]+", url):
        errors.append("ci_run_url must identify an exact GitHub Actions run")
    if m["artifact_kind"] not in KINDS:
        errors.append("unrecognized artifact_kind")
    for k in ("real_artifact_crc_verified", "recovery_verified", "hardware_verified"):
        if type(m[k]) is not bool:
            errors.append(k + " must be boolean")
    if m["artifact_kind"] == "f7-native-tgz" and m["real_artifact_crc_verified"] is not True:
        errors.append("F7 real-artifact DFU CRC evidence missing")
    if m["artifact_kind"] == "android-test-apk":
        for k in ("signing_compatible", "version_code_increases"):
            if type(m.get(k)) is not bool or m[k] is not True:
                errors.append("Android " + k + " evidence missing")
    if m["recovery_verified"] is not True:
        errors.append("recovery evidence missing")
    if m["hardware_verified"] is not True:
        errors.append("physical acceptance evidence missing")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="PRIVATE sanitized manifest only")
    args = parser.parse_args()
    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    errors = validate(manifest)
    print("HOLD: " + "; ".join(errors) if errors else "ELIGIBLE FOR MANUAL REVIEW (not approval)")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
