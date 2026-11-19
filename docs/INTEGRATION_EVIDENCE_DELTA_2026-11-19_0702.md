# Public-safe integration evidence delta — 2026-11-19 07:02 America/Toronto

This is a **read-only handoff**, not an authorization to build, install, flash, merge or distribute. It contains no private firmware code, logs, artifacts, credentials or personal diagnostics. All links are to GitHub records; private links require authorized access.

## Exact source and CI observations

| Area | Exact source/branch | CI evidence | Interpretation |
| --- | --- | --- | --- |
| Firmware C2 boundary audit | [private PR #67](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/67), `33e0142983bd998f4e3eb3dd3693494096f1acdf` | No exact-head run in latest eight repository runs | Audit is not release authorization; verified C2 boundary and native linker/flash layout still required |
| Firmware native update safety | [private PR #66](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/66), `604e89a17a3ba485bbf347b68d0bf2326e28426b` | [44481566067](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481566067), [44481581444](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481581444), [44481593032](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481593032): three completed failures on same branch/workflow | **HOLD**; do not disable offset/overlap guard |
| Approved fallback | [public-safe run 44491711278](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44491711278) | Firmware job passed; protocol, Android, contract, diagnostic jobs skipped | Fallback execution occurred, but it does **not** clear the native flash safety failure |
| Android stale GATT callback checks | [PR #83](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/83), `13cbc076357c767e1eeaae6b937c4b42833f9cf5` | [44517913454](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44517913454): success | Host CI only; installed app signing compatibility, real BLE handshake and on-device upgrade remain unverified |
| Paired release evidence policy | [PR #172](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/172), `a3d42c7a17274a284e8bbfad3097376e37685e78` | [44511605042](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44511605042) and [44511605146](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44511605146): success | Synthetic evidence-policy tests only, not actual firmware CRC or APK signature verification |
| Historical native CRC candidate | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328), `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | Workflow success | Historical result, not current exact-source release approval; [PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains draft |

## Paired-candidate promotion gate (all must pass)

1. **F7:** exact private source SHA and approved Momentum base; verified C2/radio flash boundary and linker segment placement; non-skipped native compile; real `firmware.dfu` embedded suffix CRC; SHA-256 of the actual native updater `.tgz`; encrypted-only delivery identity; recovery/qFlipper procedure. Never retry the updater previously rejected with DFU CRC 9-99.
2. **Android:** exact APK source SHA, package ID, versionCode and signing certificate comparison with installed app; signature-compatible update or separately identified opt-in test APK. Do not uninstall or overwrite the existing app.
3. **BLE AI1:** matching documented API/spec version, characteristic UUIDs, frame and authentication rules, reconnect/CCCD behavior and real paired-device handshake. Stock Momentum RPC status is not evidence of AI1 readiness.
4. **Cross-system:** same-source provenance and test/run IDs in the single integration-owned ledger; optional Pi/ESP32 components remain separate until compatibility gates pass.
5. **Fallback:** two completed failures on the same workflow and branch, or repeated pre-run provisioning failure, trigger approved public-safe private-firmware fallback. Log original and fallback IDs; classify code versus infrastructure; mark private Actions:read/dispatch 403 as **BLOCKED**, never infer billing.

## Next action

Obtain private exact-head F7 C2 boundary proof and native layout evidence without modifying the feature-owner branch. Independently collect Android signing/versionCode evidence and BLE AI1 paired contract evidence. Only the integration-testing workstream may update the shared combined release-candidate ledger. No promotion, flash or install until all required gates pass.
