"""Public-safe, offline CI failure classifier. No GitHub access or secrets.

Input is an explicitly sanitized list of run summaries; never feed private logs.
Only completed failures on the same repository, branch AND workflow count.
"""
from collections import defaultdict


def classify(runs):
    """Return per-key decisions; newest records are sorted by completed_at then run_id.

    Status 'no_job' represents a repeated pre-provisioning failure, which is
    eligible for the approved fallback after two observations. Unknown
    status, permissions errors, or incomplete runs fail closed.
    """
    groups = defaultdict(list)
    for run in runs:
        key = (run["repository"], run["branch"], run["workflow"])
        groups[key].append(run)
    decisions = {}
    for key, items in groups.items():
        ordered = sorted(items, key=lambda r: (r["completed_at"], r["run_id"]))
        failures = []
        for run in reversed(ordered):
            if run.get("access") != "accessible":
                decisions[key] = {"status": "BLOCKED", "run_ids": [], "reason": "Actions read unavailable"}
                break
            if run.get("status") != "completed":
                decisions[key] = {"status": "WAIT", "run_ids": [], "reason": "latest run incomplete"}
                break
            if run.get("conclusion") == "success":
                decisions[key] = {"status": "NO_FALLBACK", "run_ids": [], "reason": "latest run passed"}
                break
            if run.get("conclusion") != "failure":
                decisions[key] = {"status": "REVIEW", "run_ids": [], "reason": "unknown/cancelled conclusion"}
                break
            if run.get("jobs") not in ("failed", "no_job"):
                decisions[key] = {"status": "REVIEW", "run_ids": [], "reason": "failure type not established"}
                break
            failures.append(run)
            if len(failures) == 2:
                decisions[key] = {
                    "status": "FALLBACK_REQUIRED",
                    "run_ids": [r["run_id"] for r in reversed(failures)],
                    "reason": "two consecutive completed failures on identical workflow and branch",
                }
                break
        else:
            decisions[key] = {"status": "WAIT", "run_ids": [r["run_id"] for r in failures], "reason": "fewer than two completed failures"}
    return decisions
