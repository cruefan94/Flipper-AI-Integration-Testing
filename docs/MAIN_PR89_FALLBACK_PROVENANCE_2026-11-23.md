# MAIN integration gate: PR89 failure provenance and release admission (2026-11-23)

PUBLIC-SAFE ONLY. This is a review handoff, not release authorization or a firmware build. No private source, firmware binary, secrets, raw job logs, or owner diagnostics may be copied here.

## Exact observed failures

- Private Momentum PR #89, branch `fix/flipperhttp-exact-pong-whitespace-20261123-0133`, head `0cae6e1fb7a81928566306a53a17abb6cac75d96`.
- Full-build attempts: [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882) (prior head `6a62e9ce9ecc589d2b6024488b4effe1f6425854`) and [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592) (current head). Both completed failure on the same branch/workflow: TWO-FAILURE FALLBACK TRIGGER MET, although the source head changed. Do not mistake this for an exact-head repeated test.
- In second run, Worker unit/packaging and independent Python syntax jobs failed; native FAP and Momentum updater jobs were SKIPPED. This does not demonstrate a compiler failure. Obtain private job-step evidence to determine root cause; do not attribute to billing or runners without evidence.
- Approved public-safe private-firmware fallback must use existing reviewed route from private release-blocker PR #23 and integration test-only PR #23. Before dispatch, confirm authorized private Actions read permission, exact pinned SHA and encrypted-only artifact routing. If permission returns 403: BLOCKED, no fallback run ID, do not retry indefinitely. Record actual dispatch run ID and individual job outcomes; never copy private source or logs into public issue comments.

## Independent CI evidence

- Android Worker correction PR #146 at `c4e89edac2dcf44dd5b199296093b40f9f52a00f`: [45133595585](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45133595585) completed SUCCESS. This does not prove PR #145's earlier failed head passes, nor any Android APK compilation.
- Android M7 PR #143 at `c8a7c88412c2b2e961eb131502f7bba34b44014b`: combined APK [45106703969](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703969), isolated M7 [45106703986](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703986), metadata [45106703984](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703984) passed. Signing-certificate continuity, exact downloadable APK hash and physical BLE AI1 remain unverified.
- Historical native encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed SUCCESS with custom-firmware job successful; source regression PR #22 head `32f631c846db67d5f581887c00bbd06599b665c6` passed [43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939) and [43828565944](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565944). Neither result alone proves actual firmware.dfu suffix CRC, exact updater .tgz/member SHA-256 or safe flash.

## Release admission (all required)

1. Freeze exact firmware, Android and contract SHAs; require explicit BLE AI1 protocol/version, framing, PING/PONG, timeout, errors and reconnect parity across the FAP and APK.
2. Privately inspect the native `firmware.dfu` suffix CRC and archive/member SHA-256 for the same encrypted F7 updater, with source and run provenance; do not use CRC 9-99 failed image.
3. Confirm APK package/versionCode and signing certificate fingerprint matches installed app before an in-place upgrade. If mismatch, HOLD: do not uninstall or overwrite; any separately signed test APK requires owner approval and a nonconflicting application ID.
4. Prepare official Momentum/qFlipper recovery and backup instructions without flashing. Record exact artifact hashes and evidence in private canonical issue #5; keep public only non-sensitive status.
5. Keep Pi, ESP32, radio and voice optional until their individual compatibility/safety gates pass. No production merges, cloud deploy, hardware flash or device install.

**Current release state: HOLD** for Android test APK, **HOLD** for F7 updater, **BLOCKED** for standalone FAP native acceptance. No combined candidate promotion authorized.
