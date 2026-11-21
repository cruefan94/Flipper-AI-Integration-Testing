# Termux / GitHub remote diagnostics — read-only, public-safe preflight

Updated 2026-11-21. This is a **manual** owner-operated guide, not a remote device bridge deployment or evidence of successful hardware operation.

## Scope and privacy

Use a Termux shell on Android or an SSH shell on the owner's Pi to inspect **public** GitHub workflow metadata. Never copy private firmware source, artifacts, raw CI logs, authentication tokens, device serial numbers, BLE addresses, Wi-Fi details, IP addresses, installed-app data, or personal diagnostic dumps into public issues or artifacts. Do not run `set -x`, `env`, `printenv`, `gh auth token`, or `curl -v` in shared transcripts. Do not pipe downloaded scripts to a shell. This preflight does not install APKs or flash devices.

## Minimal public read-only commands

Prerequisites: `python3` and `curl` available, with network access. No GitHub token needed for public endpoints; unauthenticated API rate limits apply. These commands emit only public workflow metadata.

```sh
for repo in Flipper-AI-Android-Satellite Flipper-AI-Integration-Testing; do
  printf '\n== %s ==\n' "$repo"
  curl --fail --silent --show-error --max-time 15 \
    "https://api.github.com/repos/cruefan94/$repo/actions/runs?per_page=5" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); [print(x["id"],x["head_branch"],x["head_sha"],x["status"],x["conclusion"]) for x in d.get("workflow_runs",[])]'
done
```

If `curl` fails, report only HTTP status/category and repository name; do not publish raw headers. This output cannot establish artifact integrity, signing compatibility, or device readiness.

## Private Momentum metadata and two-failure fallback

Do **not** call private Momentum endpoints from public CI or include any private URL-bearing request headers in logs. An owner-approved private monitor must have scoped Actions:read permission. HTTP 401/403 or missing credential means **BLOCKED**, not a successful fallback and not proof of a billing problem. After two completed failures on the same branch and workflow (or repeated pre-provisioning failure), use only the approved private-safe fallback route; record run IDs and sanitized statuses privately in Momentum issue #5. A public workflow may receive fixed labels such as `PRIVATE_ACTIONS_ACCESS_BLOCKED` but never private source, artifacts, tokens or raw logs.

## Cross-component acceptance checklist

- AI1: pin exact Android and firmware commits, UUID/characteristic contract revision, authentication, framing, UTF-8, CCCD, reconnect/session invalidation and denial behavior; host success is not physical BLE proof.
- Android: compare installed and proposed APK signing certificate digests **privately**, package name, monotonically increasing versionCode, and non-destructive upgrade plan. On mismatch, **do not uninstall/replace**; a separately identified test APK requires explicit approval.
- F7: privately verify extracted genuine `firmware.dfu` suffix CRC, package contents and SHA-256, source SHA, target F7/C2 boundaries and recovery procedure. Synthetic CRC success or encrypted compilation alone is insufficient. Never retry the known failed CRC 9-99 image.
- Pi/ESP32/Arduino/radio: maintain independent compatibility and voltage/legal/safety gates. No promotion based on a passing synthetic fixture alone.

## Handoff template (private tracker)

```text
Workstream:
Repository / branch / exact SHA:
PR / Actions run IDs / completed conclusions:
Failure class (code / runner / permission / unknown):
Fallback run ID or BLOCKED reason:
AI1 contract revision and dependency refs:
Android test APK: candidate ID / signing & versionCode gate / HOLD:
F7 updater: candidate ID / genuine CRC & hashes / HOLD:
Hardware acceptance: NOT TESTED unless owner verified:
Next isolated action:
```

No production merges, remote deployment, hardware flash, or installation are authorized by this guide.
