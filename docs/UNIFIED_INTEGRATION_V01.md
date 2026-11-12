# Unified Flipper AI integration checkpoint v01

This is an integration **manifest**, not a merged or hardware-verified firmware release.

## Verified component baseline (2026-11-12)

| Component | Repository | Ref | Verification |
|---|---|---|---|
| Android AI Satellite | cruefan94/Flipper-AI-Android-Satellite | fix/ai1-overflow-classification-v29 | Public GitHub Actions run 43221966349 passed: JVM protocol tests, Python security regressions, debug APK assembly and artifact upload |
| Momentum AI native code | cruefan94/Flipper-AI-Momentum- | fix/ai-client-zero-id-state-v46 | Source branch identified; integration, firmware build and hardware validation not yet verified |
| Shared AI1 contract tests | cruefan94/Flipper-AI-Integration-Testing | feature/public-ci-bootstrap-v01 | Prior public workflow runs passed; recheck against latest Android and Momentum sources |

## Integration order

1. Freeze an exact commit SHA for each component after source review. Do not infer that independent branches contain one another's fixes.
2. Compare Android `SatelliteProtocol`, `ProtocolSession`, and `SatelliteRequestHandler` against Momentum `ai_wire` and `ai_client`: 180-byte maximum, ASCII AI1 framing, request ID uint32 boundaries, NUL/CR/LF handling, replay/handshake rules and ATT MTU.
3. Add cross-language vectors for zero ID, max ID, overflow, embedded delimiters, truncation, malformed UTF-8 and reconnect.
4. Integrate BLE GATT discovery, bonded consent, subscription, request dispatch, timeout and reconnect. Source-level tests are not a substitute for physical Flipper/Android pairing.
5. Produce an Android debug APK and a separately validated Momentum firmware/FAP artifact. Do not flash or merge to main automatically.
6. Only after these pass, integrate voice, radio, Wi-Fi and GitHub capabilities into the existing Android UI.

## Safety and scope

- Preserve Momentum themes, dolphin animations, apps and ESP32-S2 functionality.
- Keep GitHub credentials on Android, never on Flipper or SD.
- No private firmware code is to be copied into this public repository without explicit review.
- No claim of on-device offline inference, BLE pairing, firmware build, or end-to-end success without corresponding evidence.
- Any AI1 parser error classification change must be reflected in tests on both sides.

## Progress gates

- [x] Android v29 CI APK build and automated tests pass
- [ ] Pin reviewed Momentum v46 commit and establish its build status
- [ ] Cross-language AI1 compatibility tests against latest source
- [ ] BLE GATT end-to-end integration
- [ ] Hardware pairing and offline inference tests
- [ ] Unified release candidate with independently installable Android APK and Flipper package
