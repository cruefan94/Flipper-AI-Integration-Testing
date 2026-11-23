#!/usr/bin/env python3
"""Offline, public-safe Android upgrade admission gate. No APKs, keystores or devices."""
import argparse
import json
import re
import sys
import unittest

HEX = re.compile(r"^[0-9a-fA-F]{64}$")
PACKAGE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+$")

def validate(record):
    """Fail closed: only sanitized, independently extracted metadata is accepted."""
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    installed, candidate = record.get("installed"), record.get("candidate")
    if not isinstance(installed, dict) or not isinstance(candidate, dict):
        return ["installed and candidate metadata are required"]
    for label, app in (("installed", installed), ("candidate", candidate)):
        if not isinstance(app.get("package"), str) or not PACKAGE.fullmatch(app["package"]):
            errors.append(label + ".package invalid")
        if type(app.get("version_code")) is not int or app["version_code"] < 1:
            errors.append(label + ".version_code invalid")
        for key in ("signer_sha256", "apk_sha256"):
            if not isinstance(app.get(key), str) or not HEX.fullmatch(app[key]):
                errors.append(label + "." + key + " missing or invalid")
    if errors:
        return errors
    if installed["package"] != candidate["package"]:
        errors.append("package mismatch: not an in-place upgrade")
    if installed["signer_sha256"].lower() != candidate["signer_sha256"].lower():
        errors.append("signing certificate mismatch: do not replace/uninstall")
    if candidate["version_code"] <= installed["version_code"]:
        errors.append("candidate version_code must increase")
    if installed["apk_sha256"].lower() == candidate["apk_sha256"].lower():
        errors.append("candidate APK identical to installed APK")
    if record.get("metadata_verified_from_real_apks") is not True:
        errors.append("independent real-APK metadata verification required")
    return errors

class GateTests(unittest.TestCase):
    def setUp(self):
        self.data = {"installed":{"package":"ca.example.satellite","version_code":12,
                     "signer_sha256":"a"*64,"apk_sha256":"b"*64},
                     "candidate":{"package":"ca.example.satellite","version_code":13,
                     "signer_sha256":"a"*64,"apk_sha256":"c"*64},
                     "metadata_verified_from_real_apks":True}
    def test_valid_metadata(self): self.assertEqual(validate(self.data), [])
    def test_signer_mismatch(self):
        self.data["candidate"]["signer_sha256"]="d"*64
        self.assertTrue(any("signing" in x for x in validate(self.data)))
    def test_downgrade(self):
        self.data["candidate"]["version_code"]=11
        self.assertTrue(validate(self.data))
    def test_unverified(self):
        self.data["metadata_verified_from_real_apks"]=False
        self.assertTrue(validate(self.data))
    def test_missing_hash(self):
        del self.data["candidate"]["apk_sha256"]
        self.assertTrue(validate(self.data))
    def test_package_mismatch(self):
        self.data["candidate"]["package"]="ca.example.other"
        self.assertTrue(validate(self.data))
    def test_boolean_version_rejected(self):
        self.data["candidate"]["version_code"]=True
        self.assertTrue(validate(self.data))
    def test_no_secrets_or_apks(self):
        self.assertTrue(validate({"installed":{},"candidate":{}}))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", nargs="?", help="local JSON with sanitized installed/candidate APK metadata")
    parser.add_argument("--self-test", action="store_true")
    args=parser.parse_args()
    if args.self_test:
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(GateTests)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if not args.metadata:
        parser.error("metadata JSON path required")
    try:
        with open(args.metadata,encoding="utf-8") as f: record=json.load(f)
        errors=validate(record)
    except (OSError,ValueError) as exc:
        print("BLOCKED: unreadable or invalid metadata",file=sys.stderr)
        return 2
    if errors:
        for error in errors: print("HOLD: "+error)
        return 1
    print("METADATA GATE PASS ONLY — physical BLE, source provenance, CI and owner install approval still required")
    return 0

if __name__=="__main__":
    sys.exit(main())
