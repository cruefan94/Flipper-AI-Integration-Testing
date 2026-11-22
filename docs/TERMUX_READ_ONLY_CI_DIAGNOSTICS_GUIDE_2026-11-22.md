# Android Termux → GitHub CI diagnostics (public-safe, read-only)

Status: operator guide, **not** an implemented remote bridge. 2026-11-22.
This guide does not install anything, dispatch Actions, change device settings, or upload logs.

## Safety boundary
- Only use the public GitHub REST API for the public Android and Integration-Testing repositories. The private Momentum repository must **never** be queried with a public bridge or its private source/logs/artifacts copied to public issues.
- Do not paste personal device logs, BLE MACs, addresses, account details, API keys, signing keys, tokens, cloud endpoints, raw payloads, firmware or APK binaries into public Actions, issues or PRs.
- Public issue/PR summaries may contain only: repo name, PR number, short public commit SHA, Actions run URL/ID, status/conclusion, named gate and a manually reviewed sanitized failure category.
- No automatic diagnostic upload; manually review each line before posting. HTTP 403 means **BLOCKED / insufficient permission**, not billing failure.
- Two consecutive completed failures on the same workflow+branch (or repeated pre-job failure) trigger the existing approved public-safe fallback. Never silently retry or treat a successful monitor as proof of a dispatched fallback.

## Optional read-only Termux checks (public repositories only)
Requires an existing Termux installation, `curl`, and `python3`; no GitHub token needed. If unavailable, use the GitHub Actions web pages instead. These commands display only public run metadata locally, and do not create issues or upload files.

```sh
python3 - <<'PY'
import json, urllib.request, urllib.error
repos = (
    "cruefan94/Flipper-AI-Android-Satellite",
    "cruefan94/Flipper-AI-Integration-Testing",
)
for repo in repos:
    url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=5"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "flipper-ai-readonly-check"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.load(response)
        print("\n", repo)
        for run in payload.get("workflow_runs", []):
            print(run.get("id"), run.get("head_branch"), run.get("head_sha", "")[:12],
                  run.get("status"), run.get("conclusion"), run.get("html_url"))
    except urllib.error.HTTPError as exc:
        print(repo, "BLOCKED HTTP", exc.code)
    except (OSError, ValueError) as exc:
        print(repo, "UNVERIFIED: metadata unavailable", type(exc).__name__)
PY
```

Do **not** infer current-branch success from an older green run. Match the full head SHA, workflow, branch, attempt, job and artifact identity before release admission. A successful host regression is not proof of Android signing compatibility or a physical BLE link.

## Manual handoff template (sanitized fields only)

| Field | Required evidence |
|---|---|
| Workstream | Android / firmware / FAP / Pi / ESP32 / radio |
| Source | Repository, PR, branch and **exact** commit SHA |
| CI | Workflow name, run ID/URL, attempt, job result and failure class |
| Fallback | Two failing IDs and approved fallback ID, or **BLOCKED** with missing permission |
| APK | VersionCode, package ID, signer certificate fingerprint, APK SHA-256, test-only installation policy |
| F7 | Exact source SHA, real firmware.dfu suffix CRC, updater internal checksums, .tgz SHA-256, encrypted-only artifact identity |
| AI1 | API/version, characteristic roles, protocol test commit, actual hardware result separately |
| Candidate | HOLD until every applicable gate is independently evidenced |

Keep signing fingerprints and hashes in a private canonical ledger when combined with sensitive artifact provenance. Never publish private artifacts to this repository. Existing failed CRC 9-99 firmware is prohibited; synthetic fixture success cannot rehabilitate it. Never uninstall or replace an installed Android app with a mismatched signer. No flash/install/production merge without explicit owner approval.

Canonical private tracker: https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5
