# Fallback attribution and release evidence boundary — 2026-11-18 06:56 ET

Public-safe coordination note. No private firmware source, binaries, logs, tokens, keys or device diagnostics are included.

## Observed evidence
- Momentum full-inventory failures: [44260352832](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260352832) and [44260368327](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260368327), recorded as the same workflow/branch failure pair.
- Public-safe integration fallback [44288673073](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44288673073): latest attempt jobs `describe` and `firmware / custom-firmware` completed successfully; `android`, `diagnostic`, `protocol` and `contract` were skipped.
- **Attribution distinction:** a successful firmware fallback job proves that job executed, not that the original private full-inventory failure was repaired, that all trigger-to-dispatch metadata were validated, or that a flashable firmware image passed safety checks. The private firmware PR #55 describes the general build fallback as permissions-blocked; reconcile this wording against the actual fallback dispatch trigger and source ref before marking a particular workflow/branch's policy obligation fulfilled.
- Private firmware [PR #55](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/55) is an isolated fail-closed C2 metadata diagnostic test; [PR #54](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/54) captures diagnostic metadata only. Neither proves corrected memory occupancy.
- Android combined host build [44214146838](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44214146838) passed at reported SHA `9da29c4f`; the historical Android two-failure fallback has no independently verified Android-compatible dispatch.
- Release ownership: private [Momentum PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), public-safe [integration PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23). Combined candidate ledger belongs solely to integration-testing workstream.

## Required attribution record for every fallback
Record **trigger repo, workflow ID, branch, two consecutive completed failed run IDs and attempts, failure classification, fallback dispatch event/run ID, exact source commit, actual executed jobs and conclusions, permissions/access status**. If any binding is absent, mark **DISPATCH OBSERVED — TRIGGER ATTRIBUTION UNVERIFIED**, not fully resolved. For a missing or 403 private Actions:read credential, mark **BLOCKED**, do not guess billing or retry indefinitely.

## Release acceptance holds
1. **F7 HOLD:** C2 memory overlap must be fixed without bypass; native F7 build at exact candidate SHA must execute (not skip), then verify real extracted `firmware.dfu` suffix CRC, TGZ manifest, SHA-256 and private/encrypted artifact identity. Quarantine CRC 9-99 updater permanently. No qFlipper flash without owner approval and backup/recovery procedure.
2. **Android HOLD:** candidate APK must have reproducible versionCode/package identity, compare installed and candidate signing certificates without exporting private keys, and prove compatible in-place update or use an explicitly approved separate application ID. Never uninstall/replace installed app.
3. **BLE AI1 HOLD:** pin Android/F7 source SHAs and protocol version, validate HELLO/ASK framing, auth, CCCD, reconnect, disconnect, malformed frame and consent revocation via cross-repo tests. Host pass is not physical handshake.
4. **Pi/ESP32/Arduino/radio/voice:** optional until individual compatibility and hardware/safety gates pass; Pi storage backup-first before gateway/recovery reliance.

## Next action
Reconcile the exact trigger attribution for fallback 44288673073 with private Momentum Actions metadata, request owner-side permission configuration if needed, and obtain a C2-safe exact-head native updater build. Do not merge, install, flash, publish private artifacts or relax CI gates.
