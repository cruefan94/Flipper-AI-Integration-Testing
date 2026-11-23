#!/usr/bin/env python3
"""Public-safe artifact identity contract. No private artifact bytes or secrets."""
import argparse
import json
import re
import sys
import unittest

HEX = re.compile(r"^[0-9a-f]{64}$")
SHA = re.compile(r"^[0-9a-f]{40}$")

def validate(record):
    """Require distinct evidence for encrypted transport and native firmware."""
    if not isinstance(record, dict):
        raise ValueError("record must be an object")
    required = ("source_commit", "workflow_run_id", "encrypted_artifact_id",
                "encrypted_archive_sha256", "native_updater_sha256",
                "firmware_dfu_sha256", "firmware_dfu_crc_verified",
                "private_verification_run_id", "recovery_guide_reviewed")
    for key in required:
        if key not in record:
            raise ValueError("missing: " + key)
    if not isinstance(record["source_commit"], str) or not SHA.fullmatch(record["source_commit"]):
        raise ValueError("invalid source commit")
    for key in ("workflow_run_id", "encrypted_artifact_id", "private_verification_run_id"):
        if type(record[key]) is not int or record[key] <= 0:
            raise ValueError("invalid " + key)
    for key in ("encrypted_archive_sha256", "native_updater_sha256", "firmware_dfu_sha256"):
        if not isinstance(record[key], str) or not HEX.fullmatch(record[key]):
            raise ValueError("invalid " + key)
    if len({record[k] for k in ("encrypted_archive_sha256", "native_updater_sha256", "firmware_dfu_sha256")}) != 3:
        raise ValueError("transport, updater and firmware hashes must be independently measured")
    for key in ("firmware_dfu_crc_verified", "recovery_guide_reviewed"):
        if record[key] is not True:
            raise ValueError("unverified " + key)
    if record.get("hardware_tested") is True:
        raise ValueError("hardware claims require separate owner-controlled evidence")
    if record.get("release_approved") is True:
        raise ValueError("release approval is outside this contract")
    return True

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(source_commit="a"*40, workflow_run_id=1, encrypted_artifact_id=2,
                         encrypted_archive_sha256="a"*64, native_updater_sha256="b"*64,
                         firmware_dfu_sha256="c"*64, firmware_dfu_crc_verified=True,
                         private_verification_run_id=3, recovery_guide_reviewed=True)
    def test_valid(self):
        self.assertTrue(validate(self.good))
    def test_missing_native_hash(self):
        self.good.pop("native_updater_sha256")
        with self.assertRaises(ValueError): validate(self.good)
    def test_same_hash_is_not_independent_proof(self):
        self.good["native_updater_sha256"] = "a"*64
        with self.assertRaises(ValueError): validate(self.good)
    def test_synthetic_crc_not_accepted(self):
        self.good["firmware_dfu_crc_verified"] = "synthetic-pass"
        with self.assertRaises(ValueError): validate(self.good)
    def test_boolean_run_id_rejected(self):
        self.good["private_verification_run_id"] = True
        with self.assertRaises(ValueError): validate(self.good)
    def test_no_hardware_claim(self):
        self.good["hardware_tested"] = True
        with self.assertRaises(ValueError): validate(self.good)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="JSON evidence manifest; never supply private bytes")
    args = parser.parse_args()
    if not args.manifest:
        unittest.main(argv=[sys.argv[0]])
    else:
        try:
            with open(args.manifest, encoding="utf-8") as f:
                validate(json.load(f))
            print("PASS: metadata evidence contract only; NOT flash approval")
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            print("BLOCKED: " + str(exc), file=sys.stderr)
            sys.exit(1)
