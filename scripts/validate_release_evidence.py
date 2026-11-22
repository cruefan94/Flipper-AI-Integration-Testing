#!/usr/bin/env python3
"""Public-safe, offline release-evidence admission validator.

Only accepts a deliberately minimal, non-sensitive manifest. No network access,
private repository paths, logs, firmware, APKs, or secret material are read.
Usage: python3 scripts/validate_release_evidence.py manifest.json
       python3 scripts/validate_release_evidence.py --self-test
"""
import json
import re
import sys
import unittest
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
RUN = re.compile(r"^[1-9][0-9]{5,}$")
STATUS = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED"}
REQUIRED = {"schema", "android", "f7", "ai1", "fallback"}
ARTIFACT = {"source_sha", "artifact_sha256", "ci_run_id", "result"}
MAX_BYTES = 8192


def validate(data):
    errors = []
    if not isinstance(data, dict) or set(data) != REQUIRED:
        return ["top-level keys must be exactly schema, android, f7, ai1, fallback"]
    if data["schema"] != 1:
        errors.append("schema must equal 1")
    for kind in ("android", "f7"):
        value = data[kind]
        if not isinstance(value, dict) or set(value) != ARTIFACT:
            errors.append(kind + ": invalid field set")
            continue
        if not isinstance(value["source_sha"], str) or not SHA.fullmatch(value["source_sha"]):
            errors.append(kind + ": invalid source SHA")
        digest = value["artifact_sha256"]
        if digest is not None and (not isinstance(digest, str) or not HEX64.fullmatch(digest)):
            errors.append(kind + ": invalid artifact SHA256")
        run = value["ci_run_id"]
        if run is not None and (not isinstance(run, str) or not RUN.fullmatch(run)):
            errors.append(kind + ": invalid CI run ID")
        if value["result"] not in STATUS:
            errors.append(kind + ": invalid result")
        if value["result"] == "PASS" and (digest is None or run is None):
            errors.append(kind + ": PASS requires artifact digest and CI run ID")
    for kind in ("ai1", "fallback"):
        value = data[kind]
        if not isinstance(value, dict) or set(value) != {"result", "ci_run_id"}:
            errors.append(kind + ": invalid field set")
            continue
        if value["result"] not in STATUS:
            errors.append(kind + ": invalid result")
        run = value["ci_run_id"]
        if run is not None and (not isinstance(run, str) or not RUN.fullmatch(run)):
            errors.append(kind + ": invalid CI run ID")
        if value["result"] == "PASS" and run is None:
            errors.append(kind + ": PASS requires CI run ID")
    return errors


class Tests(unittest.TestCase):
    def fixture(self):
        a = {"source_sha": "a" * 40, "artifact_sha256": None,
             "ci_run_id": None, "result": "UNVERIFIED"}
        return {"schema": 1, "android": dict(a), "f7": dict(a),
                "ai1": {"result": "BLOCKED", "ci_run_id": None},
                "fallback": {"result": "UNVERIFIED", "ci_run_id": None}}

    def test_unverified_admitted(self):
        self.assertEqual(validate(self.fixture()), [])

    def test_no_unproven_pass(self):
        a = self.fixture()
        a["f7"]["result"] = "PASS"
        self.assertTrue(validate(a))

    def test_proven_pass(self):
        a = self.fixture()
        a["android"].update(result="PASS", artifact_sha256="b"*64, ci_run_id="45068584230")
        self.assertEqual(validate(a), [])

    def test_extra_fields_rejected(self):
        a = self.fixture()
        a["android"]["token"] = "never-allowed"
        self.assertTrue(validate(a))

    def test_invalid_sha_rejected(self):
        a = self.fixture()
        a["f7"]["source_sha"] = "bad"
        self.assertTrue(validate(a))

    def test_ai1_requires_run(self):
        a = self.fixture()
        a["ai1"]["result"] = "PASS"
        self.assertTrue(validate(a))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    elif len(sys.argv) == 2:
        path = Path(sys.argv[1])
        if path.stat().st_size > MAX_BYTES:
            sys.exit("BLOCKED: manifest exceeds 8192 bytes")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            sys.exit("BLOCKED: invalid or unreadable JSON manifest")
        problems = validate(data)
        if problems:
            for problem in problems:
                print("BLOCKED:", problem)
            sys.exit(1)
        print("Schema valid; release NOT authorized. Hardware, signing and DFU CRC require separate proof.")
    else:
        sys.exit("usage: validate_release_evidence.py MANIFEST.json | --self-test")
