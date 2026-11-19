# Paired release evidence delta — 2026-11-19 09:02 America/Toronto

Public-safe coordination only. This is not release authorization. No private firmware source, updater, secrets, user device diagnostics, or personal logs are included.

## Newly checked heads and CI
- Firmware PR [#69](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/69), head `b7ae14bb93e34f2e3f82079f43a8e1c2afdee120`, adds fail-closed C2 audit CLI coverage. Its exact-head CI/native updater acceptance is NOT established by this document.
- Android PR [#84](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/84), head `6ebb790539bfebc71f142b8107c61ec79f7645e9`: [Actions 44536357309](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44536357309) completed successfully, including host regressions and full-feature APK build job. APK signing certificate identity, installed-package continuity, versionCode monotonicity, artifact SHA-256, and on-device safe upgrade remain unverified. Do not replace or uninstall the installed app.
- Pi dashboard repair PR [#177](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/177), head `2d5336656cf59fc63dc0453eb13539b6d171f5b4`: [Actions 44530833357](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44530833357) completed successfully for the public smoke/contract job. This does NOT alone prove the earlier exact 11-test suite has passed on the repaired head. The original exact-suite failures were [44521022652](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521022652), [44521042473](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521042473), and [44521062532](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521062532). Do not equate smoke success with exact-suite recovery.
- Historical native encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) is completed successful but is not evidence for the current head. CRC gate [PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains open at `32f631c846db67d5f581887c00bbd06599b665c6`.

## Non-negotiable candidate gates
1. F7: independently confirm correct C2 flash boundary, successful *non-skipped* native updater compilation, actual `firmware.dfu` suffix CRC, internal `.tgz` SHA-256, pinned private source SHA, encrypted-only delivery identity, and qFlipper/DFU recovery procedure. Never retry the earlier CRC 9-99 updater. Public tracker must not contain private source/binaries.
2. Android: compare installed and candidate package IDs, signing certificate SHA-256, versionCode and downgrade behavior through a private-safe evidence path; require explicit owner consent for any separate test APK install. Preserve user data.
3. BLE AI1: pin matching firmware and Android commits, protocol version, UUID/ATT/auth/CCCD semantics, reconnect epoch behavior and real paired device handshake before claiming integrated functionality.
4. Pi/ESP32/radio/voice remain optional and separate until exact tests and interface dependencies pass.
5. Same workflow + same branch: after two consecutive completed failures, or repeated pre-job provisioning failure, invoke only the approved public-safe private-source fallback. Record original and fallback run IDs. Missing private Actions read/dispatch permission = BLOCKED, not success. Distinguish infrastructure from code faults.
6. Release ledger ownership remains with integration-testing. No protected merges, device flashes, app installs or production deployment from this document.

## Next acceptance step
Run the repaired Pi *exact* test workflow on the repair head with >=11 executed tests and zero skips; collect native F7 artifact-level CRC and SHA evidence through private-safe route; check Android signing upgrade compatibility; then run paired AI1 contract tests. Track exact refs and results in the private canonical issue #5.
