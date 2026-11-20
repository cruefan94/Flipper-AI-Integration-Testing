# MAIN integration evidence — 2026-11-19 19:57 ET

Public-safe coordination only. No private source, binary, credential, hardware diagnostics or firmware log.

## New exact-head Android regression (not a second failure)

- Android PR [#90](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/90), branch `fix/android-null-connect-session-guard-20261119-1947`, head `f169931bb84c6728868e072179943933172ad618`.
- Completed failing [Actions #44648762154](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44648762154), job `Host regressions + one full-feature Android APK`, failing step `One-time Android source, JVM and security regressions`. Runner provisioned; assertion/root cause not established from job summary. One completed failure on this branch/workflow, not two.
- PR [#89](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/89) earlier passed [#44632497713](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44632497713) at `c6e83950428476afe7d8c29c0f60400ac19b7b03`; this does **not** pass PR #90.
- Android owner: isolate failing assertion privately, repair on Android-owned branch, obtain exact-head successful source/JVM/security and APK build evidence. Do not promote any APK while signer, package identity and versionCode continuity remain unverified.

## F7 and fallback

- Momentum [PR #71](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/71), `238a54bfc0b1708a827d489cee5d43197871bfb3`, two completed failed runs [#44568518970](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970) and [#44568544991](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991).
- Prior [public-safe fallback #44587016728](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728) is diagnostics-only; native firmware skipped. Do not interpret it as a repair.
- Historical native [#43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed successfully (`custom-firmware` job), but does not prove current native updater CRC, internal hashes, C2 flash boundary, encrypted-only artifact identity or hardware safety.
- **Never retry the known CRC 9-99 updater**. Native F7 .tgz remains HOLD until exact artifact manifest, firmware.dfu suffix CRC, internal SHA-256, C2 bounds, recovery guide and approved private-safe verification.
- For each workflow+branch, count consecutive completed failures separately; on two failures or repeated pre-runner failure invoke approved public-safe fallback without exposing private firmware. If private Actions read/dispatch is inaccessible, mark BLOCKED; do not silently substitute a green public smoke job.

## Independent gates

- Public integration [PR #200](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/200), head `b53d1ab843b525e8620758b2e13b5c5fab23f972`, [smoke CI #44642051170](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44642051170) passed; documentation smoke is not a combined release candidate.
- Pi/qFlipper exact [#44635265115](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44635265115) passed; device recovery still unverified.
- Public-safe radio redirect [#44645466007](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44645466007) smoke passed; no radio device integration promotion.
- BLE AI1: require versioned HELLO/ACK, stock Momentum RPC vs custom AI1 separation, malformed frame rejection, reconnect/stale callback, background continuity and paired hardware handshake against pinned Android/F7 SHAs.
- Termux/GitHub diagnostics: read-only, redacted, opt-in; no token or private logs in public artifacts.

## Release ledger (no candidate promotion)

| Deliverable | Status | Required next evidence |
| --- | --- | --- |
| Android test APK | HOLD | PR #90 exact-head passing regressions and build; signer/package/versionCode compatible with installed app; user approval before install |
| Native F7 Momentum updater .tgz | HOLD | Private exact-source native build, genuine DFU CRC, internal SHA-256, C2 bounds, encrypted-only artifact, qFlipper recovery |
| Paired BLE AI1 | HOLD | Cross-component contract and physical handshake |
| Pi/ESP32/radio/voice | ISOLATED | Hardware and integration acceptance |

Phase 1 private [release blockers PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and [fallback coverage PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23) remain governing gates. No protected merge, flash, install or release promotion authorized.
