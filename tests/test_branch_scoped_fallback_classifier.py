"""Synthetic-only regression tests for branch-scoped fallback decisions."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from branch_scoped_fallback_classifier import classify


def run(number, *, branch="candidate", workflow="native-f7", status="completed",
        conclusion="failure", jobs="failed", access="accessible"):
    return dict(repository="private-placeholder", branch=branch, workflow=workflow,
                run_id=number, completed_at=f"2026-11-22T00:{number:02d}:00Z",
                status=status, conclusion=conclusion, jobs=jobs, access=access)


class FallbackClassifierTests(unittest.TestCase):
    def decision(self, runs):
        return next(iter(classify(runs).values()))

    def test_two_failures_require_fallback(self):
        d = self.decision([run(1), run(2)])
        self.assertEqual(d["status"], "FALLBACK_REQUIRED")
        self.assertEqual(d["run_ids"], [1, 2])

    def test_repeated_no_job_provisioning_failure(self):
        self.assertEqual(self.decision([run(1, jobs="no_job"), run(2, jobs="no_job")])["status"], "FALLBACK_REQUIRED")

    def test_success_resets_consecutive_failure_count(self):
        self.assertEqual(self.decision([run(1), run(2, conclusion="success"), run(3)])["status"], "WAIT")

    def test_different_workflows_do_not_accumulate(self):
        decisions = classify([run(1), run(2, workflow="protocol")])
        self.assertEqual({v["status"] for v in decisions.values()}, {"WAIT"})

    def test_different_branches_do_not_accumulate(self):
        decisions = classify([run(1), run(2, branch="other")])
        self.assertEqual({v["status"] for v in decisions.values()}, {"WAIT"})

    def test_incomplete_latest_run_not_counted(self):
        self.assertEqual(self.decision([run(1), run(2, status="queued")])["status"], "WAIT")

    def test_private_actions_read_denied_is_blocked(self):
        self.assertEqual(self.decision([run(1), run(2, access="denied")])["status"], "BLOCKED")

    def test_cancelled_does_not_count(self):
        self.assertEqual(self.decision([run(1), run(2, conclusion="cancelled")])["status"], "REVIEW")

    def test_unknown_job_evidence_does_not_count(self):
        self.assertEqual(self.decision([run(1), run(2, jobs="unknown")])["status"], "REVIEW")


if __name__ == "__main__":
    unittest.main()
