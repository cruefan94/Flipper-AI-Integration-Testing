import unittest
from tools.check_two_failure_evidence import evaluate

def run(i, workflow="F7", branch="candidate", conclusion="failure", status="completed"):
    return {"id": i, "workflow": workflow, "branch": branch, "status": status, "conclusion": conclusion}

class FallbackEvidenceTests(unittest.TestCase):
    def test_two_failures_require_fallback(self):
        out = evaluate({"runs": [run(11), run(12)], "private_actions_read": "accessible"})
        self.assertEqual(out["pairs"][0]["failing_run_ids"], [11, 12])
        self.assertEqual(out["pairs"][0]["decision"], "FALLBACK_REQUIRED")
        self.assertFalse(out["dispatched"])
        self.assertFalse(out["native_build_verified"])

    def test_missing_permission_blocks(self):
        self.assertEqual(evaluate({"runs": [run(11), run(12)], "private_actions_read": "blocked"})["pairs"][0]["decision"], "BLOCKED")

    def test_success_resets(self):
        self.assertEqual(evaluate({"runs": [run(1), run(2, conclusion="success"), run(3)]})["pairs"], [])

    def test_distinct_branch_or_workflow(self):
        self.assertEqual(evaluate({"runs": [run(1), run(2, branch="other"), run(3, workflow="S3")]})["pairs"], [])

    def test_incomplete_not_counted(self):
        self.assertEqual(evaluate({"runs": [run(1), run(2, status="queued")]})["pairs"], [])

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"runs": [run(1), run(1)]})

    def test_malformed_rejected(self):
        with self.assertRaises(ValueError):
            evaluate({"runs": [{"id": 1}]})

    def test_unknown_access_blocked(self):
        self.assertEqual(evaluate({"runs": [run(1), run(2)]})["pairs"][0]["decision"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
