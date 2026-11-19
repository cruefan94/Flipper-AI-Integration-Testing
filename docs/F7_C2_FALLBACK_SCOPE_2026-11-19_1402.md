# F7 C2 two-failure fallback — scope-corrected evidence (2026-11-19)

PUBLIC-SAFE ONLY. No private firmware source, binaries, logs, credentials, device identifiers or private build output.

## Exact trigger and observed route
- Private Momentum PR #71, branch `test/f7-c2-exact-head-ci-20261119-1138`, SHA `238a54bfc0b1708a827d489cee5d43197871bfb3`.
- Completed failing same-branch runs: [44568518970](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970) and [44568544991](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991).
- Public-safe automatic monitor [44586884817](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44586884817) succeeded, with `watch-and-route` job and route step successful.
- **NEW:** dispatched fallback [44587016728](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728) succeeded, event `workflow_dispatch`, title `fallback | cruefan94/Flipper-AI-Momentum-#44568544991`, at public harness SHA `f1cac80854f26259534c032b2855dd609dd6c58e`.
- Fallback `describe` and `diagnostic` jobs succeeded. `firmware`, `android`, `protocol`, and `contract` jobs **SKIPPED**. Therefore this is an independently successful **public-runner diagnostic fallback**, NOT a native firmware rebuild, not a C2 fix, and not a paired AI1 test. Prior statement that this sequence had no fallback run is superseded.
- Do not infer that private Actions:read access is generally restored solely from successful routing. Confirm the exact monitor coverage summary separately. Do not classify private failure root cause without private step evidence.

## Release gates remain CLOSED
1. Native F7: authoritative C2/linker boundary and full image overlap audit, real `firmware.dfu` suffix CRC on exact candidate, internal updater SHA-256, encrypted-only provenance, and non-destructive qFlipper recovery procedure. NEVER retry failed DFU CRC 9-99 image.
2. Android: CI build at [44580819629](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44580819629) passed for SHA `31875d2709258cdd38ed430d956e1e3894501217` (PR #86), but existing-installed signer certificate compatibility, versionCode monotonicity, safe upgrade and physical BLE pairing are unverified. Do not uninstall or replace owner's existing APK.
3. BLE AI1: pin exact firmware and Android SHA, compare UUIDs, GATT characteristic roles, message framing, auth/consent, reconnect/cancellation, and error behavior. Require cross-repo CI plus device handshake before promotion.
4. Pi: [44584782076](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44584782076) exact qFlipper inventory CI passed on `43312bd3b4acbe2dba2a7d0e496314fb14db7d28`; physical Pi/qFlipper recovery remains untested.
5. Single combined release ledger owner: integration-testing workstream only. Separate feature branches do not imply candidate integration.

## Next private-safe actions
- Privately inspect failing F7 audit job steps and root cause, without copying logs to public.
- Validate private Actions monitoring coverage, and distinguish diagnostic fallback from a successful private firmware compile.
- Request exact SHA + native CRC/hash manifest and Android signer/versionCode evidence from owners; only then create a controlled non-production paired candidate.
- Keep production merge, hardware flash, APK install and cloud deploy prohibited until explicit approval and physical verification.
