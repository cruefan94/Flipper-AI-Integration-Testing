# ESP32-S3 source candidate: exact-head failure classification (2026-11-20 00:00 ET)

## Scope and provenance
Private Momentum draft PR #72, source SHA `94253300aa7a1379e5eeb3f11156f78f8b0d0b96`, targets an optional ESP32-S3 AI1 bridge and external stock-Momentum app. It is NOT an F7 release candidate. Never export private firmware source, binaries, logs, credentials, or personal diagnostics to this public repository.

## Three failed workflows are not three repeated attempts of the same workflow
- [S3 bridge + external app #44672970355](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970355): completed failure; **offline protocol/source regressions** failed; both compile jobs skipped. Failure job ID 136078025792.
- [Private F7 candidate #44672970526](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970526): completed failure; **quick source checks** failed; native TGZ and full compile skipped. Failure job ID 136078026964.
- [Standalone FAP #44672970371](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970371): completed failure; precise failing step not yet classified.
Do NOT count three different workflows as two consecutive failures of one workflow+branch. Confirm each workflow's previous completed attempt before invoking mandatory fallback; prior F7 PR #71 failures and fallback #44587016728 remain separate historical evidence.

## Corrective investigation (private-only)
1. Retrieve the failing **step names** and sanitized error classification privately for each job. Determine whether source assertions, compilation, missing dependency, permission, or runner provisioning caused each failure. Do not assume billing.
2. If one workflow on this exact branch reaches two consecutive completed failures, invoke the approved public-safe fallback with only fixed-label status summaries and opaque run IDs; if Actions:read is denied, record BLOCKED/403 and do not claim successful fallback.
3. Re-run only after a concrete corrective commit; preserve run IDs and exact SHA. Keep skipped native compile marked NOT TESTED.
4. S3 bridge must remain separate until verified protocol UUID/version, authentication, UART framing, fail-closed malformed input, and paired physical compatibility. Do not claim ESP32-S3 hardware is present or flashed.

## Android recovery and release holds
Android draft PR #93 source `dcbd749571f0f9c77a1f05870da69ad5833b0aa9`: [combined APK CI #44676544922](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44676544922) completed success. This is host CI, **not** signer-compatible in-place upgrade, BLE hardware handshake, or owner installation authorization.
Integration draft PR #210 source `b8eb7a73b7088a96e968e11f8e604f08c0c84d05`: [smoke CI #44671699408](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44671699408) completed success.

Android unified test APK: HOLD until installed signer/versionCode comparison, approved side-by-side strategy and paired AI1 checks. F7 native updater TGZ: HOLD until true firmware.dfu suffix CRC, updater internal SHA, verified C2 boundary, encrypted-only artifact identity, and recovery plan. Never retry CRC 9-99 updater. No production merge, flash, install, or release promotion.

## Handoff
Owners of firmware and Android branches retain source edits. Integration-testing workstream owns unified candidate ledger; request exact passing SHA/run/artifact digest from owners, not optimistic status. This document is public-safe diagnostic metadata only.
