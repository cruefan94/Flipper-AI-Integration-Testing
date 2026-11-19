# F7 native C2 / updater release evidence — 2026-11-19 04:00 ET

Public-safe integration handoff. **HOLD** all native F7 updater promotion and device flashing. No private source, binaries, tokens, job logs or diagnostics are included.

## Exact evidence
- Private Momentum PR #66: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/66
- Three completed failed attempts on the same workflow and branch: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481566067 ; https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481581444 ; https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481593032
- On run 44481593032 the native integrated update job **failed**, standalone FAP, ESP32 and SD starter jobs **passed**, final combined bundle **skipped**. This is NOT a native updater release.
- Historical encrypted native build https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 has a successful custom-firmware job, but is older and is not proof of the present F7 candidate or physical safety.
- Android https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/81 and https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44482308174 have passing host/APK job evidence, not verified signing continuity or safe upgrade.
- Private release blockers: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23 ; public-safe fallback policy: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23

## Fallback disposition — REQUIRED / BLOCKED
The two-failure threshold was exceeded for the same workflow and branch. No authorized dispatch was performed; **fallback run ID: none**. The established public-safe route requires verified private Actions:read permission and an approved workflow dispatch path. A previous HTTP 403 means coverage is **BLOCKED** until a new permission check succeeds. Do not interpret this as billing failure. Never copy private firmware, build outputs, logs, keys or credentials into the public repository.

## Exact candidate acceptance checklist
1. Firmware owner diagnoses native C2/flash-layout rejection in the private repository. Preserve fail-closed flash guards; no bypass or blind retries. Pin source commit and dependencies.
2. After a genuine fix, run a non-skipped native F7 compile in a permitted private-safe workflow. Capture run ID, job conclusion, source SHA, artifact name and immutable SHA-256 privately.
3. Verify the actual packaged firmware.dfu suffix and full-file CRC against the real generated file (not synthetic fixtures), updater archive contents and checksums; confirm encrypted-only artifact handling.
4. Independently validate qFlipper recovery procedure and never reuse the prior CRC 9-99 failing artifact. Hardware flash requires owner approval.
5. Android owner supplies APK package ID, versionCode, signer certificate digest for both installed and candidate versions, artifact SHA-256 and proven compatible update path; no uninstall or replacement of existing app.
6. Compare firmware and Android BLE AI1 protocol versions, GATT characteristics, CCCD/authentication, reconnect/session invalidation and RPC-vs-AI1 status; run paired contract tests. Physical handshake remains unverified until device testing.
7. Pi, ESP32, radio, voice and Termux components remain separately gated unless exact passing build and interface evidence supports promotion.

## Release ledger
| Deliverable | Evidence | Gate |
|---|---|---|
| F7 native updater .tgz | Native integrated update failed; bundle skipped | HOLD |
| Android test APK | Host/APK CI passed; signer/versionCode comparison absent | HOLD |
| BLE AI1 | Separate source tests; no pinned paired physical evidence | HOLD |
| Pi / ESP32 / radio / voice | Separate prototypes | NOT PROMOTED |
| Two-failure fallback | Threshold met; permission/dispatch unverified | BLOCKED |

Next action: firmware owner resolves safe native C2 layout, integration owner verifies approved fallback access and dispatch, then tests exact pinned artifacts without flashing or installing.
