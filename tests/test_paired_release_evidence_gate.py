"""Public-safe offline regression tests; no GitHub token or hardware required."""
import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "paired_release_evidence_gate.py"
spec = importlib.util.spec_from_file_location("paired_gate", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def passing():
    return {
        "firmware": {
            "repository": "private/repo", "commit_sha": "a" * 40,
            "workflow_run_url": "https://github.com/example/repo/actions/runs/123",
            "jobs": {k: "success" for k in gate.REQUIRED_JOBS["firmware"]},
        },
        "android": {
            "repository": "public/repo", "commit_sha": "b" * 40,
            "workflow_run_url": "https://github.com/example/repo/actions/runs/456",
            "jobs": {k: "success" for k in gate.REQUIRED_JOBS["android"]},
        },
        "paired": {"jobs": {"ai1_contract": "success"}},
        "hardware_verified": True, "owner_approved": True,
    }

class EvidenceGateTests(unittest.TestCase):
    def test_complete_manifest(self):
        self.assertEqual(gate.validate(passing()), [])
    def test_native_skipped(self):
        e = passing()
        e["firmware"]["jobs"]["native_compile"] = "skipped"
        self.assertTrue(any("native_compile" in x for x in gate.validate(e)))
    def test_crc_synthetic_is_not_success(self):
        e = passing()
        e["firmware"]["jobs"]["real_dfu_crc"] = "synthetic-only"
        self.assertTrue(gate.validate(e))
    def test_android_signing_unknown(self):
        e = passing()
        del e["android"]["jobs"]["signer_match"]
        self.assertTrue(gate.validate(e))
    def test_ai1_unpaired(self):
        e = passing()
        e["paired"]["jobs"]["ai1_contract"] = "skipped"
        self.assertTrue(gate.validate(e))
    def test_no_owner_approval(self):
        e = passing()
        e["owner_approved"] = False
        self.assertTrue(gate.validate(e))
    def test_no_physical_verification(self):
        e = passing()
        e["hardware_verified"] = False
        self.assertTrue(gate.validate(e))
    def test_missing_provenance(self):
        e = passing()
        e["firmware"]["commit_sha"] = "short"
        self.assertTrue(gate.validate(e))
    def test_invalid_input(self):
        self.assertTrue(gate.validate(None))

if __name__ == "__main__":
    unittest.main()
