# MAIN integration: Android upgrade validator CI scope (2026-11-23 16:04 ET)

## Exact evidence
- Draft PR #451: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/451
- Proposed validator commit: 59fb0cca6abe680bfbb34e3f5932032197e107a8
- GitHub Actions PR smoke run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45254897274 — completed success, per commit-associated workflow query.
- This is **public runner and contract smoke** evidence, NOT proof that the eight new validator regressions were invoked. Inspect the job steps/logs for explicit test invocation before claiming test coverage.

## Mandatory promotion blockers
1. Compare installed Android package name, signing certificate SHA-256 and versionCode against exact test APK; never replace or uninstall existing app on mismatch. Protect user data. Opt-in side-by-side test requires distinct applicationId and owner approval.
2. Record APK SHA-256, exact source commit, build workflow and tested artifact ID; prove BLE AI1 handshake/ASK/ANSWER/CCCD behavior on physical Flipper/phone before device acceptance.
3. F7: private source SHA, encrypted archive identity, decrypted updater/member SHA-256 and **actual firmware.dfu suffix CRC** must be verified privately. Synthetic CRC and green host build do not substitute. Never retry CRC 9-99 updater.
4. PR #90 exact-head native-protocol failures: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45219142235 and https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45219142350. Two-failure policy triggered. Fallback is BLOCKED until an authorized dispatch and corresponding run ID are observed. Distinguish permission/runner failures from code failures; no automatic billing attribution.
5. Preserve encrypted artifact 14811097270 via approved private-only route before 2026-11-30 11:03 UTC. Its public Actions archive digest identifies only the encrypted delivery, not the updater contents.

## Ownership and safety
Integration-testing is sole owner of combined release ledger. No feature source edits, shared release candidate branch changes, private source/binary/log/token disclosure, production merges, device flashing, APK installation or cloud deployment in this branch. qFlipper recovery and stock Momentum restore must be documented and reviewed before any future owner-approved device trial.
