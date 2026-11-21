# Release evidence expiry and admission checkpoint — 2026-11-21 14:57 ET

Public-safe metadata only. This document does **not** attest to firmware contents or authorize flashing/installing. No private source, firmware binary, credentials, personal logs or decrypted artifact is stored here.

## Verified GitHub metadata (not device acceptance)

| Evidence | Exact source / run | GitHub status | Limitation |
| --- | --- | --- | --- |
| Historical encrypted F7 candidate | [run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328), source `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | completed success | PR [#22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) head is `32f631c846db67d5f581887c00bbd06599b665c6`, NOT the tested SHA; real firmware.dfu suffix CRC/internal updater SHA unverified |
| Native encrypted fallback | [run 44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267), workflow SHA `f1cac80854f26259534c032b2855dd609dd6c58e` | completed success | Workflow SHA is not necessarily pinned private firmware source SHA; actual F7 attestation missing |
| Android combined debug APK | [run 44931667498](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44931667498), source `f1e7b087630777c4ac138e57e46771a27b2b5bbe` | completed success | Signing cert digest, versionCode/package identity, installed-app upgrade and physical AI1 BLE not verified |
| FlipperHTTP PR [#81](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/81) | [run 44936047367](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44936047367), SHA `869484d9505244715604809421ac473a7f6c51f4` | completed failure | Do not combine with earlier different-branch PR failures; classify from authorized job logs |
| Integration PR [#310](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/310) | [run 44939053053](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44939053053), SHA `97806c84689e2fc3c07beb53aadeb4ce842726bf` | completed success | Public smoke only |

## Time-critical encrypted artifact retention

The four encrypted artifacts from run 43828499328 have GitHub metadata expiry on **2026-11-23 UTC** (IDs 14207991854, 14207847319, 14207827386, 14207736853). Their archive digests are GitHub *archive* digests, **not** the internal firmware.dfu or updater file digests. Never copy decrypted private firmware or encrypted private build artifacts to this public repository. An authorized private custodian may preserve them in an approved private destination with immutable source SHA, archive digest, private internal updater manifest and restricted access. If that cannot be done before expiry, mark evidence unavailable and rebuild only through approved private-safe route. Do not retry failed CRC 9-99 image.

Android debug artifact ID 14717684250, archive digest `sha256:6106ae8dfdb609ab2ec994100c95cff220c47236099d0afa7743650992229413`, expires **2026-11-28T17:45:40Z**. The archive digest does not prove APK signing compatibility. Existing installed Android app must not be replaced/uninstalled; test installation requires explicit owner approval.

## Release admission (fail closed)

1. **F7 private-only**: pin exact firmware source SHA + Momentum base; independently validate actual firmware.dfu suffix CRC from native output, internal .tgz members' SHA-256, updater manifest, F7 target, encrypted-only artifact identity, and a documented qFlipper DFU recovery/restore route. Synthetic fixture CI is not enough.
2. **Android**: record package name, signing certificate SHA-256 (not key), versionCode and versionName for installed app and candidate; prove compatible upgrade path or use separately identified opt-in test package. Preserve app data. Test BLE AI1 protocol/version and reconnect on physical devices before claiming integration.
3. **Cross-component**: pin BLE AI1 command/response/error contract versions and exact Android/F7/ESP32/Pi refs; require passing scoped contract CI and device acceptance. ESP32/Pi remain optional peripherals until their gates pass.
4. **Two-failure routing**: count consecutive completed failures per exact repo+branch+workflow (or repeated no-job provisioning); trigger only approved public-safe fallback. Distinguish code from runner/infrastructure. A private Actions:read 403 means BLOCKED, not a successful fallback. Record original and fallback run IDs.
5. **Ownership**: integration-testing owns combined candidate ledger; do not mutate shared release candidate branch concurrently. No protected merges, device flashes, APK installs, production deployments or claims of device success without approval.

Next: private artifact custodian to confirm retention and native F7 attestation; Android owner to supply non-secret cert/version comparison; firmware owner to triage PR #81 jobs with authorized private logs.