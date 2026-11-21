"""Public-safe Android upgrade metadata gate. No APKs, keys or device identifiers."""
import json
import sys
import unittest

REQUIRED = ("package", "version_code", "signer_sha256")

def check(installed, candidate):
    for item in (installed, candidate):
        if not isinstance(item, dict) or any(k not in item for k in REQUIRED):
            return "BLOCKED: incomplete metadata"
        if not isinstance(item["version_code"], int) or isinstance(item["version_code"], bool) or item["version_code"] < 1:
            return "BLOCKED: invalid versionCode"
        if not isinstance(item["package"], str) or not item["package"]:
            return "BLOCKED: invalid package"
        signer = item["signer_sha256"]
        if not isinstance(signer, str) or len(signer) != 64 or any(c not in "0123456789abcdefABCDEF" for c in signer):
            return "BLOCKED: invalid signer fingerprint"
    if installed["package"] != candidate["package"]:
        return "SIDE_BY_SIDE_ONLY: package identity differs; installation requires owner approval"
    if installed["signer_sha256"].lower() != candidate["signer_sha256"].lower():
        return "HOLD: signing mismatch; do not replace or uninstall installed app"
    if candidate["version_code"] <= installed["version_code"]:
        return "HOLD: versionCode must increase"
    return "METADATA_PASS_ONLY: device upgrade and BLE AI1 still unverified"

class Tests(unittest.TestCase):
    def setUp(self):
        self.a = dict(package="example.ai", version_code=10, signer_sha256="a"*64)
        self.b = dict(package="example.ai", version_code=11, signer_sha256="A"*64)
    def test_metadata_only_pass(self):
        self.assertTrue(check(self.a,self.b).startswith("METADATA_PASS_ONLY"))
    def test_signer_mismatch(self):
        self.b["signer_sha256"]="b"*64
        self.assertTrue(check(self.a,self.b).startswith("HOLD: signing"))
    def test_downgrade(self):
        self.b["version_code"]=10
        self.assertTrue(check(self.a,self.b).startswith("HOLD: versionCode"))
    def test_side_by_side(self):
        self.b["package"]="example.ai.test"
        self.assertTrue(check(self.a,self.b).startswith("SIDE_BY_SIDE_ONLY"))
    def test_missing_metadata(self):
        del self.b["signer_sha256"]
        self.assertTrue(check(self.a,self.b).startswith("BLOCKED"))
    def test_invalid_signer(self):
        self.b["signer_sha256"]="secret"
        self.assertTrue(check(self.a,self.b).startswith("BLOCKED"))
    def test_boolean_version_rejected(self):
        self.b["version_code"]=True
        self.assertTrue(check(self.a,self.b).startswith("BLOCKED"))

if __name__ == "__main__":
    if len(sys.argv)==3:
        with open(sys.argv[1], encoding="utf-8") as f: installed=json.load(f)
        with open(sys.argv[2], encoding="utf-8") as f: candidate=json.load(f)
        result=check(installed,candidate)
        print(result)
        sys.exit(0 if result.startswith("METADATA_PASS_ONLY") else 1)
    unittest.main()
