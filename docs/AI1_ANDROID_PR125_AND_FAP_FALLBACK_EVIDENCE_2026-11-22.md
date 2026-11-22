# AI1 release evidence delta — 2026-11-22 06:02 ET

Public-safe integration triage. **No private firmware source, binary, credential, token, personal device log, or build output is included.**

## Current Android regression (do not promote)
- [Android PR #125](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/125), exact head `c33f3d823f7bd4a4f6662ed76269232ded9ae18f`, branch `test/cloud-status-redaction-matrix-20261122`.
- [Combined APK run 45014436917](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45014436917): completed **failure**. Job provisioned successfully; checkout, Java, Android SDK and Gradle setup passed. The **One-time Android source, JVM and security regressions** step failed. APK build, provenance generation and APK upload were **skipped**. This is a test-stage regression, **not** evidence of an APK compilation failure or runner provisioning failure.
- [APK metadata run 45014436936](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45014436936): completed **failure**. Diagnose independently; no artifact is promoted.
- [Earlier Android PR #124 combined build 45004495801](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45004495801) and [metadata 45004495849](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45004495849) passed at `f1188d21e7ee01219a36698fdb270f69df1c407d`. Different head and branch: cannot substitute for PR #125 acceptance.

## Private native Flipper v0.8 FAP fallback
- [Private FAP PR #86](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/86), branch `fix/flipper-ai-v08-fap-ci-trigger-20261122`, head `5eed030b206e15983624107bd794ae792138d5f2`.
- [Run 45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [run 45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405) both completed failure for the same workflow and branch. Jobs have no executed steps in available job records: provisioning/infrastructure *suspected*, not proven. Do not assert billing cause.
- **Two-failure fallback threshold met.** Dispatch of the approved public-safe private-firmware fallback remains **BLOCKED / not evidenced**; private Actions:read 403 or missing dispatch permission must be explicitly surfaced. Do not treat earlier diagnostic-only green fallback runs as current native FAP or CRC acceptance.

## F7 and Android release gates
- [Historical encrypted native F7 run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): completed success, custom-firmware job and native compile/package steps passed. This does **not** prove the current candidate's actual `firmware.dfu` suffix CRC, all inner updater hashes, encrypted-only identity, or physical flash success.
- [F7 CRC PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) head `32f631c846db67d5f581887c00bbd06599b665c6`; exact-head acceptance must be checked before promotion.
- Failed DFU CRC 9-99 image is prohibited from retry. Hold Flipper `.tgz` and standalone `.fap` until actual native compile, genuine CRC/hash attestation, provenance and qFlipper recovery path are proven.
- Hold Android test APK upgrade until certificate fingerprint and versionCode continuity are checked against the installed app. Existing signing mismatch means **do not replace or uninstall**; separate test install requires explicit owner opt-in.
- Stock Momentum RPC AppStart/AppData, AI1 BLE request/reply and reconnect need cross-device acceptance; passing host codec tests are not hardware proof.

## Next owner-specific actions
1. Android feature owner: inspect the **first failed regression assertion** on PR #125 and repair on its own branch, then re-run once and attach exact head/run evidence.
2. Integration owner: obtain authorized private Actions read/dispatch permissions and invoke approved public-safe fallback, capturing fallback run ID and actual executed job scope. Never expose private firmware content.
3. Release-ledger owner only: record exact artifact SHA-256, signed APK certificate/versionCode, F7 `firmware.dfu` real suffix CRC, inner updater hashes, and compatible AI1 contract before candidate promotion. No concurrent release-branch edits.
4. Pi/ESP32/radio workstreams remain optional until their own CI and compatibility gates pass.

This is a documentation/evidence update, not a passing test, candidate promotion, hardware flash, APK installation or production merge.
