# Coordinated release evidence boundary — 2026-11-17 18:00 ET

Public-safe, documentation-only integration handoff. No private source, artifact, signing certificate, credential, logs, or device diagnostics are reproduced.

## Exact observed jobs

| Gate | GitHub evidence | What it proves | What it does not prove |
|---|---|---|---|
| Native F7 | [44180961225](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225) | custom-firmware job passed: private SHA pin check, private source checks, compile, **actual** firmware.dfu framing/CRC step, native .tgz inspection, encryption, encrypted-only upload | Independent native artifact SHA-256/source attestation disclosure to private ledger, qFlipper/device success |
| Public smoke at PR #99 head `68dd0e141b339eb1d40bdc56fad643f05b4c92d5` | [44186214927](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44186214927) | public runner/contract smoke completed successfully | Firmware or Android build acceptance |
| Combined Android | [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) | Android SDK and Gradle setup passed, source/JVM/security regression step **failed** | No APK was built: build, integrity report and upload were skipped |
| Android signer test branches | [PR #66](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/66), [PR #67](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/67) | Read-only, fail-closed synthetic signer preflight under review | Installed app signer match, actual APK upgrade safety, device acceptance |

## Candidate promotion requirements

1. **F7:** privately record exact pinned Momentum source SHA, encrypted artifact run/artifact ID, SHA-256 of encrypted package, separately verified decrypted native .tgz and firmware.dfu SHA-256, actual DFU suffix CRC result, update target, qFlipper recovery plan, and independent reviewer. Encrypted ZIP digest is **not** a native firmware hash. Never reuse the CRC 9-99 artifact.
2. **Android:** diagnose regression step 7 on run 44181012277 using authorized sanitized logs, fix in Android-owned branch, rerun exact-head source/JVM/security + complete APK build. Record APK SHA-256, package name, version code, signing certificate digest and installed-app digest via approved local-only comparison. Matching digests alone do not authorize an upgrade. Never uninstall/replace existing app.
3. **BLE AI1:** pin both exact source revisions, UUID/characteristic/role and framing contract, consent/error semantics, CCCD disconnect/reconnect behavior, and cross-component tests; physical handshake remains an independent gate.
4. **Fallback:** count consecutive completed failures by **workflow and branch**, not across PRs; after two or pre-job repeated failures invoke only approved public-safe reference-only fallback. Record triggering IDs, dispatched ID, conclusion and sanitized cause. If private Actions:read is 403/missing, mark **BLOCKED**, not success. One observed fallback dispatch does not prove automatic coverage.
5. **Optional modules:** Pi, ESP32, Arduino, radio and voice stay separately gated until compatibility, safety and provenance pass. Do not modify the shared release ledger or another workstream's feature branch concurrently.

## Status

Both coordinated deliverables **HOLD**. Native F7 compile/real DFU gate is green, but private release attestation and physical test are outstanding. Combined Android build is red with no produced APK in the cited run. No production merge, flashing, installation or cloud deployment is authorized.

Owner-approved policy references: [private Momentum PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), [public-safe failover PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23), [private tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).
