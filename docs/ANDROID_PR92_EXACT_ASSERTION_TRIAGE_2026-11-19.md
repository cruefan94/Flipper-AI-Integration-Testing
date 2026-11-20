# Android PR #92: exact failing assertion and safe integration handoff

Date: 2026-11-19 America/Toronto (Actions logs timestamp 2026-11-20 UTC). Public-safe diagnosis only.

## Evidence
- Android PR: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/92
- Exact head: `f9e1639975071fc4cf6cb74508748f9b46ae95c2`
- Failed completed run: https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44670603238
- Failed job ID: `136070360450`, step `One-time Android source, JVM and security regressions`
- Failing test: `test_ble_manual_stop_recovery_source.ManualDisconnectRecoveryTests.test_delayed_recovery_rechecks_stop_token_and_device`.
- Assertion reports regex `final int token=\\+\\+recoveryToken;` did not match the source, which contains `final int token=++recoveryToken;` (with spaces around assignment). The expected expression is too whitespace-sensitive. This is a *source assertion failure*, not proof that BLE runtime behavior is defective; do not classify as a runner/billing failure.
- Recommendation for Android branch owner: revise only the test's expression to permit whitespace, e.g. `r"final\\s+int\\s+token\\s*=\\s*\\+\\+recoveryToken\\s*;"`, while retaining assertions that manual disconnect invalidates pending retry callbacks and rechecks selected device. Run the focused test, then complete exact-head CI. Do not alter Android feature source here.

## Two-failure gate
This is one completed failing attempt for this workflow/branch as observed. Before retry, inspect latest run history; after two consecutive completed failures on the same workflow/branch (or repeated pre-provision failure), invoke the approved public-safe fallback, record both run IDs and fallback ID, and never publish private firmware/source, binaries, credentials or logs. Private Actions-read 403 means BLOCKED, not success.

## Unified release hold
- Android APK: exact-head regression failed; signer, package identity, versionCode and data-preserving update compatibility unverified. No replacement/uninstall.
- Native F7 updater: private PR #71 C2 audit remains failed; diagnostic-only fallback is not a native build. Real `firmware.dfu` suffix CRC, C2 boundary, internal hashes and encrypted artifact identity remain unverified. Never retry CRC 9-99 updater.
- BLE AI1: host test is not paired device acceptance. Require firmware and Android exact SHAs, protocol/version match, handshake, disconnect/reconnect, background and malformed-frame tests.
- Pi/ESP32/radio/voice/Termux: separate gates until actual integration evidence.
- No promotion, production merge, flashing, installation, or secrets disclosure.
