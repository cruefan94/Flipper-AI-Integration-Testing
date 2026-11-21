# Exact-head FlipperHTTP and release-gate handoff — 2026-11-21 11:00 EST

PUBLIC-SAFE metadata only. No private source, binary, logs, credentials, artifact URLs or personal diagnostics. This is not release approval.

## Verified exact-head evidence
- Firmware PR #80: `fix/flipperhttp-host-labels-20261121-1034`, head `c562e76d6d4ef05d5313d2dd7398f95650ec40fc`. FlipperHTTP read-only probe FAP workflow run [44919941418](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44919941418) **completed failure**. This is the **first verified completed failure** for this branch/workflow; do not combine with PR #79, #78 or #76. Inspect individual job/step evidence privately before labeling code, runner or permissions failure. Native FAP acceptance is not established.
- Android Worker PR #111 head `994400674429cd5d05eec0bb1a6999bff151f95f`: [44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886) **completed success**, Worker contract scope only, not APK signing or BLE hardware.
- Integration PR #298 head `8d36716974bcaea19ba248f3bf1c7697da5072bf`: [44916873901](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44916873901) **completed success**, general smoke only.
- Integration PR #300 head `1b70723f1e8a803a41e29bd9c5c1ad9c2805647c`: [44918786595](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44918786595) **completed success**, general smoke only.
- F7 CRC gate PR #22 head `32f631c846db67d5f581887c00bbd06599b665c6`: synthetic gate [43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939) **completed success**; does **not** prove CRC of a real updater.
- Historical encrypted native run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) must not be substituted for PR #22 exact-head native provenance. Separate encrypted fallback [44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267) completed successfully but does not attest an installable F7 image.

## Two-failure routing
For each exact repository + branch + workflow, count only consecutive **completed failing** attempts; pending/skipped jobs do not constitute a second failed run. A repeated pre-job provisioning failure also triggers routing. After threshold, use only the approved encrypted, private-firmware-safe integration fallback. Missing private Actions:read or HTTP 403 = **BLOCKED**, never green or auto-repaired. Record failing IDs, fallback ID, sanitized result, root-cause classification and corrective action. Do not rerun indefinitely or publish private build material.

## Candidate HOLD / handoff
- **F7 updater .tgz**: require private source SHA, actual `firmware.dfu` suffix CRC, updater internal SHA-256 manifest, encrypted-only artifact identity, C2 and qFlipper recovery verification. Quarantine CRC 9-99 failed image permanently. No flashing.
- **Android APK**: require exact APK SHA-256, package ID, versionCode, signer certificate digest matching installed app for in-place update; otherwise use opt-in separately identified test APK, never uninstall/replace stable installation. BLE AI1 protocol parity and physical testing remain outstanding.
- **ESP32/Pi/radio/voice**: retain independent gates until real protocol and device acceptance evidence. No candidate promotion based on general smoke.

Next: inspect PR #80 failed job steps with authorized private access, verify dedicated PR #300 tests separately from smoke, and request exact-artifact F7 attestation in the private tracker. Integration-testing owns combined candidate ledger; this branch makes no candidate changes.
