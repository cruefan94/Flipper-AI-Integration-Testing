# Native fallback artifact presence versus release integrity — 2026-11-23 08:03 ET

## Verified GitHub evidence
- Momentum PR #89 source head: `0cae6e1fb7a81928566306a53a17abb6cac75d96`; full-build failures [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882) (earlier SHA `6a62e9ce9ecc589d2b6024488b4effe1f6425854`) and [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592) (head SHA).
- Approved fallback [45160017502](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45160017502) completed successfully. Its run artifact listing contains **one non-expired artifact**, ID `14811097270`, named `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`. This is evidence of encrypted artifact *presence*, not of contents, source SHA, real DFU suffix CRC, extracted updater checksums, firmware functionality, or physical install.
- Historical native run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) currently lists **zero artifacts**. Do not substitute its historical job result for current exact-artifact inspection.
- Integration PR #427 exact-head public smoke [45170591115](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45170591115) completed successfully.
- Android Worker PR #148 exact-head [45178722399](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45178722399) passed; this is **not** an integrated APK build. Android M7 combined APK run [45106703969](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703969) passed separately at `c8a7c88412c2b2e961eb131502f7bba34b44014b`.

## Private-only artifact admission procedure
1. In an authorized **private** workspace, obtain the encrypted artifact by its immutable run and artifact IDs. Do not download, decrypt, unpack, log, or upload its contents in this public workspace.
2. Record private firmware source SHA, pinned Momentum upstream SHA, workflow/ref, artifact ID, archive SHA-256, each updater member SHA-256, and the actual `firmware.dfu` suffix CRC computed from the binary. Compare with a fresh independent check. A synthetic CRC fixture is not sufficient.
3. Confirm the encrypted-only upload boundary, updater metadata and target F7 compatibility. Record the checksum evidence only in the private tracker, with sanitized pass/fail labels here.
4. Before any owner-approved physical test, retain a known-good official Momentum package, qFlipper/DFU recovery instructions and verified backup. Never retry the prior CRC 9-99 image.
5. For Android, record APK SHA-256, package ID, versionCode, installed-versus-candidate signing certificate fingerprints, and explicit side-by-side test installation consent. Never uninstall/overwrite the existing app to work around signer mismatch.
6. Require actual BLE AI1 service/characteristic and framing parity plus cross-device evidence. Green protocol unit tests alone do not authorize release.

## Release ledger
| Candidate | Build evidence | Exact artifact integrity | Hardware acceptance | Decision |
|---|---|---|---|---|
| F7 native updater | scoped fallback passed; encrypted artifact exists | **NOT VERIFIED** | NOT TESTED | HOLD |
| Standalone FAP | exact-head native acceptance absent | NOT VERIFIED | NOT TESTED | HOLD |
| Android M7 APK | combined build CI passed | signer continuity / APK digest not verified here | BLE AI1 not tested | HOLD |
| Pi / ESP32 / radio | independent isolated tests only | not admitted | not tested | OPTIONAL / HOLD |

Two-consecutive-failure policy remains unchanged: after qualifying same-workflow/branch failures or repeated pre-runner failure, dispatch only the approved public-safe private-firmware fallback. Log trigger IDs, fallback ID, actual executed/skipped jobs, and access/permission blockers. Do not loop reruns or infer billing causes. No merges, flash, APK installs or production deployments authorized.
