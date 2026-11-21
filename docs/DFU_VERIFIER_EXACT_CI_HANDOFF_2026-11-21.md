# Exact-head offline DFU verifier acceptance handoff — 2026-11-21

Scope: public-safe release evidence only. This is **not** a native F7 artifact attestation or permission to flash.

## Verified exact-head CI
- [DFU verifier PR #274](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/274), head `cb5668b9cf8703321f43f751c44168853e45680e`, [Actions #44873180128](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44873180128): completed SUCCESS. This confirms the workflow outcome, not independent validation of a real private `firmware.dfu`.
- [Release matrix PR #271](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/271), head `8d8b9054c2b39b636f7284ee829dc20071bbee52`, [Actions #44868631465](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44868631465): completed SUCCESS.
- [Historical CRC PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22), head `32f631c846db67d5f581887c00bbd06599b665c6`: [Actions #43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939) and [#43828565944](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565944) completed SUCCESS, synthetic/source only.

## Required private-only next gate
1. Resolve native F7 package identity to the exact private firmware source SHA, workflow run, artifact ID and encrypted-only delivery.
2. In an authorized **private** environment, extract the intended updater; independently validate the **actual** `firmware.dfu` suffix CRC, package manifest and internal SHA-256, C2 bounds, hardware target, and Momentum compatibility. Keep firmware binaries, internal paths, logs and credentials private.
3. Record only approved non-sensitive pass/fail metadata in public CI; keep detailed provenance in private [canonical issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5). Do not retry the CRC 9-99 failed updater.
4. Android release remains blocked until installed-vs-candidate signing certificate, package ID, increasing versionCode, BLE AI1 parity and opt-in device acceptance are proven. Do not uninstall or replace the owner's installed app.
5. Maintain the same-workflow+branch two-consecutive-failure fallback. For S3 PR #75, failures [#44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063) and [#44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160) require approved public-safe private-firmware fallback. Existing private Actions:read 403 is BLOCKED; do not call a diagnostic-only run native acceptance.

## Promotion decision
Android test APK: HOLD. Native F7 updater .tgz: HOLD. External ESP32/Pi/radio/voice components: separate acceptance gates. No protected merges, production deploy, hardware flashing or installation.
