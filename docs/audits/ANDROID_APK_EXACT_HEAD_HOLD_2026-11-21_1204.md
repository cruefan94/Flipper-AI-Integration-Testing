# Android combined APK exact-head failure and release admission — 2026-11-21

PUBLIC-SAFE metadata only. No APK, private firmware, keys, logs, device identifiers, or credentials.

## Exact-head evidence
- Android PR [#112](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/112): branch `fix/android-navtest-package-identity-20261121`, head `ad0d47c94760db3819c668c0a748a527320cd42f`.
- Combined APK workflow [#44926545670](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44926545670): completed **failure** at that head. Do not call this an APK build success; job-step/root cause requires inspection. This is one observed completed failure on this exact workflow+branch, not automatically a two-failure trigger.
- Worker PR [#111](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/111), [#44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886): contract success on **different** head `994400674429cd5d05eec0bb1a6999bff151f95f`; cannot establish combined APK success.
- Integration PR [#301](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/301), smoke [#44921945553](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44921945553): passed at `3aae191593ff1a42a4ace650dd7ca2dd4cff9672`, but smoke does not test Android signing or BLE hardware.
- Firmware FlipperHTTP PR [#80](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/80), run [#44919941418](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44919941418): failed on separate branch. Do not aggregate with earlier PR #76-79 failures.

## Release gates — HOLD
1. Reproduce/triage Android combined APK job failure without publishing sensitive logs. Require exact-head green combined build before promotion.
2. Privately compare installed app signing certificate fingerprint to candidate; verify same application ID, monotonic versionCode, data-preserving upgrade path. Signing mismatch: **do not uninstall/overwrite**. Distinct test package only with explicit device-owner approval.
3. BLE AI1 contract: pin firmware and Android API/spec versions, service/characteristic IDs, frame limits, authentication/handshake, reconnection, timeout/error semantics; run source parity and physical device acceptance separately.
4. F7 Momentum native updater: independently attest exact private source SHA, real firmware.dfu suffix CRC, internal SHA-256, encrypted artifact identity, qFlipper recovery; never retry CRC 9-99 image. Successful encrypted fallback [#44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267) is build evidence, not flash clearance.
5. After two consecutive completed failures on the **same** repository+branch+workflow, or repeated pre-provision failure, invoke approved public-safe fallback. If private Actions:read returns 403, record **BLOCKED**; do not infer billing or claim fallback success. Record trigger/fallback IDs and classification.

No candidate promotion, protected merge, device install or flash authorized. The combined release ledger remains owned by integration testing; other workstreams hand off exact commit, artifact, CI and blockers.
