#!/usr/bin/env python3
"""Fail-closed, public-safe release evidence gate. No private artifacts or credentials."""
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
ALLOWED = {"repository", "source_sha", "workflow_run_id", "workflow_url",
           "artifact_sha256", "artifact_kind", "ci_result", "ai1_contract",
           "signing_match", "version_increment", "dfu_crc_valid",
           "internal_hashes_valid", "encrypted_only", "recovery_ready",
           "device_test", "failed_run_ids", "fallback_run_id",
           "fallback_result", "private_actions_access"}
KINDS = {"android_apk", "f7_updater"}
STATES = {"pass", "fail", "blocked", "unknown"}
def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    extra = set(record) - ALLOWED
    if extra:
        errors.append("unexpected fields (potential sensitive data)")
    for key in ("repository", "source_sha", "workflow_run_id", "workflow_url",
                "artifact_sha256", "artifact_kind", "ci_result", "ai1_contract"):
        if key not in record:
            errors.append("missing " + key)
    if not SHA.fullmatch(str(record.get("source_sha", ""))):
        errors.append("invalid source_sha")
    if not HASH.fullmatch(str(record.get("artifact_sha256", ""))):
        errors.append("invalid artifact_sha256")
    if type(record.get("workflow_run_id")) is not int or record["workflow_run_id"] <= 0:
        errors.append("invalid workflow_run_id")
    repo = record.get("repository")
    if repo not in {"cruefan94/Flipper-AI-Momentum-", "cruefan94/Flipper-AI-Android-Satellite"}:
        errors.append("unapproved repository")
    expected_url = "https://github.com/{}/actions/runs/{}".format(repo, record.get("workflow_run_id"))
    if record.get("workflow_url") != expected_url:
        errors.append("workflow URL does not match run and repository")
    if record.get("artifact_kind") not in KINDS:
        errors.append("invalid artifact_kind")
    for key in ("ci_result", "ai1_contract"):
        if record.get(key) not in STATES:
            errors.append("invalid " + key)
    kind = record.get("artifact_kind")
    required = ("signing_match", "version_increment") if kind == "android_apk" else (
        "dfu_crc_valid", "internal_hashes_valid", "encrypted_only", "recovery_ready")
    for key in required:
        if record.get(key) is not True:
            errors.append(key + " not attested")
    if record.get("ci_result") != "pass" or record.get("ai1_contract") != "pass":
        errors.append("CI or AI1 contract not passing")
    if record.get("device_test") != "pass":
        errors.append("physical device test not passing")
    failures = record.get("failed_run_ids", [])
    if not isinstance(failures, list) or any(type(n) is not int or n <= 0 for n in failures):
        errors.append("invalid failed_run_ids")
    elif len(failures) >= 2:
        if record.get("fallback_result") != "pass" or type(record.get("fallback_run_id")) is not int:
            errors.append("two failures require proven fallback")
        if record.get("private_actions_access") != "accessible":
            errors.append("private Actions access blocked")
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: release_evidence_gate.py public-safe-manifest.json")
    try:
        record = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        errors = validate(record)
    except (OSError, ValueError) as exc:
        sys.exit("HOLD: invalid evidence file (" + type(exc).__name__ + ")")
    if errors:
        sys.exit("HOLD: " + "; ".join(errors))
    print("EVIDENCE GATE PASSED (not authorization to install, flash, merge or deploy)")
