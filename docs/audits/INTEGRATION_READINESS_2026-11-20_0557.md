# Unified Flipper AI release gate — evidence snapshot (2026-11-20 05:57 America/Toronto)

PUBLIC-SAFE metadata only. This file is a historical audit snapshot, **not** an approved release manifest, passing firmware claim, or permission to install/flash. The integration-testing owner alone maintains the combined candidate ledger.

## Source / CI evidence

| Component | Exact PR / SHA | CI evidence | Gate |
| --- | --- | --- | --- |
| Android AI1 device-switch revocation | [PR 96](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/96) / `ff51c6e7108c3efea028fd10f47a00e614061f20` | [44722699068](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44722699068), completed success | APK compile passed; installed-app signer/versionCode **unverified** |
| Android upgrade evidence validator | [PR 223](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/223) / `441faaee9e68b184732765797b2d67cca8f52f77` | [44715509389](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44715509389), success | Synthetic gate only; no owner's installed certificate checked |
| Release evidence / AI1 parity validator | [PR 222](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/222) / `49868b98ae10d87cef1a2df006bd7475a3b84771` | [44706808548](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44706808548), success | Schema parity only, paired transport unverified |
| Private Momentum S3 prototype | [PR 72](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/72) / `94253300aa7a1379e5eeb3f11156f78f8b0d0b96` | S3 [44672970355](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970355), F7 [44672970526](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44672970526): failed | Source/compile blocker; **no native updater acceptance** |
| Historical encrypted F7 native candidate | `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328), completed success | Older source only; **not** current DFU CRC/hash proof |

## Required gates before promotion

1. **Android:** obtain independently extracted installed APK package name, signing-certificate SHA-256 and versionCode using a consented private diagnostic route. Compare with the exact candidate's signer, package and higher versionCode. Never publish device identifiers, keystore material, fingerprints tied to personal diagnostics or installed APK. Do not uninstall/replace the stable app; a separate test APK requires explicit opt-in.
2. **F7:** use an approved private build route only; verify exact source commit, native compile, *actual* `firmware.dfu` suffix CRC, full updater member checksums, encrypted-only provenance, C2 boundary and qFlipper restore path. The known failed CRC 9-99 updater is prohibited. Synthetic fixture success is insufficient.
3. **BLE AI1:** verify identical protocol version and command/error semantics across exact Android and firmware refs, revocation on manual disconnect/device switch, stale-session rejection, reconnect lifecycle and paired physical handshake. Host-only checks cannot satisfy hardware gate.
4. **Fallback:** count consecutive completed failures by the **same workflow and branch**. After two, or repeated pre-runner failures, route through approved PUBLIC-SAFE integration fallback; record source failing IDs, fallback ID, result and corrective action. Public route must never receive private firmware source, binaries, credentials or private logs. If private Actions:read returns 403, mark **BLOCKED**; don't interpret diagnostic-only success as native compilation.
5. **Pi/ESP32/radio/voice:** remain separately gated until exact commit, passing CI, dependencies, electrical/transport safety and relevant hardware acceptance are documented. No automatic promotion.

## Current disposition

Android integrated test APK: **HOLD** (signing continuity, device approval). Native F7 Momentum updater `.tgz`: **HOLD** (current native build, genuine DFU CRC, hashes, C2 and recovery). No production merge, flash, install or physical verification is authorized by this document.

Next: hand off the Android PR96 passing ref to the ledger owner; privately collect signing continuity; investigate the first failing private F7 command and confirm the two-failure fallback record; then execute paired AI1 contract/hardware acceptance. Keep public issue comments restricted to non-sensitive status.
