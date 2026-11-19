# Android PR #88 exact-head regression: release gate and diagnostic handoff

Date: 2026-11-19. Public-safe coordination only; no source, APK, logs, secrets, device identifiers or private firmware.

## Evidence and classification
- Android PR: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/88
- Exact head: `38d1c48ff38cc3feeb7f3f75bee2edd9a405274a`
- Branch: `fix/android-ble-status-lock-20261119-1648`
- Completed failed run: https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44622613821
- Failed job: `Host regressions + one full-feature Android APK`
- Failed step: `One-time Android source, JVM and security regressions`
- Classification: source/JVM/security regression step failure, **specific cause unknown until safe step details are reviewed**. A runner was provisioned; do not assume billing or infrastructure.
- This is **one** verified completed failure on this workflow and branch; do not claim the two-failure threshold has been reached. Older green PR #87 run 44602761921 is not exact-head evidence.

## Owner-directed repair gate
1. Android owner inspects the failed step privately and identifies the exact failing assertion/command without publishing credentials, user data, prompts, BLE identifiers or private firmware.
2. Fix on the Android-owned branch only. Do not modify it from integration-testing.
3. Run the focused failing test once, then exact-head source/JVM/security regressions and Gradle debug APK compilation. Record immutable commit SHA, job IDs, executed/skipped counts and artifact digest where authorized.
4. On **two consecutive completed failures** for the same core workflow+branch, or repeated pre-provisioning failure, invoke the established approved public-safe integration-testing fallback; record both source run IDs, fallback run ID, job scope and result. If private Actions:read is 403, mark monitoring **BLOCKED** and request appropriate permission; never fabricate success.
5. Do not promote a debug APK solely because Gradle succeeds. Verify package/applicationId, versionCode progression, signer certificate continuity, and non-destructive upgrade path before owner-approved installation. Existing signer mismatch means do not uninstall or overwrite the installed app.
6. BLE AI1: pair the exact firmware and Android commit refs, versioned HELLO/ACK contract, disconnect/reconnect, stale GATT callbacks, background session and no-engine fallback; no hardware success inferred from host tests.

## Parallel F7 safety hold
- Private C2 exact-head failures: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970 and https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991
- Public-safe fallback https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728 passed diagnostics only; native firmware job skipped.
- Historical native https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 does not validate current updater. Never retry failed CRC 9-99 updater.
- Require authoritative flash boundary, real firmware.dfu suffix CRC, internal updater hashes, encrypted-only provenance and qFlipper recovery verification before F7 candidate promotion.

## Unified candidate ledger
| Component | Exact head | Gate |
| --- | --- | --- |
| Android PR #88 | `38d1c48ff38cc3feeb7f3f75bee2edd9a405274a` | **HOLD** failed exact-head regressions; signer upgrade unverified |
| Momentum PR #71 | `238a54bfc0b1708a827d489cee5d43197871bfb3` | **HOLD** C2 audit failed twice; diagnostic fallback only |
| AI1 paired acceptance PR #193 | `6cf03ca2889f52b0dde20860a7e0f6c6bac30664` | Smoke CI passed #44615261188; paired acceptance not run |
| Pi/ESP32/radio/voice | Not pinned in this checkpoint | Optional; no promotion |

No merge, flash, install, release candidate artifact, or physical test is authorized by this document.
