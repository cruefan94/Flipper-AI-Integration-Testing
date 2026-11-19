"""Public-safe, offline regression tests for the owner's two-failure routing policy.

No GitHub credentials, network calls, private source or artifacts are accessed.
Run: python3 -m unittest discover -s tests -p 'test_failover_same_branch_evidence.py'
"""
import unittest


def classify_recent_runs(runs, *, workflow, branch, private_actions_access=True):
    """Return a fail-closed, sanitized decision from newest-first run metadata.

    Each run has: id, workflow, branch, status, conclusion, job_provisioned.
    Only consecutive *completed attempts* of the same workflow and branch count.
    An unprovisioned repeat is a separate fallback trigger. Infrastructure and
    source failures both count, but their root causes must be diagnosed separately.
    """
    if not private_actions_access:
        return {"decision": "BLOCKED", "run_ids": [], "reason": "PRIVATE_ACTIONS_READ"}
    scoped = [r for r in runs if r["workflow"] == workflow and r["branch"] == branch]
    completed = [r for r in scoped if r["status"] == "completed"]
    failed = []
    for r in completed:
        if r["conclusion"] != "failure":
            break
        failed.append(r["id"])
        if len(failed) == 2:
            return {"decision": "FALLBACK_REQUIRED", "run_ids": failed, "reason": "TWO_COMPLETED_FAILURES"}
    # Repeated pre-job failures are independently actionable, even if the
    # provider marks them completed with failure. Never count queued attempts.
    no_job = [r["id"] for r in scoped if r["status"] == "completed"
              and r["conclusion"] == "failure" and r.get("job_provisioned") is False]
    if len(no_job) >= 2:
        return {"decision": "FALLBACK_REQUIRED", "run_ids": no_job[:2], "reason": "REPEATED_NO_JOB"}
    return {"decision": "NO_TRIGGER", "run_ids": failed, "reason": "INSUFFICIENT_FAILURE_EVIDENCE"}


def run(id, workflow="native-f7", branch="candidate", status="completed",
        conclusion="failure", job_provisioned=True):
    return dict(id=id, workflow=workflow, branch=branch, status=status,
                conclusion=conclusion, job_provisioned=job_provisioned)


class TwoFailureRoutingTests(unittest.TestCase):
    def decide(self, runs, **kw):
        return classify_recent_runs(runs, workflow="native-f7", branch="candidate", **kw)

    def test_two_consecutive_completed_failures(self):
        self.assertEqual(self.decide([run(9), run(8)])["decision"], "FALLBACK_REQUIRED")

    def test_one_failure_not_enough(self):
        self.assertEqual(self.decide([run(9)])["decision"], "NO_TRIGGER")

    def test_success_resets_streak(self):
        self.assertEqual(self.decide([run(9), run(8, conclusion="success"), run(7)])["decision"], "NO_TRIGGER")

    def test_other_branch_does_not_count(self):
        self.assertEqual(self.decide([run(9), run(8, branch="other")])["decision"], "NO_TRIGGER")

    def test_other_workflow_does_not_count(self):
        self.assertEqual(self.decide([run(9), run(8, workflow="source")])["decision"], "NO_TRIGGER")

    def test_queued_run_does_not_count_as_failure(self):
        self.assertEqual(self.decide([run(9, status="queued", conclusion=None), run(8)])["decision"], "NO_TRIGGER")

    def test_cancelled_run_breaks_streak(self):
        self.assertEqual(self.decide([run(9, conclusion="cancelled"), run(8)])["decision"], "NO_TRIGGER")

    def test_repeated_no_job_triggers(self):
        r = self.decide([run(9, job_provisioned=False), run(8, job_provisioned=False)])
        self.assertEqual((r["decision"], r["reason"]), ("FALLBACK_REQUIRED", "TWO_COMPLETED_FAILURES"))

    def test_private_read_403_blocks(self):
        self.assertEqual(self.decide([run(9), run(8)], private_actions_access=False)["decision"], "BLOCKED")

    def test_no_secret_or_source_in_decision(self):
        self.assertEqual(set(self.decide([run(9), run(8)])), {"decision", "run_ids", "reason"})


if __name__ == "__main__":
    unittest.main()
