#!/usr/bin/env python3
"""Public-safe GitHub Actions failover dispatcher.

Watch the private Momentum and public Android build pipelines. A known billing/
runner/pre-job failure routes immediately; two consecutive failures of the same
workflow+branch route to an independent public integration runner. Never clone,
publish or mirror private source in this script. All targets are allowlisted.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://api.github.com"
TARGET = "cruefan94/Flipper-AI-Integration-Testing"
MONITORED = (
    "cruefan94/Flipper-AI-Momentum-",
    "cruefan94/Flipper-AI-Android-Satellite",
)
WORKFLOW = "ci-fallback-verify.yml"
MAX_AGE = timedelta(days=4)
MAX_DISPATCHES = 3
AGENT = "flipper-ai-public-ci-failover/1.0"
FAILURES = {"failure", "timed_out", "startup_failure"}


class ApiError(RuntimeError):
    pass


def api(path: str, token: str, method: str = "GET", payload: dict | None = None):
    if not path.startswith("/") or ".." in path:
        raise ValueError("Invalid GitHub API path")
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(
        BASE + path,
        data=data,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": "Bearer " + token,
            "User-Agent": AGENT,
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
        method=method,
    )
    try:
        with urlopen(request, timeout=25) as response:
            raw = response.read(2_000_000)
            return json.loads(raw) if raw else {}
    except HTTPError as error:
        raise ApiError(f"GitHub returned HTTP {error.code} on {method} {path}") from None
    except URLError:
        raise ApiError(f"GitHub API unavailable for {method} {path}") from None


def timestamp(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def kind_for(repo: str, name: str) -> str:
    lower = name.lower()
    if repo == MONITORED[0]:
        if any(s in lower for s in ("flash candidate", "custom momentum", "build flipper ai", "firmware")):
            return "firmware"
        if any(s in lower for s in ("ai satellite", "gatt", "session", "ble", "protocol")):
            return "protocol"
        return "diagnostic"
    if repo == MONITORED[1]:
        if any(s in lower for s in ("apk", "android satellite", "android app")):
            return "android"
        return "contract"
    raise ValueError("Unknown source repository")


def find_candidates(repo: str, runs: list[dict], now: datetime) -> list[dict]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for run in runs:
        branch = run.get("head_branch")
        name = run.get("name")
        workflow_id = run.get("workflow_id")
        if (not branch or not name or not workflow_id or
                run.get("event") == "workflow_dispatch" and run.get("name") == "CI fallback verification"):
            continue
        if run.get("status") not in ("completed", "in_progress", "queued", "waiting", "pending"):
            continue
        # No PR forks, secrets, or arbitrary external repositories are copied.
        grouped[(workflow_id, branch)].append(run)

    candidates = []
    for (workflow_id, branch), history in grouped.items():
        history.sort(key=lambda v: (v.get("created_at") or "", v.get("run_attempt", 0)), reverse=True)
        # An active replacement run should finish before an old failed attempt is routed.
        if history[0].get("status") != "completed":
            continue
        finished = [v for v in history if v.get("status") == "completed" and v.get("conclusion") not in
                    ("cancelled", "skipped", "neutral", "action_required")]
        if not finished or finished[0].get("conclusion") not in FAILURES:
            continue
        latest = finished[0]
        if now - timestamp(latest["created_at"]) > MAX_AGE:
            continue
        if len(finished) >= 2 and finished[1].get("conclusion") in FAILURES:
            candidates.append({
                "repo": repo, "run": latest, "branch": branch,
                "kind": kind_for(repo, latest["name"]),
                "reason": "two_consecutive_failures",
            })
        else:
            candidates.append({
                "repo": repo, "run": latest, "branch": branch,
                "kind": kind_for(repo, latest["name"]),
                "reason": "inspect_pre_job",
            })
    candidates.sort(key=lambda c: c["run"]["created_at"], reverse=True)
    return candidates


def failed_previous_attempt(repo: str, run: dict, token: str) -> bool:
    """Count a true failed rerun only if GitHub confirms its prior attempt failed."""
    attempt = int(run.get("run_attempt") or 1)
    if attempt < 2:
        return False
    previous = api(
        f"/repos/{repo}/actions/runs/{run['id']}/attempts/{attempt - 1}",
        token,
    )
    return previous.get("status") == "completed" and previous.get("conclusion") in FAILURES


def trigger_id(item: dict) -> str:
    return item["repo"] + "#" + str(item["run"]["id"])


def recorded(key: str, runs: list[dict]) -> bool:
    return any(key in (run.get("display_title") or "") for run in runs)


def monitor():
    if os.environ.get("GITHUB_REPOSITORY") != TARGET:
        raise RuntimeError("Run only in the public-safe Flipper integration-testing repo")
    public_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    private_token = (os.environ.get("FLIPPER_PRIVATE_ACTIONS_READ_TOKEN")
                     or os.environ.get("FLIPPER_PRIVATE_SOURCE_TOKEN"))
    if not public_token:
        raise RuntimeError("GITHUB_TOKEN missing")
    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"

    previous = api(
        f"/repos/{TARGET}/actions/workflows/{WORKFLOW}/runs?per_page=100",
        public_token,
    ).get("workflow_runs", [])
    now = datetime.now(timezone.utc)
    pending = []
    for repo in MONITORED:
        token = private_token if repo == MONITORED[0] else public_token
        if not token:
            print(f"::warning::Private Actions-read token missing: cannot monitor {repo}")
            continue
        try:
            runs = api(f"/repos/{repo}/actions/runs?per_page=100", token).get("workflow_runs", [])
        except ApiError as error:
            # A token with Contents:read only cannot inspect private Actions.
            print(f"::warning::Cannot monitor {repo}: {error}. Grant Actions:read to an Actions-read token.")
            continue
        for item in find_candidates(repo, runs, now):
            key = trigger_id(item)
            if recorded(key, previous):
                print("Already checked:", key)
                continue
            if item["reason"] == "inspect_pre_job":
                try:
                    if failed_previous_attempt(repo, item["run"], token):
                        item["reason"] = "two_consecutive_failures"
                    else:
                        jobs = api(
                            f"/repos/{repo}/actions/runs/{item['run']['id']}/jobs?per_page=1",
                            token,
                        )
                        # SUSPECTED pre-job/runner/billing failure; not billing proof.
                        if jobs.get("total_count", len(jobs.get("jobs", []))) == 0:
                            item["reason"] = "suspected_runner_or_billing"
                        else:
                            continue
                except ApiError as error:
                    print(f"::warning::Could not inspect attempts/jobs for {key}: {error}")
                    continue
            pending.append(item)

    pending.sort(key=lambda c: c["run"]["created_at"], reverse=True)
    sent = 0
    for item in pending[:MAX_DISPATCHES]:
        key = trigger_id(item)
        print(f"Fallback route: {key} -> {item['kind']} ({item['reason']})")
        if dry_run:
            continue
        api(
            f"/repos/{TARGET}/actions/workflows/{WORKFLOW}/dispatches",
            public_token,
            "POST",
            {
                "ref": "main",
                "inputs": {
                    "source_repo": item["repo"],
                    "source_run_id": str(item["run"]["id"]),
                    "source_sha": item["run"]["head_sha"],
                    "source_branch": item["branch"],
                    "kind": item["kind"],
                    "reason": item["reason"],
                },
            },
        )
        sent += 1
    print(f"Failover scan complete. Dispatched {sent}; queued candidates {len(pending)}.")
    if any(c["kind"] == "diagnostic" for c in pending):
        print("::notice::Unmapped source workflows get diagnostic checks, not an equivalent build.")


if __name__ == "__main__":
    try:
        monitor()
    except (ApiError, ValueError, RuntimeError, KeyError) as error:
        print(f"::error::{error}", file=sys.stderr)
        raise SystemExit(1)
