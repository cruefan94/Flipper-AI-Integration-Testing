# Combined Android failure routing and native F7 attempt evidence — 2026-11-17

Public-safe audit only. No private source, binaries, logs, credentials, or personal diagnostics.

## Exact observed evidence

- Android combined workflow `420703090`, branch `feature/ai1-background-service-dispatch-20261116`: completed failures [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456). Latest failing head `7aae70bd7fd7dc93a4f452025d5fdb960b84d8df`. **Two-failure fallback trigger met**. Do not repeatedly rerun the same failing branch.
- Latest Android job `134468338944`: runner setup, JDK, Android SDK and Gradle setup succeeded; **One-time Android source, JVM and security regressions** failed. APK compilation and APK upload were skipped. Classify as source/regression failure pending sanitized failing assertion, not as billing/runner failure.
- [Native encrypted F7 run 44180961225](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225): latest attempt **2** completed success; public workflow head `fc6c9e462295ff2fdfae9a481580965d5c408e55`. The latest `custom-firmware` job succeeded. Two encrypted, explicitly UNTESTED artifacts remain listed, one per attempt. **Only attempt 2 may be considered current**, subject to independent private source SHA, real DFU CRC, manifest and SHA-256 verification. Artifact display-name SHA must not substitute for authoritative private source SHA.
- [Older run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): completed success, but superseded as candidate evidence. [F7 source gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains under review.
- Owner-approved coordination gates: [private release blockers PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), [test-only fallback coverage PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23), and [private tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).

## Fail-closed next actions

1. Authorized integration-testing owner: invoke the **approved public-safe** fallback route for the Android same-workflow/same-branch pair, if it supports that workflow; record actual dispatch ID and outcome. Never pass private source, firmware binaries, logs, tokens or personal diagnostics. If the approved route cannot accept Android, mark **BLOCKED / route incompatible** and escalate without repurposing a private firmware route.
2. Android owner: inspect the failed source/JVM/security regression assertion through authorized logs, fix in the owning branch, run exact-head regression, then build a distinct opt-in test APK. Do not uninstall/replace the installed APK; compare signing certificate and package/version compatibility before any upgrade.
3. Firmware owner: confirm exact private SHA for native attempt 2, validate real `firmware.dfu` header/suffix CRC and updater contents, record SHA-256 in the **private** ledger, verify encrypted-only artifact access, and retain qFlipper restore instructions. The CRC 9-99 artifact remains quarantined.
4. Integration owner: require matching BLE AI1 revision and tested HELLO/ASK, reconnect, consent and stale-response behavior before either candidate promotion. Optional Pi/ESP32/radio hardware stays separate until compatible.
5. Maintain no production merges, flashing, installs or deployment. Passing host checks never equal physical hardware verification.

## Release ledger (public-safe)

| Candidate | Evidence | Release state |
| --- | --- | --- |
| Android combined test APK | Two failed host regression runs; no latest APK build | HOLD |
| F7 encrypted native updater | Attempt 2 host job success; private provenance and device acceptance not published | HOLD |
| BLE AI1 cross-device | No verified physical handshake at matched revisions | HOLD |
| Pi / ESP32 / radio / voice | No verified promotion to unified candidates | OPTIONAL / HOLD |
