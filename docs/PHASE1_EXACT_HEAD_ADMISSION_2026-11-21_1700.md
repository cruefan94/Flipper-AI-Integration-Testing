# Phase 1 exact-head release handoff — 2026-11-21 17:00 EST

Public-safe metadata only. No private firmware, artifact contents, device logs, tokens, certificate fingerprints, or credentials.

## Current independently scoped checks

| Workstream | Head SHA | Evidence | Admission |
| --- | --- | --- | --- |
| Android opt-in side-by-side PR [#114](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/114) | `939b8e5f997ab5d43fd8b8f206137283329c7691` | [combined APK CI #44948078014](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44948078014) completed success | HOLD: actual APK signing certificate, package ID, versionCode, on-device BLE AI1 and owner opt-in not proven |
| FlipperHTTP PR [#81](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/81) | `869484d9505244715604809421ac473a7f6c51f4` | [read-only probe #44936047367](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44936047367) completed failure | BLOCKED: native FAP skipped/not accepted; classify job failure from authorized logs |
| Arduino/ESP32 manifest PR [#319](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/319) | `5e81d9866ec62635e9f0dbc6e096e8be397330d2` | [offline regression #44951648216](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44951648216) success | Optional hardware only, no candidate promotion |
| F7 synthetic CRC PR [#22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) | `32f631c846db67d5f581887c00bbd06599b665c6` | historical native [#43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) success on *different* pinned source | HOLD: real updater `firmware.dfu` suffix CRC, internal SHA-256, private source SHA, manifest, encrypted artifact identity and qFlipper recovery |

## Explicit release checks (not performed by this document)

1. **Android:** on an authorized isolated test artifact, extract actual package name, versionCode and signing certificate digest; compare with installed app metadata *privately*. Different signing identity for the same package means no in-place upgrade; use separately named opt-in test application only with owner consent. Never uninstall existing app.
2. **F7:** inside an approved private-only build environment, check actual extracted `firmware.dfu` 16-byte suffix and whole-file CRC, internal file hashes, signed/encrypted artifact provenance and exact private source SHA. Synthetic CRC tests and successful archive upload do not satisfy this. Keep CRC 9-99 artifact prohibited.
3. **AI1:** compare Android/firmware/ESP32 request/response framing, UTF-8 limits, reconnect epochs and error codes against the pinned contract; require cross-component CI and physical owner-operated acceptance before promotion.
4. **Recovery:** prepare official compatible Momentum updater, SD backup and qFlipper recovery instructions *before* owner-approved flashing; do not claim restoration tested without device evidence.
5. **Two-failure routing:** group completed attempts by exact repository + workflow + branch, not by PR stack or commit alone. After two consecutive failures, or repeated failure before runner provisioning, dispatch approved public-safe fallback. If private Actions:read is 403/missing, record **BLOCKED**, run IDs and needed permissions; never publish private build bytes or logs.

## Coordination

Owner-approved blockers: [private Momentum PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23). Failover visibility: [integration PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23). Canonical private handoff: [Momentum issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).

This document is a handoff, **not** a unified build candidate or tested release. No production merge, install, flash or source feature modification.
