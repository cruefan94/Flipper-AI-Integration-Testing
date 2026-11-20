#!/usr/bin/env python3
"""Offline, fail-closed Android upgrade metadata comparison. No APK upload or device access."""
import argparse
import json
import re
from pathlib import Path

SHA256 = re.compile(r"[0-9a-fA-F]{64}\Z")
PACKAGE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)+\Z")

def validate(installed, candidate):
    for label, record in (("installed", installed), ("candidate", candidate)):
        if not isinstance(record, dict):
            raise ValueError(f"{label}: metadata must be an object")
        if not isinstance(record.get("package"), str) or not PACKAGE.fullmatch(record["package"]):
            raise ValueError(f"{label}: invalid package")
        if type(record.get("versionCode")) is not int or record["versionCode"] < 1:
            raise ValueError(f"{label}: invalid versionCode")
        signer = record.get("signerSha256")
        if not isinstance(signer, str) or not SHA256.fullmatch(signer):
            raise ValueError(f"{label}: invalid signer fingerprint")
    if installed["package"] != candidate["package"]:
        raise ValueError("package mismatch: do not upgrade")
    if installed["signerSha256"].lower() != candidate["signerSha256"].lower():
        raise ValueError("signer mismatch: do not replace or uninstall installed app")
    if candidate["versionCode"] <= installed["versionCode"]:
        raise ValueError("versionCode not increasing")
    return True

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("installed", type=Path)
    p.add_argument("candidate", type=Path)
    a = p.parse_args()
    try:
        validate(json.loads(a.installed.read_text()), json.loads(a.candidate.read_text()))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        p.exit(1, f"HOLD: {exc}\n")
    print("METADATA MATCH ONLY: verify independently extracted signer, package and versionCode; device install requires owner approval.")

if __name__ == "__main__":
    main()
