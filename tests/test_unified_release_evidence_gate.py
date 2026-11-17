"""Public-safe offline release-evidence gate. No repository secrets or firmware bytes."""
import re
import unittest

SHA = re.compile(r"^[0-9a-f]{40}$")
HASH = re.compile(r"^[0-9a-f]{64}$")

def evaluate(e):
    """Return blockers; never infer native CRC from encrypted ZIP or CI success."""
    blockers = []
    for component in ("android", "firmware"):
        item = e.get(component, {})
        if not SHA.fullmatch(str(item.get("source_sha", ""))):
            blockers.append(component + ": exact source SHA missing")
        if not isinstance(item.get("passing_run_id"), int) or item["passing_run_id"] <= 0:
            blockers.append(component + ": passing run ID missing")
        if not HASH.fullmatch(str(item.get("artifact_sha256", ""))):
            blockers.append(component + ": artifact SHA-256 missing")
    android = e.get("android", {})
    if not android.get("package_name") or not isinstance(android.get("version_code"), int):
        blockers.append("android: package/version evidence missing")
    if not HASH.fullmatch(str(android.get("signer_sha256", ""))):
        blockers.append("android: signer fingerprint missing")
    if android.get("upgrade_compatible") is not True and android.get("isolated_test_package") is not True:
        blockers.append("android: neither safe upgrade nor isolated test package proven")
    firmware = e.get("firmware", {})
    if firmware.get("real_dfu_header_valid") is not True:
        blockers.append("firmware: actual DFU header unverified")
    if firmware.get("real_dfu_suffix_crc_valid") is not True:
        blockers.append("firmware: actual DFU suffix CRC unverified")
    if not HASH.fullmatch(str(firmware.get("native_tgz_sha256", ""))):
        blockers.append("firmware: native TGZ hash missing")
    if firmware.get("encrypted_only_delivery") is not True:
        blockers.append("firmware: encrypted-only delivery unverified")
    if e.get("ai1_contract_parity") is not True:
        blockers.append("AI1: paired contract parity unverified")
    if e.get("hardware_acceptance") is not True:
        blockers.append("hardware: physical acceptance unverified")
    return blockers

class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.good = {
            "android": {"source_sha": "a"*40, "passing_run_id": 1,
                "artifact_sha256": "b"*64, "package_name": "example.test",
                "version_code": 2, "signer_sha256": "c"*64,
                "isolated_test_package": True},
            "firmware": {"source_sha": "d"*40, "passing_run_id": 2,
                "artifact_sha256": "e"*64, "native_tgz_sha256": "f"*64,
                "real_dfu_header_valid": True, "real_dfu_suffix_crc_valid": True,
                "encrypted_only_delivery": True},
            "ai1_contract_parity": True, "hardware_acceptance": True}
    def test_complete_evidence(self):
        self.assertEqual(evaluate(self.good), [])
    def test_empty_fails_closed(self):
        self.assertGreaterEqual(len(evaluate({})), 10)
    def test_encrypted_hash_not_native_hash(self):
        del self.good["firmware"]["native_tgz_sha256"]
        self.assertIn("firmware: native TGZ hash missing", evaluate(self.good))
    def test_synthetic_crc_not_real_crc(self):
        self.good["firmware"]["synthetic_crc_passed"] = True
        self.good["firmware"]["real_dfu_suffix_crc_valid"] = False
        self.assertIn("firmware: actual DFU suffix CRC unverified", evaluate(self.good))
    def test_ci_success_not_hardware(self):
        self.good["hardware_acceptance"] = False
        self.assertIn("hardware: physical acceptance unverified", evaluate(self.good))
    def test_signer_mismatch_requires_isolation(self):
        self.good["android"]["isolated_test_package"] = False
        self.assertIn("android: neither safe upgrade nor isolated test package proven", evaluate(self.good))
    def test_invalid_sha(self):
        self.good["android"]["source_sha"] = "short"
        self.assertIn("android: exact source SHA missing", evaluate(self.good))
    def test_ai1_unverified(self):
        self.good["ai1_contract_parity"] = False
        self.assertIn("AI1: paired contract parity unverified", evaluate(self.good))

if __name__ == "__main__":
    unittest.main()
