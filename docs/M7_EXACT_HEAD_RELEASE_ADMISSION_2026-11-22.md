# M7 exact-head integration admission — 2026-11-22 22:59 America/Toronto

PUBLIC-SAFE METADATA ONLY. Review-only, not a release authorization. This document is an evidence handoff to the sole combined release-ledger owner; do not edit the shared release-candidate branch.

## New exact-head Android evidence
- PR #143: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/143
- Commit: `c8a7c88412c2b2e961eb131502f7bba34b44014b`; branch `feature/northern-ai-memory-context-m7-20261122`.
- Combined APK CI https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703969 — completed SUCCESS.
- Isolated S25 M7 encrypted-memory preview APK CI https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703986 — completed SUCCESS.
- APK metadata CI https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703984 — completed SUCCESS.
- Earlier superseded commit `1b893a6ecc66e28c58e2ff210b653e1975620684` had cancelled build runs #45106688158 and #45106688150; cancellations are not source failures or a two-failure pair.

## Admission checklist (all independent)
1. Verify SHA-256 of downloaded **exact** APK, package name, versionCode, signing certificate fingerprint against currently installed app. A green debug APK does not prove signature-compatible upgrade. No uninstall/replacement; separate opt-in test app requires owner approval.
2. Prove BLE AI1 request/response framing, version, error handling, reconnect, and C/Java parity against **pinned matching commits**; stock Momentum RPC alone is not AI1. Physical phone/Flipper acceptance still required.
3. Verify M7 encrypted-memory behavior and opt-in cloud context privacy against exact APK. No private user data, memory samples, keys or diagnostics in public CI.
4. For F7, independently validate the **actual** `firmware.dfu` suffix CRC, updater manifest and SHA-256, encrypted-only artifact provenance, exact private source SHA, native compilation, and qFlipper recovery instructions. Synthetic CRC tests are insufficient; known DFU CRC 9-99 image is quarantined.
5. FAP native compile on matching Momentum SDK remains a separate gate; native F7 firmware job passing is not proof of FAP compilation.
6. Pi/ESP32/Arduino/radio/voice modules remain optional until dependencies and safety are independently accepted.

## Current blocked evidence
- Momentum PR #88 exact head `cf738f959de58a162a83db873bcbf66c0eac72ba` had failed native FAP #45067246324 and F7 #45067246380. Classify from authorized private job metadata, not assumptions.
- Historical native F7 run #43828499328 and public PR #22 demonstrate gate development, not exact-artifact flash readiness.
- Automatic fallback monitor #45097635063 passed; firmware jobs in #45097671207 and #45097674197 passed with other scopes skipped; separate protocol fallback #45097676662 passed four protocol jobs. No cross-run claim of unified hardware success.
- Mandatory fallback: two consecutive completed failures of the same workflow+branch, or repeated pre-runner failure, triggers the approved PUBLIC-SAFE private-firmware route. Record original run IDs, fallback run ID, permission status and job scopes. Private Actions:read 403 => BLOCKED; never leak source, firmware, artifacts, logs, tokens or diagnostics publicly.

**Decision:** M7 is eligible for evidence review only, not candidate promotion. Both unified Android test APK and native Momentum F7 .tgz remain HOLD. No production merge, flashing, installation or deployment.
