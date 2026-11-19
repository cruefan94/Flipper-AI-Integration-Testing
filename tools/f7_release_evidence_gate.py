#!/usr/bin/env python3
"""Public-safe, offline release-evidence POLICY gate. Never reads firmware or secrets."""
import argparse
import json
import re
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
REQUIRED = ("source_sha", "native_run_url", "native_build_passed",
            "native_job_not_skipped", "real_dfu_crc_verified",
            "native_updater_sha256", "encrypted_artifact_only",
            "flash_layout_safety_passed", "android_signing_compatible",
            "android_version_code_increases", "paired_ai1_contract_passed",
            "hardware_verified", "owner_flash_approved")

def validate(data):
    if not isinstance(data, dict):
        return ["manifest must be an object"]
    errors = []
    for key in REQUIRED:
        if key not in data:
            errors.append("missing " + key)
    if errors:
        return errors
    if not isinstance(data["source_sha"], str) or not HEX40.fullmatch(data["source_sha"]):
        errors.append("invalid source_sha")
    if not isinstance(data["native_updater_sha256"], str) or not HEX64.fullmatch(data["native_updater_sha256"]):
        errors.append("invalid native_updater_sha256")
    url = data["native_run_url"]
    if not isinstance(url, str) or not re.fullmatch(r"https://github.com/[^/]+/[^/]+/actions/runs/[0-9]+", url):
        errors.append("invalid native_run_url")
    for key in REQUIRED[2:]:
        if key == "native_updater_sha256":
            continue
        if type(data[key]) is not bool or data[key] is not True:
            errors.append("not proven: " + key)
    return errors

def main():
    p = argparse.ArgumentParser(description="Offline strict manifest policy gate; never uploads artifacts")
    p.add_argument("manifest")
    args = p.parse_args()
    try:
        with open(args.manifest, encoding="utf-8") as f:
            obj = json.load(f)
    except (OSError, ValueError) as exc:
        print("FAIL: cannot read valid JSON manifest", file=sys.stderr)
        return 2
    errors = validate(obj)
    for error in errors:
        print("FAIL: " + error, file=sys.stderr)
    if errors:
        return 1
    print("PASS: declared evidence policy only; not proof of authenticity or physical device testing")
    return 0

if __name__ == "__main__":
    sys.exit(main())
