# Android AI1 readiness regression: exact-head repair evidence (2026-11-20)

Public-safe integration handoff; **not** a release approval.

## Observed results

| Android source | PR | Exact head | Combined APK workflow | Result |
|---|---|---|---|---|
| RPC versus AI1 readiness regression | [#101](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/101) | `3b039b82cd94b0bbc2921022f3e6ae3a6d8b3103` | [#44831627893](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44831627893) | completed failure |
| Readiness source-regression regex repair | [#102](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/102) | `d12a7f1e13f6e313cf93302a68c1995a4ce13615` | [#44839423609](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44839423609) | completed success |

These are **different branches and commits**. The second is not a retry or proof of passing the failed #101 head. Do not count them as two consecutive failures for the same workflow+branch. The passing combined APK workflow is not proof of installed-app signer continuity, device upgrade safety, or real Flipper AI1 readiness.

## Cross-component release acceptance

1. Require pinned Android and firmware source SHAs, tested workflow URLs, and explicit AI1 wire protocol/version evidence. Stock Momentum RPC connected status must never imply authenticated AI1 service readiness.
2. Confirm that the repaired source regression checks the actual code path and cannot silently pass on missing/malformed input; independently inspect test assertions before promoting.
3. Compare installed Android package ID, signing certificate SHA-256 and versionCode against the proposed test APK in a **private**, owner-consented environment. Never collect signing keys or device identifiers in public CI. A mismatch is a hard HOLD: no uninstall/replacement.
4. Keep Android PR #102 independent until its changes are reviewed for safe integration into the controlled non-production candidate; do not assume PR #101 and #102 are combined.
5. Native F7 candidate remains HOLD until the exact private source SHA, real `firmware.dfu` suffix CRC, updater SHA-256, C2 boundary and recovery procedure are verified privately. Never retry the CRC 9-99 image.
6. After two consecutive completed failures on the **same workflow and branch**, invoke the approved public-safe private-firmware fallback. A private Actions:read 403 is **BLOCKED**, not a successful fallback. Do not expose private source, logs, binaries, tokens or keys.

## Candidate ledger entry

- Android: PR #102 source regression CI PASS; APK signing/update and physical BLE AI1 acceptance HOLD; not promoted.
- F7: encrypted native fallback run [#44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608) passed build/upload; exact-artifact DFU CRC, source provenance, C2 and physical recovery HOLD; not promoted.
- ESP32-S3: same-branch host failures [#44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063) and [#44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160); fallback diagnostics [#44782519310](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782519310) are not native acceptance.

No protected merge, hardware flash, installation, public firmware disclosure or production deployment is authorized by this handoff.
