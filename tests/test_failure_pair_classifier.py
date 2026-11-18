"""Public-safe, offline regression gate for the two-failure fallback policy.

Only sanitized GitHub run metadata is accepted. No tokens, logs or firmware source.
Run: python3 -m unittest discover -s tests -p 'test_failure_pair_classifier.py'
"""
import unittest

def classify(runs):
    """Return eligible same-repo/workflow/branch failure pairs, newest first.

    A successful completed attempt resets the consecutive failure count.
    Cancelled/skipped/queued runs are not completed failing attempts.
    Different workflows and branches must never be combined.
    """
    groups = {}
    for run in runs:
        required = ("id", "repository", "workflow", "branch", "status", "conclusion", "created_at")
        if any(not run.get(k) for k in required):
            raise ValueError("missing required run metadata")
        key = (run["repository"], run["workflow"], run["branch"])
        groups.setdefault(key, []).append(run)
    pairs = []
    for key, items in groups.items():
        streak = []
        for run in sorted(items, key=lambda r: (r["created_at"], r["id"])):
            if run["status"] != "completed" or run["conclusion"] in ("cancelled", "skipped", "neutral"):
                continue
            if run["conclusion"] == "failure":
                streak.append(run["id"])
                if len(streak) == 2:
                    pairs.append({"repository": key[0], "workflow": key[1],
                                  "branch": key[2], "failed_run_ids": streak.copy()})
                # Do not dispatch repeatedly for 3+ failures in one streak.
            else:
                streak = []
    return pairs

def run(i, workflow="native", branch="feature", conclusion="failure", status="completed"):
    return dict(id=i, repository="owner/private", workflow=workflow, branch=branch,
                status=status, conclusion=conclusion, created_at=f"2026-11-18T{i:02d}:00:00Z")

class FailurePairTests(unittest.TestCase):
    def test_two_same_workflow_branch(self):
        self.assertEqual(classify([run(1), run(2)])[0]["failed_run_ids"], [1, 2])
    def test_different_workflows_do_not_pair(self):
        self.assertEqual(classify([run(1, "native"), run(2, "inventory")]), [])
    def test_different_branches_do_not_pair(self):
        self.assertEqual(classify([run(1, branch="a"), run(2, branch="b")]), [])
    def test_success_resets_streak(self):
        self.assertEqual(classify([run(1), run(2, conclusion="success"), run(3)]), [])
    def test_cancelled_not_a_failure(self):
        self.assertEqual(classify([run(1), run(2, conclusion="cancelled")]), [])
    def test_queued_not_a_failure(self):
        self.assertEqual(classify([run(1), run(2, status="queued")]), [])
    def test_out_of_order(self):
        self.assertEqual(classify([run(2), run(1)])[0]["failed_run_ids"], [1, 2])
    def test_only_one_dispatch_per_streak(self):
        self.assertEqual(len(classify([run(1), run(2), run(3)])), 1)
    def test_missing_metadata_fail_closed(self):
        with self.assertRaises(ValueError):
            classify([{"id": 1}])
    def test_same_name_other_repository_does_not_pair(self):
        other = run(2)
        other["repository"] = "owner/other"
        self.assertEqual(classify([run(1), other]), [])

if __name__ == "__main__":
    unittest.main()
