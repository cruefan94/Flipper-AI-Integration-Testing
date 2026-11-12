import unittest
from scripts.verify_release_readiness import verify

SHA = "a" * 40

def evidence(verified=True):
    return {"verified": verified, "evidence_url": "https://github.com/example/repo/actions/runs/123"}

class ReleaseReadinessTests(unittest.TestCase):
    def test_no_evidence_is_not_ready(self):
        self.assertEqual(len(verify({})), 7)

    def test_partial_ci_cannot_pass_as_hardware(self):
        report = {name: evidence() for name in ("firmware", "android", "protocol", "hardware_ble", "packaging")}
        report["firmware"]["commit_sha"] = SHA
        report["android"]["commit_sha"] = SHA
        report["hardware_ble"]["verified"] = False
        self.assertIn("hardware_ble: not verified", verify(report))

    def test_mutable_refs_rejected(self):
        report = {name: evidence() for name in ("firmware", "android", "protocol", "hardware_ble", "packaging")}
        report["firmware"]["commit_sha"] = "main"
        report["android"]["commit_sha"] = SHA
        self.assertTrue(any("immutable" in x for x in verify(report)))

    def test_public_ci_alone_cannot_certify_release(self):
        report = {name: evidence() for name in ("firmware", "android", "protocol", "hardware_ble", "packaging")}
        report["firmware"]["commit_sha"] = SHA
        report["android"]["commit_sha"] = SHA
        report["firmware"]["verified"] = False
        report["hardware_ble"]["verified"] = False
        blockers = verify(report)
        self.assertIn("firmware: not verified", blockers)
        self.assertIn("hardware_ble: not verified", blockers)

    def test_all_evidence_passes(self):
        report = {name: evidence() for name in ("firmware", "android", "protocol", "hardware_ble", "packaging")}
        report["firmware"]["commit_sha"] = SHA
        report["android"]["commit_sha"] = SHA
        self.assertEqual(verify(report), [])

if __name__ == "__main__":
    unittest.main()
