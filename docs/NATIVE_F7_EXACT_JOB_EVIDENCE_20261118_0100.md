# Native F7 exact-job evidence checkpoint — 2026-11-18 01:00 ET

PUBLIC-SAFE METADATA ONLY. Do not attach private firmware, unencrypted binary, tokens, keys, logs or device identifiers.

## New evidence
- Private Momentum workflow [44238360282](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238360282), branch `feature/momentum-ai1-next-flash-20261118-build-gate`, source head `1e7a412003af01653ff89dc03fee743a1e37a624`, completed SUCCESS.
- Latest-attempt job `134579872805`, **Full F7 AI1 firmware compile and strict update inspection**, completed SUCCESS (not skipped).
- Latest-attempt job `134584131021`, **Private DRAFT release with direct native TGZ download (no decryption)**, completed SUCCESS (not skipped).
- Private artifact **PRIVATE-Momentum-AI1-F7-NATIVE-TGZ-NO-DECRYPT-UNVERIFIED** exists, 12,646,893 bytes, not expired. Artifact existence and job success do **not** prove physical flashability, source-to-binary reproducibility or end-to-end BLE compatibility.
- Another workflow [44238377245](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238377245) was green while its native compile was skipped. Never substitute it for the executed job above.
- Earlier public-safe [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) succeeded and exposes only encrypted UNTESTED artifacts. Its source SHA is `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`; this is **not** the newer private build's SHA.
- Android combined build [44214146838](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44214146838) succeeded at `9da29c4fce8e82c981823c9aee0296671abfb335`, with a 24,496,527-byte DEBUG-UNTESTED artifact. Signer compatibility and phone installation are not established.
- [PR #112](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/112) exact-head public smoke [44240754261](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44240754261) succeeded at `3c5eb8a53b9b8b6d67e44445b85c9d3c60124bb2`.

## Non-negotiable promotion gates
1. Privately verify real extracted `firmware.dfu` suffix CRC and framing, updater manifest, complete file SHA-256, signed/provenanced source SHA and encrypted-only public artifact identity. Preserve the failed CRC 9-99 updater quarantine; never retry it.
2. Independently verify Android APK package ID, installed-vs-candidate signing certificates, monotonic versionCode and safe upgrade path before any opt-in install. Do not uninstall/replace existing phone app.
3. Verify matching BLE AI1 protocol/version, GATT permissions, disconnect/reconnect and consent behavior on actual paired hardware before claiming end-to-end success.
4. Maintain the two-consecutive-failure fallback by **workflow and branch**; classify runner provisioning separately from source/test failures. Historical Android combined failures [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456) still have no verified authorized Android-compatible fallback run ID. Label fallback BLOCKED; passing subsequent builds do not retroactively satisfy it.
5. Do not promote or merge candidates; no flashing, APK installation or publication. The integration-testing workstream alone owns the unified release ledger.

## Handoff
Request from firmware owner: private artifact SHA-256 manifest, real DFU CRC verification transcript/attestation (kept private), precise source provenance and qFlipper recovery acceptance. Request from Android owner: APK signing/versionCode compatibility attestation and exact cross-component AI1 test evidence. Keep ESP32/Pi/radio optional until separately verified.
