# Android combined APK: exact-head recovery evidence (2026-11-21)

PUBLIC-SAFE metadata only. This is a handoff, **not** a release candidate admission or a claim of on-device installation.

## Correction to earlier HOLD based on PR #112
- PR #112, `fix/android-navtest-package-identity-20261121`, SHA `ad0d47c94760db3819c668c0a748a527320cd42f`: combined APK run [44926545670](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44926545670) **failed**.
- New stacked PR [#113](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/113), `test/android-navtest-suffix-guard-20261121`, SHA `f1e7b087630777c4ac138e57e46771a27b2b5bbe`: combined APK run [44931667498](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44931667498) **completed successfully**, including job `Host regressions + one full-feature Android APK`.
- The new green head is a **different branch and commit**; do not mark PR #112's failed run retroactively green.
- The green run exposes artifact ID `14717684250`, name `FlipperAI-Android_20261121_run44931667498-a1_shaf1e7b087_ALLFEATURES-DEBUG-UNTESTED`, archive size 24,496,533 bytes, expiry 2026-11-28T17:45:40Z. Metadata does not prove installed package identity, APK signing certificate, versionCode, or phone data preservation.
- Treat as **debug / untested**; do not install over the owner's existing signed app. A separate package/applicationId for side-by-side testing requires explicit owner approval.

## Evidence needed before controlled candidate handoff
1. Pin the exact SHA above and all stacked dependencies; verify the combined APK artifact's internal file hashes, package/applicationId, versionName, versionCode, minSdk, signing certificate SHA-256 and signing lineage privately.
2. Compare the existing installed app's signing certificate and package ID through owner-approved, read-only device inspection. If signatures differ for the same package, **block replacement**; never uninstall or clear data to force an upgrade.
3. Run cross-component BLE AI1 contract/version tests with explicit handshake/authentication, RPC-vs-AI1 separation, reconnect and background recovery. Host success is not physical BLE acceptance.
4. Do not promote firmware: native encrypted fallback [44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267) has artifact ID `14709001142` expiring 2026-11-28T13:13:56Z, but still needs private exact-source provenance, real `firmware.dfu` suffix CRC, internal updater SHA-256, C2 audit, and qFlipper recovery proof. Never retry CRC 9-99 image.
5. Retain two-failure counting by exact repository + branch + workflow. Private Actions:read 403 is BLOCKED, not success; only approved encrypted-only fallback may access private firmware. No source/binary/logs/credentials in public.

This file is independent of the combined release-candidate ledger (integration-testing workstream ownership). No source branches, protected branches, release candidates, devices or signing keys were changed.
