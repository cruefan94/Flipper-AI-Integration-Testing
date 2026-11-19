# Integration evidence delta — 2026-11-19 14:57 EST

Public-safe evidence only. This document does not authorize a flash, install, merge, or candidate promotion.

## Exact current Android head
- PR https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/87
- Branch `test/android-service-ownership-gate-20261119-1451`
- Source SHA `ab09373796546d2f0d5a11a164a6f59e168a5874`
- Completed successful Actions https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44602761921
- Job explicitly builds **debug** APK and uploads integrity/provenance; no evidence here of signing-certificate continuity, increasing versionCode, installed-app upgrade or device data preservation. Do not overwrite installed APK.

## Exact private F7 failure/fallback scope
- PR https://github.com/cruefan94/Flipper-AI-Momentum-/pull/71 at `238a54bfc0b1708a827d489cee5d43197871bfb3`
- Failed completed runs: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970 and https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991
- Automatic monitor: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44586884817 (success)
- Dispatched fallback: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728 (success), but **only** `describe` and independent `diagnostic` jobs ran; firmware, Android, protocol and contract jobs skipped.
- Fallback **routing** verified; firmware build, root cause, private Actions-read coverage and BLE AI1 acceptance **not** verified.
- Historic encrypted F7 native build https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 passed at an older pinned revision. It does not establish current firmware.dfu CRC or current C2 layout safety. Never retry failed CRC 9-99 updater.

## Additional current test evidence
- qFlipper read-only recovery preflight PR https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/189 at `a626fc3b9752356e824780cf6a9b73569c1cde7e`; public smoke https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44595649539 passed, **not** physical recovery.
- F7 native updater candidate: HOLD pending real firmware.dfu suffix CRC, internal SHA256, verified C2 boundary, private encrypted-only artifact provenance and physical owner approval.
- Android candidate: HOLD pending signer/package/versionCode continuity, non-destructive upgrade path, BLE AI1 paired contract and owner approval.
- Pi/ESP32/radio/voice remain optional until exact source+test+compatibility gates pass.

## Next evidence actions
1. Privately obtain F7 failing step and native C2 image layout evidence; do not publish private logs or firmware.
2. Independently verify real DFU CRC and internal updater hashes against the exact encrypted candidate, not archive hash alone.
3. Compare Android installed signer and versionCode against candidate using approved private diagnostics; no uninstall or install.
4. Run exact paired firmware/Android AI1 contract tests, then physical owner-authorized handshake.
5. Record exact refs and CI outcomes in private issue #5; do not change the shared release ledger outside its sole owner.
