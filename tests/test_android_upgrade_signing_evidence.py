"""Public-safe Android APK upgrade evidence gate; metadata only, no APKs or keys."""
import json
import re
import sys
import unittest

HEX64 = re.compile(r"^[0-9a-f]{64}$")
PACKAGE = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
FIELDS = {"mode", "installed", "candidate"}
IDENTITY = {"package", "version_code", "signer_sha256", "apk_sha256"}


def validate(record):
    """Return release-blocking reasons; never infer installed identity from CI metadata."""
    if not isinstance(record, dict) or set(record) != FIELDS:
        return ["invalid top-level metadata schema"]
    if record["mode"] not in ("upgrade", "side_by_side"):
        return ["invalid installation mode"]
    reasons = []
    for label in ("installed", "candidate"):
        value = record[label]
        if not isinstance(value, dict) or set(value) != IDENTITY:
            reasons.append(f"{label}: invalid identity schema")
            continue
        if not isinstance(value["package"], str) or not PACKAGE.fullmatch(value["package"]):
            reasons.append(f"{label}: invalid package")
        if type(value["version_code"]) is not int or value["version_code"] <= 0:
            reasons.append(f"{label}: invalid version code")
        for key in ("signer_sha256", "apk_sha256"):
            if not isinstance(value[key], str) or not HEX64.fullmatch(value[key]):
                reasons.append(f"{label}: invalid {key}")
    if reasons:
        return reasons
    installed, candidate = record["installed"], record["candidate"]
    if record["mode"] == "upgrade":
        if installed["package"] != candidate["package"]:
            reasons.append("upgrade package mismatch")
        if installed["signer_sha256"] != candidate["signer_sha256"]:
            reasons.append("upgrade signer mismatch; never uninstall existing app")
        if candidate["version_code"] <= installed["version_code"]:
            reasons.append("upgrade version_code must increase")
    else:
        if installed["package"] == candidate["package"]:
            reasons.append("side-by-side package must differ")
    return reasons


class GateTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "mode": "upgrade",
            "installed": {"package": "org.example.flipper", "version_code": 10,
                          "signer_sha256": "a" * 64, "apk_sha256": "b" * 64},
            "candidate": {"package": "org.example.flipper", "version_code": 11,
                          "signer_sha256": "a" * 64, "apk_sha256": "c" * 64},
        }

    def test_valid_upgrade(self):
        self.assertEqual(validate(self.item), [])

    def test_signing_mismatch(self):
        self.item["candidate"]["signer_sha256"] = "d" * 64
        self.assertIn("upgrade signer mismatch; never uninstall existing app", validate(self.item))

    def test_version_downgrade(self):
        self.item["candidate"]["version_code"] = 9
        self.assertTrue(validate(self.item))

    def test_same_version(self):
        self.item["candidate"]["version_code"] = 10
        self.assertTrue(validate(self.item))

    def test_upgrade_package_change(self):
        self.item["candidate"]["package"] = "org.example.test"
        self.assertIn("upgrade package mismatch", validate(self.item))

    def test_valid_side_by_side(self):
        self.item["mode"] = "side_by_side"
        self.item["candidate"]["package"] = "org.example.flipper.test"
        self.item["candidate"]["signer_sha256"] = "d" * 64
        self.assertEqual(validate(self.item), [])

    def test_side_by_side_same_package(self):
        self.item["mode"] = "side_by_side"
        self.assertTrue(validate(self.item))

    def test_reject_extra_fields(self):
        self.item["candidate"]["token"] = "secret"
        self.assertTrue(validate(self.item))

    def test_reject_invalid_hash(self):
        self.item["candidate"]["apk_sha256"] = "ABC"
        self.assertTrue(validate(self.item))

    def test_reject_bool_version(self):
        self.item["candidate"]["version_code"] = True
        self.assertTrue(validate(self.item))

    def test_reject_unknown_mode(self):
        self.item["mode"] = "replace"
        self.assertTrue(validate(self.item))

    def test_reject_missing_installed_identity(self):
        del self.item["installed"]
        self.assertTrue(validate(self.item))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        with open(sys.argv[1], encoding="utf-8") as stream:
            result = validate(json.load(stream))
        print(json.dumps({"eligible_by_metadata_only": not result, "blockers": result}))
        sys.exit(bool(result))
    unittest.main()
