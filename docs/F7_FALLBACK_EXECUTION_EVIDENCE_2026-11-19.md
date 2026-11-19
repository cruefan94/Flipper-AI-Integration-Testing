# F7 two-failure fallback execution: evidence correction (2026-11-19 04:55 ET)

PUBLIC-SAFE METADATA ONLY. This record contains no firmware source, binaries, credentials, private logs or personal diagnostics.

## Exact trigger and execution
- Original private firmware workflow: `Build Flipper AI - custom Momentum + full executable inventory`, branch `test/stock-momentum-flash-offset-guard-20261119-0240`.
- Three completed failures: [44481566067](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481566067), [44481581444](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481581444), [44481593032](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481593032). Head SHA of third: `604e89a17a3ba485bbf347b68d0bf2326e28426b`.
- **New evidence supersedes earlier BLOCKED/no-dispatch reports:** public-safe [fallback run 44491711278](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44491711278) completed **successfully** on public harness main `f1cac80854f26259534c032b2855dd609dd6c58e`.
- In fallback, `firmware / custom-firmware` job `135448765692` completed successfully. Steps explicitly include private credential checks, pinned Momentum source, private overlay tests, native compile, native updater TGZ verification, encryption, and encrypted-only artifact upload. Other jobs (protocol, Android, contract, diagnostic) were **skipped**.
- [Fallback monitor 44491610574](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44491610574) completed successfully.

## Interpretation and remaining release gates
- **Fallback executed**, so blanket statements that it was not dispatched are now stale. Its successful encrypted native compile does **not** prove that the original ESP32-S2 flash-plan safety failure was corrected; the fallback used a different path. Do not disable or bypass the original guard.
- Do not infer genuine DFU suffix CRC proof, source SHA parity with the failed branch, decrypted artifact hash, firmware flash safety, qFlipper recovery success, or device compatibility merely from green job labels. Obtain authorized private evidence and exact source SHA, updater SHA-256, real firmware.dfu suffix CRC verification, encrypted artifact identity, and recovery instructions before promotion.
- Android [PR 82](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/82), SHA `e6424c6cfe7e0898e87ec7bc49a4be5e4118e990`, [APK CI 44499811765](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44499811765) passed. Signing continuity, versionCode, install-free upgrade compatibility and paired AI1 BLE acceptance remain unverified.
- [Momentum PR 66](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/66) remains held; [F7 CRC PR 22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) is a separate gate.
- Never retry the historical DFU CRC 9-99 updater; no protected merge, physical flash, APK install, production release or public private-firmware artifact.

## Next action
Authorized private read-only inspection of fallback job's source revision and verification manifest; compare to current candidate and PR #23 handoff. Preserve the two-failure trigger for each exact workflow/branch, and record fallback IDs rather than declaring BLOCKED when a successful run exists.
