# CI fallback: workflow-and-branch identity evidence (2026-11-17)

PUBLIC-SAFE coordination note only. No firmware, binaries, private logs, secrets, device identifiers, or tokens are included.

## Decision rule

Count consecutive **completed failures** only within the same repository, workflow ID and head branch. A success interrupts the streak; a cancelled or queued attempt is not a completed failure. Separately escalate repeated failures that prevent any job from being provisioned. Capture the attempt number and job provision state before classifying. Never infer billing from a failure. After the threshold, use only the approved private-safe integration-testing route; do not transfer private source or firmware to public artifacts. If private Actions read or authorized dispatch is unavailable, mark BLOCKED, retain the run IDs, and do not imply a fallback occurred.

## Current evidence to triage

| Repository / workflow | Branch | Completed run IDs | Decision |
| --- | --- | --- | --- |
| Momentum / 420935082 | feature/momentum-ai1-next-flash-20261117 | 44024430141 (failure), 44024439067 (failure) | Same workflow and branch, threshold met; inspect jobs and use approved safe fallback, subject to permissions |
| Momentum / 414157517 | feature/momentum-ai1-next-flash-20261117 | 44024410032 (failure), 44024430149 (failure) | Same workflow and branch, threshold met; investigate separately from 420935082 |
| Android / 420703090 | test/ai1-policy-revocation-inflight-20261117-0048: 44026721567 (failure); fix/ai1-revocation-epoch-20261117-0248: 44041523364 (failure) | Different branches | Do not count these as a same-branch pair; investigate test regression without false escalation |

These records describe GitHub Actions conclusions, not validated firmware or device behavior. The exact Momentum native updater remains **ON HOLD** after a real DFU header-size mismatch in integration-testing run 44023046497. A passing synthetic CRC test does not clear this hold. The known CRC 9-99 updater must never be retried.

## Evidence required before any promotion

- For each CI failure: repository, workflow ID, branch, head SHA (private tracker only where sensitive), run ID, attempt, provisioned job count, failed step, failure category, and corrective action.
- For a fallback: approved route, dispatch authority, fallback run ID, conclusion, and proof that only public-safe metadata crossed repository boundaries. If not dispatched, record **BLOCKED / no run ID**.
- For F7: exact private source SHA in private tracker, real DfuSe header/element framing, firmware.dfu suffix CRC, updater TGZ SHA-256, encrypted-only artifact provenance and expiry, and qFlipper recovery review. No physical flash without owner approval.
- For Android: exact APK package name, versionCode, signing certificate fingerprint compared with installed app, safe side-by-side behavior, and passing AI1 policy-revocation tests. Never uninstall or replace the existing app without approval.
- For BLE AI1: matched firmware/Android contract revision and real-device HELLO/ASK/ANSWER, cancellation, CCCD revocation and reconnect tests.

The integration-testing workstream alone owns the combined candidate ledger. This note is a handoff, not a release candidate and not evidence of physical acceptance.
