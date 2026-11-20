#!/usr/bin/env python3
"""Offline, public-safe release gate. Never upload private manifests or binaries.

Usage: python3 tools/check_release_evidence.py --self-test
       python3 tools/check_release_evidence.py /path/to/PRIVATE/local-manifest.json
Only exit status is emitted. No manifest values or paths are printed.
"""
import argparse
import json
import re
import sys

HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")
REQUIRED = ("source_sha", "ci_run_url", "artifact_sha256", "contract_version",
            "native_build_passed", "real_artifact_verified", "hardware_verified")
SHA40 = re.compile(r"^[a-fA-F0-9]{40}$")
RUN = re.compile(r"^https://github\.com/[^/]+/[^/]+/actions/runs/[0-9]+$")
AI1_VERSION = re.compile(r"^AI1-v[1-9][0-9]*$")

def valid(entry):
    if not isinstance(entry, dict) or any(k not in entry for k in REQUIRED):
        return False
    if not isinstance(entry["source_sha"], str) or not SHA40.fullmatch(entry["source_sha"]):
        return False
    if not isinstance(entry["artifact_sha256"], str) or not HEX64.fullmatch(entry["artifact_sha256"]):
        return False
    if not isinstance(entry["ci_run_url"], str) or not RUN.fullmatch(entry["ci_run_url"]):
        return False
    if not isinstance(entry["contract_version"], str) or not AI1_VERSION.fullmatch(entry["contract_version"]):
        return False
    return all(entry[k] is True for k in ("native_build_passed", "real_artifact_verified", "hardware_verified"))

def check(data):
    # A green host-only CI or an absent candidate must never be promoted.
    if not isinstance(data, dict) or set(data) != {"android", "f7", "ai1_paired_passed"}:
        return False
    if data["ai1_paired_passed"] is not True:
        return False
    return (valid(data["android"]) and valid(data["f7"]) and
            data["android"]["contract_version"] == data["f7"]["contract_version"])

def self_test():
    e = dict(source_sha="a"*40, ci_run_url="https://github.com/x/y/actions/runs/123",
             artifact_sha256="b"*64, contract_version="AI1-v1",
             native_build_passed=True, real_artifact_verified=True, hardware_verified=True)
    good = dict(android=e.copy(), f7=e.copy(), ai1_paired_passed=True)
    assert check(good)
    for field in ("source_sha", "ci_run_url", "artifact_sha256", "contract_version"):
        bad = json.loads(json.dumps(good))
        bad["f7"][field] = "unverified"
        assert not check(bad), field
    for field in ("native_build_passed", "real_artifact_verified", "hardware_verified"):
        bad = json.loads(json.dumps(good))
        bad["f7"][field] = False
        assert not check(bad), field
    bad = json.loads(json.dumps(good))
    bad["f7"]["contract_version"] = "AI1-v2"
    assert not check(bad), "AI1 contract version mismatch"
    bad = json.loads(json.dumps(good))
    bad["ai1_paired_passed"] = False
    assert not check(bad)
    bad = json.loads(json.dumps(good))
    del bad["android"]
    assert not check(bad)
    bad = json.loads(json.dumps(good))
    bad["f7"]["native_build_passed"] = "true"
    assert not check(bad)
    return True

def main():
    parser = argparse.ArgumentParser(description="Fail-closed offline release evidence gate")
    parser.add_argument("manifest", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("PASS: synthetic fail-closed tests only; no release evidence verified")
        return 0
    if not args.manifest:
        parser.error("private local manifest required")
    try:
        with open(args.manifest, encoding="utf-8") as f:
            data = json.load(f)
        passed = check(data)
    except (OSError, ValueError, TypeError, KeyError):
        passed = False
    print("PASS: manifest fields structurally valid (not independently authenticated)" if passed
          else "HOLD: missing or invalid release evidence")
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
