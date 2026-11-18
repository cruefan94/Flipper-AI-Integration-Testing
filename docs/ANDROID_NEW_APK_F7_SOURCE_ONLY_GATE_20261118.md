# Cross-project exact-job release gate — 2026-11-18 08:57 ET

Public-safe coordination evidence only. No firmware source, device logs, signing identities, private artifact bytes or credentials.

## New Android candidate (not approved for installation)

- Repository: cruefan94/Flipper-AI-Android-Satellite
- Source: `2809b8a671b47136fe3d3f2385fc0e70ed9c0c2b`
- Branch: `test/android-gatt-profile-bitmask-20261118-0852` (PR #73)
- Actions run: https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44318380092
- Actual job: `Host regressions + one full-feature Android APK` — completed success
- Listed artifact: `FlipperAI-Android_20261118_run44318380092-a1_sha2809b8a6_ALLFEATURES-DEBUG-UNTESTED` (24,496,528 bytes)
- **Release gate: HOLD.** Build success does not prove the installed app signer matches, versionCode upgrade safety, persistent model/data migration, BLE AI1 physical handshake, or safe user installation. No replacement or uninstall of the owner's existing app. Device opt-in required.

## Latest private F7 diagnostic (not a native firmware build)

- Repository: cruefan94/Flipper-AI-Momentum-
- Source: `59c3eab16ae6ea9b12ae719513a7ab36b7fdb968`
- Branch: `audit/f7-c2-provenance-metadata-20261118-0836`
- Actions run: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44315616464
- Actual job: `F7 C2 fail-closed source contract only (no firmware compile)` — completed success
- **Release gate: HOLD.** This job is not a native F7 compile, updater TGZ, extracted DFU CRC verification, or proof the C2 overlap is repaired. Preserve the C2 guard and quarantine CRC 9-99 updater.

## Existing two-failure fallback

- Qualifying Momentum inventory failures: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260352832 and https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260368327 (same workflow and branch)
- Public-safe firmware fallback run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44288673073 — firmware job succeeded, other components skipped
- **Attribution not yet proven**: require trigger workflow/branch/source SHA, dispatch event/run ID and completed job evidence to match before marking policy satisfied. PR #128 has fail-closed attribution tests: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/128. Private Actions HTTP 403 is BLOCKED, not success.

## Candidate promotion checklist

1. Record exact tested firmware and Android SHAs, AI1 service/characteristic IDs, frame grammar, version negotiation and error behavior in one compatibility matrix; run matched cross-component tests.
2. Obtain non-skipped private F7 native compile with safe C2 memory layout; verify extracted **real** `firmware.dfu` suffix CRC, encrypted-only TGZ identity, SHA-256 and qFlipper recovery instructions without publishing private artifacts.
3. Verify Android APK certificate against currently installed package and monotonic versionCode before any upgrade, plus offline AI, background BLE and data preservation.
4. Treat Pi/ESP32/radio/voice as optional until independently tested and proven compatible.
5. Keep release HOLD until artifact and hardware acceptance; no protected merges, flashing, installs or production deployment.

Owner: Integration Testing workstream. Firmware and Android feature owners retain their branches. This file is a handoff, not a release ledger promotion.
