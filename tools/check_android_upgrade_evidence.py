#!/usr/bin/env python3
"""Offline, public-safe Android in-place upgrade evidence gate.

Input JSON must be generated locally from independently inspected APK/package
metadata. This script checks claims, not the authenticity of those observations.
Never upload device identifiers, APKs, keystores or certificates to public CI.
"""
import argparse
import json
import re
import sys

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
PACKAGE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")


def validate(evidence):
    errors = []
    if not isinstance(evidence, dict):
        return ["Evidence must be an object"]
    installed = evidence.get("installed")
    candidate = evidence.get("candidate")
    if not isinstance(installed, dict) or not isinstance(candidate, dict):
        return ["installed and candidate must be objects"]
    for label, item in (("installed", installed), ("candidate", candidate)):
        if not isinstance(item.get("package_name"), str) or not PACKAGE.fullmatch(item["package_name"]):
            errors.append(f"{label}.package_name invalid")
        if not isinstance(item.get("signer_sha256"), str) or not HEX64.fullmatch(item["signer_sha256"]):
            errors.append(f"{label}.signer_sha256 must be a 64-hex fingerprint")
        if type(item.get("version_code")) is not int or item["version_code"] < 1:
            errors.append(f"{label}.version_code must be a positive integer")
        if item.get("signature_verified") is not True:
            errors.append(f"{label}.signature_verified must be true")
    if errors:
        return errors
    if installed["package_name"] != candidate["package_name"]:
        errors.append("package mismatch: not an in-place upgrade")
    if installed["signer_sha256"].lower() != candidate["signer_sha256"].lower():
        errors.append("signer mismatch: do not replace or uninstall installed app")
    if candidate["version_code"] <= installed["version_code"]:
        errors.append("candidate version_code must increase")
    if evidence.get("owner_approved_install") is not True:
        errors.append("owner approval absent: no installation permitted")
    return errors


def selftest():
    base = {
        "installed": {"package_name": "org.example.satellite", "signer_sha256": "a" * 64, "version_code": 4, "signature_verified": True},
        "candidate": {"package_name": "org.example.satellite", "signer_sha256": "A" * 64, "version_code": 5, "signature_verified": True},
        "owner_approved_install": True,
    }
    import copy
    assert not validate(base)
    cases = [
        ("signer", lambda d: d["candidate"].update(signer_sha256="b" * 64)),
        ("version", lambda d: d["candidate"].update(version_code=4)),
        ("package", lambda d: d["candidate"].update(package_name="org.example.other")),
        ("unsigned", lambda d: d["candidate"].update(signature_verified=False)),
        ("approval", lambda d: d.update(owner_approved_install=False)),
        ("placeholder", lambda d: d["installed"].update(signer_sha256="unverified")),
        ("boolean version", lambda d: d["candidate"].update(version_code=True)),
    ]
    for name, mutation in cases:
        sample = copy.deepcopy(base)
        mutation(sample)
        assert validate(sample), f"fail-open: {name}"
    print("PASS: synthetic Android upgrade evidence self-tests")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", nargs="?", help="Local JSON evidence file; do not publish private metadata")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        selftest()
        return 0
    if not args.evidence:
        parser.error("provide evidence JSON or --self-test")
    try:
        with open(args.evidence, encoding="utf-8") as stream:
            data = json.load(stream)
    except (OSError, ValueError) as exc:
        print(f"BLOCKED: cannot read evidence: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"HOLD: {error}", file=sys.stderr)
        return 1
    print("PASS: evidence fields consistent; authenticity and device compatibility still require independent verification")
    return 0


if __name__ == "__main__":
    sys.exit(main())
