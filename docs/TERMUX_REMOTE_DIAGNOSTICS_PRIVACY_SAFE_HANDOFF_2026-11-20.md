# Termux / GitHub remote diagnostics — privacy-safe handoff (2026-11-20)

**Scope:** Read-only, opt-in diagnostics from an Android Termux session. This is a runbook, not an installed bridge, remote-control service, or proof of BLE/hardware success. Do not publish private firmware source, artifacts, log bodies, device identifiers, tokens, or personally identifying diagnostics. Use the private canonical tracker for sensitive triage; public reports may contain only sanitized run IDs, status, and failure classification.

## Consent and prerequisites
1. Obtain explicit device-owner consent before running commands on the phone. Do not enable background collection, SSH exposure, remote execution, or unattended upload.
2. Install/verify GitHub CLI in Termux only through an owner-approved package source. Use a token with the *minimum* repository and Actions:read access required. Do not paste tokens into terminal transcripts or issue comments.
3. Set repository explicitly. Use a private route for Momentum. Do not assume that public Actions access implies private Actions access.

## Read-only commands (run manually; do not paste raw output publicly)
```sh
gh --version
gh auth status
gh api 'repos/cruefan94/Flipper-AI-Integration-Testing/actions/runs?per_page=5' --jq '.workflow_runs[] | [.id,.head_branch,.head_sha,.status,.conclusion] | @tsv'
gh api 'repos/cruefan94/Flipper-AI-Android-Satellite/actions/runs?per_page=5' --jq '.workflow_runs[] | [.id,.head_branch,.head_sha,.status,.conclusion] | @tsv'
```
**Do not publish** `gh auth status` output without inspection; it can reveal account, scopes, and credential location. Do not collect or upload `env`, `~/.config/gh/hosts.yml`, Termux history, Android logs, BLE MAC addresses, location, or phone serials. Avoid `set -x`.

For a *private* run, first confirm Actions:read with a scoped credential, then query metadata only in a private session:
```sh
gh api 'repos/cruefan94/Flipper-AI-Momentum-/actions/runs?per_page=5' --jq '.workflow_runs[] | [.id,.head_branch,.head_sha,.status,.conclusion] | @tsv'
```
HTTP 401/403 means **BLOCKED (authorization/permissions)**, not a source regression, runner outage, or billing conclusion. Never silently replace it with a green public diagnostic result.

## Two-failure decision gate
For each *same workflow + same branch*, order completed attempts by time. Trigger approved public-safe fallback only after two consecutive completed failures, or repeated pre-provisioning failure. A successful completed attempt resets the count. Pending/cancelled attempts are not proof of a code failure. Record both failing run URLs, the workflow, branch, source SHA, whether a job was provisioned, and the first failing step **privately**. Classify source/test failure vs runner/infrastructure vs access blocked; unknown remains unknown. Do not loop reruns or weaken acceptance gates.

Approved fallback must use the established integration-testing private-safe route. Public output is limited to sanitized status, run IDs, and encrypted-only artifact metadata approved for disclosure. No private firmware source, binary, plaintext updater, credential, or raw log is permitted in public.

## Release handoff template (metadata only)
- Repository / exact branch / full commit SHA / PR URL:
- Workflow and completed run URL; job provisioned? first failing step (private only):
- Two-failure pair and approved fallback run URL, or BLOCKED + missing permission:
- Android: package name, versionCode and signer continuity checked **privately**? (yes/no; never publish signing material):
- F7: exact private source SHA (private), real firmware.dfu CRC verified against the **actual** image? archive SHA-256 verified? C2 boundary audited? encrypted-only delivery verified?
- BLE AI1: spec/version, UUID/roles parity, negative tests, paired physical acceptance:
- Pi/ESP32/radio: optional component, dependency and hardware gate:
- Release candidate status: HOLD until all exact-artifact gates and owner approval; qFlipper recovery instructions reviewed?
- Next action / owner:

## Explicit safety holds
Never retry the known DFU CRC 9-99 updater. A synthetic CRC test or green packaging job is not proof of a corrected real image. Do not replace/uninstall the owner's installed Android app when signer continuity is unknown; any side-by-side test APK requires opt-in approval. Do not flash hardware, install an APK, merge protected branches, or promote a candidate based on this runbook. The integration-testing workstream alone owns the combined release ledger; other workstreams hand off evidence without editing shared candidates.
