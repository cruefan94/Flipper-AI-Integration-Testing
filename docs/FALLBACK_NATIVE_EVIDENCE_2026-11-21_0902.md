# Public-safe fallback native build evidence — 2026-11-21 09:02 ET

This file records **metadata only**. No private firmware, binary, log, token, signing key, personal diagnostics, or encrypted payload is reproduced.

## Confirmed fallback
- Public integration monitor: [44906990301](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44906990301), completed success, public workflow head `f1cac80854f26259534c032b2855dd609dd6c58e`.
- Fallback: [44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267), completed success, title references private Momentum failure `44866117174`; public workflow head `f1cac80854f26259534c032b2855dd609dd6c58e`.
- Fallback job `firmware / custom-firmware`: completed success. GitHub job steps report private source checkout, AI overlay, native Momentum compilation, updater verification, encryption, and encrypted-only upload. Other diagnostic/contract/protocol/Android jobs were skipped. **Passing steps are not an independent examination of the real DFU CRC or on-device validation.**
- GitHub artifact metadata: ID `14709001142`, name `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`, size `12649800` bytes, expiration `2026-11-28T13:13:56Z`. Keep private; do not publish, decrypt publicly, flash, or distribute.
- The underlying private source commit SHA, actual internal updater SHA-256, genuine `firmware.dfu` suffix CRC result, C2 bounds, and physical qFlipper recovery proof are **not established by the public metadata**. Request a private-only signed/provenance attestation before any release-candidate admission.
- This successful fallback changes the prior blanket claim that **no fallback was dispatched** for FlipperHTTP PR #76; do not extend the claim to ESP32-S3 PR #75 or other branches without their own exact run IDs. Fallback compilation success does not mean FlipperHTTP FAP feature or ESP32-S3 hardware passed.

## Other exact-head evidence
- [F7 historical run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed success at `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`, but [PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) currently heads `32f631c846db67d5f581887c00bbd06599b665c6`: not an exact-head match.
- [F7 artifact identity audit PR #293](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/293) exact-head `6284643923c0` public smoke [44906709651](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44906709651) passed; documentation smoke is not real updater CRC proof.
- [Android Worker PR #111](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/111) exact-head `994400674429` Worker contract [44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886) passed; no APK upgrade signature or physical AI1 evidence.
- [Android GATT PR #105](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/105) exact-head `084a7221aa7d` combined APK [44863378694](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44863378694) passed; existing installed APK signature mismatch remains a no-replace hold.
- [Momentum FlipperHTTP PR #79](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/79) is an isolated follow-up; do not count its CI with PR #76 for a same-branch two-failure decision.
- [Momentum PR #75](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/75) failed same-workflow/same-branch runs [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063) and [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160). No confirmed S3-specific successful fallback here; if Actions:read is 403, mark private diagnostics BLOCKED, not automatically resolved.

## Release admission and next action
Both unified deliverables remain HOLD: Android test APK requires stable signing certificate fingerprint, package ID/versionCode, opt-in side-by-side or signature-compatible upgrade, and physical AI1; F7 native `.tgz` requires private exact source SHA, genuine `firmware.dfu` CRC and per-file hashes, C2 safety, Momentum compatibility, encrypted-only handling, and qFlipper recovery. The previously failed CRC 9-99 image is prohibited. ESP32/Pi/radio/voice are optional until their own tested interfaces and safety gates pass.

Private tracker: [Momentum issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5). No production merges, owner-device flashing, installation or cloud deployment authorized.
