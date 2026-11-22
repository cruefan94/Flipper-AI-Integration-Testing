# Cross-project admission audit — 2026-11-22 07:00 ET

Public-safe evidence only. This document contains no firmware source, binaries, credentials, personal device data or private runner logs. No release promotion is authorized.

## Newest observed heads and CI
- Android PR #126, `fix/cloud-test-assertion-redaction-20261122-0648`, SHA `7872d21649533624c3366e567953bd75355e60fd`. Combined APK workflow [45019175629](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45019175629) **failed**: runner setup and Android SDK succeeded; the **One-time Android source, JVM and security regressions** step failed. APK compilation, provenance and artifact upload were **skipped**. Metadata workflow [45019175610](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45019175610) **passed**. Do not promote or claim an APK from this head.
- Android PR #124, SHA `f1188d21e7ee01219a36698fdb270f69df1c407d`, prior combined workflow [45004495801](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45004495801) passed; this does not validate PR #126 or the installed-app signing certificate.
- Momentum PR #86, `fix/flipper-ai-v08-fap-ci-trigger-20261122`, SHA `5eed030b206e15983624107bd794ae792138d5f2`. Same workflow and branch failed twice: [45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405). Latest job had **zero steps**; classify as pre-step/provisioning-unknown, NOT a proven C compilation error or billing failure.
- The two-failure threshold is met. The approved public-safe fallback route must be invoked when authorized, but **current-branch fallback dispatch and native FAP verification are not evidenced**. Previous diagnostic-only public fallback success is not equivalent to native compilation. Private Actions:read HTTP 403, if still present, means **BLOCKED**.
- Historical encrypted F7 run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328), source SHA `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`, completed successfully. Its successful job is **not** proof of current native `firmware.dfu` suffix CRC, exact `.tgz` checksums, encrypted-only identity, qFlipper recovery or hardware flashing success. PR #22 exact head `32f631c846db67d5f581887c00bbd06599b665c6` is separate from that historical workflow source SHA.

## Required fail-closed handoffs
1. Android owner: fix PR #126 host regression on its own branch; provide passing exact-head combined APK run, artifact SHA-256, application ID, versionCode, signer fingerprint and side-by-side install safety. Never uninstall or replace the existing app to bypass signing mismatch.
2. Momentum owner: obtain private job/runner diagnostics for PR #86 and route the qualifying failure pair through the approved PUBLIC-SAFE fallback without exposing private firmware or logs. Return exact native FAP compile evidence; do not retry indefinitely.
3. Integration owner: accept only exact SHA/CI/provenance handoffs into the single controlled release ledger. Check AI1 stock RPC AppStart/AppData contract and BLE reconnect on physical hardware before device-ready claims.
4. F7 owner: inspect a newly built exact candidate privately for actual DFU suffix CRC, native updater archive manifest/hashes, encrypted-only artifact identity and tested recovery instructions. **Never retry CRC 9-99 artifact**.
5. Pi/ESP32/radio/voice remain optional and outside the unified candidates until their separate acceptance gates pass.

No protected merges, firmware flash, Android install, production deploy or candidate promotion authorized by this audit.
