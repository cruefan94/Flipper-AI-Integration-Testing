"""Public-safe, offline two-failure decision gate. No GitHub API or secrets.

Input is a sanitized JSON list of completed workflow attempts, oldest first.
Only workflow ID, branch, run ID, status, conclusion and provisioning evidence
are accepted. This tool never dispatches workflows or accesses private repos.
"""
import json
import sys

FIELDS = {"workflow_id", "branch", "run_id", "status", "conclusion", "jobs_provisioned"}
FAIL = {"failure", "timed_out", "action_required"}
SUCCESS = {"success", "cancelled", "neutral", "skipped"}

def classify(records):
    if not isinstance(records, list) or not records:
        return "INSUFFICIENT_EVIDENCE"
    seen = set()
    streak = {}
    for row in records:
        if not isinstance(row, dict) or set(row) != FIELDS:
            return "INSUFFICIENT_EVIDENCE"
        wid, branch, rid = row["workflow_id"], row["branch"], row["run_id"]
        if (not isinstance(wid, int) or isinstance(wid, bool) or wid <= 0
                or not isinstance(rid, int) or isinstance(rid, bool) or rid <= 0
                or not isinstance(branch, str) or not branch.strip()
                or not isinstance(row["jobs_provisioned"], bool)
                or row["status"] != "completed"
                or row["conclusion"] not in FAIL | SUCCESS):
            return "INSUFFICIENT_EVIDENCE"
        if rid in seen:
            return "INSUFFICIENT_EVIDENCE"
        seen.add(rid)
        key = (wid, branch)
        if row["conclusion"] in FAIL:
            streak[key] = streak.get(key, 0) + 1
            if streak[key] >= 2:
                return "FALLBACK_REQUIRED"
        else:
            streak[key] = 0
    return "NO_TRIGGER"

def main():
    try:
        payload = json.load(sys.stdin)
        decision = classify(payload)
    except (ValueError, TypeError):
        decision = "INSUFFICIENT_EVIDENCE"
    print(decision)
    return 0 if decision != "INSUFFICIENT_EVIDENCE" else 2

if __name__ == "__main__":
    raise SystemExit(main())
