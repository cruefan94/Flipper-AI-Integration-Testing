"""Offline regressions for the public-safe fallback decision gate."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "fallback", Path(__file__).resolve().parents[1] / "tools" / "public_safe_fallback_decision.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def attempt(rid, workflow=42, branch="test/a", conclusion="failure", provisioned=True):
    return dict(workflow_id=workflow, branch=branch, run_id=rid,
                status="completed", conclusion=conclusion, jobs_provisioned=provisioned)

class FallbackIdentityTests(unittest.TestCase):
    def test_same_workflow_branch_two_failures(self):
        self.assertEqual(module.classify([attempt(1), attempt(2)]), "FALLBACK_REQUIRED")
    def test_different_workflows(self):
        self.assertEqual(module.classify([attempt(1), attempt(2, workflow=43)]), "NO_TRIGGER")
    def test_different_branches(self):
        self.assertEqual(module.classify([attempt(1), attempt(2, branch="test/b")]), "NO_TRIGGER")
    def test_success_resets_streak(self):
        self.assertEqual(module.classify([attempt(1), attempt(2, conclusion="success"), attempt(3)]), "NO_TRIGGER")
    def test_pre_runner_repeated_failures(self):
        self.assertEqual(module.classify([attempt(1, provisioned=False), attempt(2, provisioned=False)]), "FALLBACK_REQUIRED")
    def test_pending_is_not_failure(self):
        row = attempt(1); row["status"] = "queued"
        self.assertEqual(module.classify([row, attempt(2)]), "INSUFFICIENT_EVIDENCE")
    def test_duplicate_id_rejected(self):
        self.assertEqual(module.classify([attempt(1), attempt(1)]), "INSUFFICIENT_EVIDENCE")
    def test_unknown_field_rejected(self):
        row = attempt(1); row["token"] = "redacted"
        self.assertEqual(module.classify([row]), "INSUFFICIENT_EVIDENCE")
    def test_late_malformed_evidence_fails_closed(self):
        bad = attempt(3); bad["private_log"] = "forbidden"
        self.assertEqual(module.classify([attempt(1), attempt(2), bad]), "INSUFFICIENT_EVIDENCE")
    def test_empty_is_unknown(self):
        self.assertEqual(module.classify([]), "INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
