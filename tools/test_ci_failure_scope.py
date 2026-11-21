import unittest
from ci_failure_scope import classify


def run(id, branch="feature", workflow=7, conclusion="failure", status="completed"):
    return {"id": id, "repository": "owner/repo", "head_branch": branch,
            "workflow_id": workflow, "status": status, "conclusion": conclusion,
            "created_at": f"2026-11-21T{id:02d}:00:00Z"}


class FailureScopeTests(unittest.TestCase):
    def test_two_failures_same_branch_trigger(self):
        self.assertEqual(classify([run(2), run(1)])[0]["fallback_status"], "REQUIRED_NOT_DISPATCHED")

    def test_different_branches_never_combine(self):
        self.assertTrue(all(not r["fallback_required"] for r in classify([run(2, "a"), run(1, "b")])))

    def test_different_workflows_never_combine(self):
        self.assertTrue(all(not r["fallback_required"] for r in classify([run(2, workflow=8), run(1)])))

    def test_success_resets(self):
        self.assertFalse(classify([run(3), run(2, conclusion="success"), run(1)])[0]["fallback_required"])

    def test_pending_ignored(self):
        self.assertTrue(classify([run(3, status="queued"), run(2), run(1)])[0]["fallback_required"])

    def test_cancelled_breaks_streak(self):
        self.assertFalse(classify([run(3), run(2, conclusion="cancelled"), run(1)])[0]["fallback_required"])

    def test_no_cause_assumed(self):
        self.assertEqual(classify([run(2), run(1)])[0]["failure_cause"], "unclassified")


if __name__ == "__main__":
    unittest.main()
