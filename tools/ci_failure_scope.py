#!/usr/bin/env python3
"""Public-safe CI failure routing. Accept GitHub Actions metadata only, never logs."""
import argparse
import json
from pathlib import Path


def classify(runs):
    """Runs newest first. Count completed failures per exact repo/branch/workflow.

    A completed success resets the consecutive failure count. Pending attempts
    are ignored, and different branches/workflows never share a counter.
    """
    groups = {}
    for run in runs:
        key = (run.get("repository"), run.get("head_branch"), run.get("workflow_id"))
        if not all(key):
            raise ValueError("repository, head_branch and workflow_id required")
        if run.get("status") != "completed":
            continue
        groups.setdefault(key, []).append(run)
    results = []
    for key, items in groups.items():
        items.sort(key=lambda x: (x.get("run_started_at") or x.get("created_at") or "", int(x.get("run_attempt", 1)), int(x["id"])), reverse=True)
        failures = []
        for item in items:
            if item.get("conclusion") == "success":
                break
            if item.get("conclusion") == "failure":
                failures.append(item["id"])
            else:
                break  # cancelled/skipped/neutral do not establish consecutive failures
        results.append({
            "repository": key[0], "branch": key[1], "workflow_id": key[2],
            "consecutive_failure_run_ids": failures,
            "fallback_required": len(failures) >= 2,
            "failure_cause": "unclassified",
            "fallback_status": "REQUIRED_NOT_DISPATCHED" if len(failures) >= 2 else "NOT_TRIGGERED",
        })
    return sorted(results, key=lambda x: (x["repository"], x["branch"], str(x["workflow_id"])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata_json", type=Path, help="sanitized Actions run metadata; never supply logs or tokens")
    args = parser.parse_args()
    runs = json.loads(args.metadata_json.read_text(encoding="utf-8"))
    if not isinstance(runs, list):
        parser.error("input must be an array")
    print(json.dumps(classify(runs), indent=2))


if __name__ == "__main__":
    main()
