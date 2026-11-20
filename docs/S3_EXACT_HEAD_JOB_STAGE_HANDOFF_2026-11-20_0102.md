# Exact-head S3 failure triage and release handoff — 2026-11-20 01:02 ET

PUBLIC-SAFE, **documentation only**. This report contains no private firmware source, logs, binaries, secrets, device identifiers or private build artifacts. It is not a release approval.

## Pinned evidence
- Private firmware draft [PR #72](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/72), head `94253300aa7a1379e5eeb3f11156f78f8b0d0b96`, has **three distinct completed failing workflows**:
  - [S3 bridge #44672970355](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970355): job `136078025792` **failure**, S3 compile job `136078041282` **skipped**, external FAP compile `136078041347` **skipped**.
  - [F7 candidate #44672970526](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970526): quick checks job `136078026964` **failure**, native F7 compile `136078029077` **skipped**, draft packaging `136078028902` **skipped**.
  - [Standalone FAP #44672970371](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970371): workflow **failure**; exact failed step not classified here.
- Public-safe [triage PR #212](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/212), head `3d2efe05ee46279a1d1cb9a4c095f2536d0dbec8`, [smoke #44677980303](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44677980303) **success**. Public smoke does **not** prove native compile.
- Android [PR #93](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/93), head `dcbd749571f0f9c77a1f05870da69ad5833b0aa9`, [combined APK #44676544922](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44676544922) **success**. Installed APK signer/versionCode continuity and BLE hardware remain **unverified**.
- Pi/ESP safety [PR #214](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/214), head `7498b2dee686018e3ee72b52863d858b4d42644e`, [smoke #44680451727](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44680451727) **success**, physical acceptance **unverified**.

## Required private-only corrective steps
1. Firmware owner retrieves **private** failed-job logs for each job above, identifies first failing command/assertion and labels it CODE, RUNNER/INFRA, PERMISSION, or UNKNOWN. The jobs were provisioned in the two inspected workflows; do **not** label billing without evidence. Do not copy raw private logs into public.
2. For each **same workflow + same branch**, inspect consecutive *completed* attempts. Three distinct workflows failing once do not constitute the two-consecutive-failure threshold. On the second completed failure, or repeated pre-provision failure, invoke the approved PUBLIC-SAFE private-firmware fallback; record triggering run IDs and actual fallback run ID. If Actions:read yields 403 or required permissions are absent, mark **BLOCKED**, not successful.
3. Fix the exact source/CI failure on its owning private feature branch; require passing exact-head checks **and** actual native compile. Avoid changing this integration release-ledger branch.
4. Native F7 gate: authoritative C2 linker/image boundary, real `firmware.dfu` suffix CRC, updater internal checksums, `update.fuf` consistency, SHA-256, encrypted-only artifact identity and verified qFlipper recovery instructions. **Never retry CRC 9-99 updater.** Historical [#43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) does not validate current SHA.
5. Android gate: compare installed signer certificate digest, package ID and monotonically increasing versionCode against exact test APK without uninstalling or replacing the installed app. Side-by-side APK only with explicit owner opt-in.
6. AI1 gate: verify exact UUID/roles and framing `AI1|TYPE|request_id|payload\n`, authentication, reconnect generation, HELLO/ACK, request correlation, timeout and malformed-frame rejection across pinned Android/firmware commits. Stock Momentum RPC is not AI1.
7. ESP32-S3 GPIO 16/17 remains provisional. No wiring or flash until board identification, 3.3V logic and ground/power safety verified.

## Candidate ledger (not promoted)
| Candidate | Pinned source | Build/acceptance |
|---|---|---|
| Android test APK | PR #93 `dcbd7495` | Combined CI success; signer/upgrade/hardware HOLD |
| Native Momentum F7 .tgz | PR #72 `94253300` | Quick checks failed, native compile skipped; CRC/hash/recovery HOLD |
| S3 external bridge/FAP | PR #72 `94253300` | Offline source failed; compile skipped; separate optional prototype |
| Pi/qFlipper | PR #214 `7498b2de` | Public smoke passed; physical safety gate pending |

Source owner handoff: provide exact repaired commit, workflow and run URL, test stage outcome and provenance; integration-testing workstream alone owns the combined candidate release ledger. Preserve [private Phase 1 PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and [public-safe fallback PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23). No production merge, device flash, APK install or cloud deployment.
