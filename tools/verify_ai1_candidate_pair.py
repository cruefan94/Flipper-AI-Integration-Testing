#!/usr/bin/env python3
"""Fail-closed public-safe AI1 candidate metadata parity check.

Only compares sanitized metadata; it does NOT verify firmware, APK, CI status,
signatures, encryption, device operation or release readiness.
"""
import json
import re
import sys
from pathlib import Path

REPOS = {
    "firmware": ("cruefan94/Flipper-AI-Momentum-", "f7-updater-tgz"),
    "android": ("cruefan94/Flipper-AI-Android-Satellite", "android-test-apk"),
}
FIELDS = {
    "component", "source_repo", "source_commit", "ai1_contract_sha256",
    "ai1_protocol_version", "artifact_sha256", "artifact_kind", "ci_run_url",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
RUN_URL = re.compile(r"https://github\.com/cruefan94/(Flipper-AI-Momentum-|Flipper-AI-Android-Satellite|Flipper-AI-Integration-Testing)/actions/runs/[1-9][0-9]*\Z")


def validate(record, expected):
    if not isinstance(record, dict) or set(record) != FIELDS:
        raise ValueError(f"{expected}: missing or unexpected metadata fields")
    repo, kind = REPOS[expected]
    if record["component"] != expected or record["source_repo"] != repo or record["artifact_kind"] != kind:
        raise ValueError(f"{expected}: component/source/artifact ownership mismatch")
    for field, regex in (("source_commit", HEX40), ("artifact_sha256", HEX64), ("ai1_contract_sha256", HEX64)):
        value = record[field]
        if not isinstance(value, str) or not regex.fullmatch(value):
            raise ValueError(f"{expected}: invalid {field}")
    version = record["ai1_protocol_version"]
    if not isinstance(version, str) or not re.fullmatch(r"[1-9][0-9]*\.[0-9]+", version):
        raise ValueError(f"{expected}: invalid AI1 protocol version")
    url = record["ci_run_url"]
    if not isinstance(url, str) or not RUN_URL.fullmatch(url):
        raise ValueError(f"{expected}: invalid CI run URL")


def check_pair(firmware, android):
    validate(firmware, "firmware")
    validate(android, "android")
    for field in ("ai1_contract_sha256", "ai1_protocol_version"):
        if firmware[field] != android[field]:
            raise ValueError(f"AI1 {field} mismatch")
    return "METADATA_PARITY_ONLY: pinned AI1 contract metadata agrees; no release or hardware verification"


def main(argv):
    if len(argv) != 3:
        print("Usage: verify_ai1_candidate_pair.py FIRMWARE_PUBLIC_METADATA.json ANDROID_PUBLIC_METADATA.json", file=sys.stderr)
        return 2
    try:
        firmware = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        android = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        print(check_pair(firmware, android))
        return 0
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
