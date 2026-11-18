# AI1 host contract green does not imply native F7 release readiness — 2026-11-18 12:03 ET

PUBLIC-SAFE metadata only. Do not attach private firmware, DFU, TGZ, source, credentials, signer information or raw personal diagnostics.

## Exact source and job evidence
- Firmware PR #60: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/60
- Firmware SHA: `08b144215890d7a6c4d61b79182debb8f0ac7fab`
- Host AI1 reconnect/RX contract run https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44349821320: `host-session-contract` **success** (job 134962084968).
- Firmware source overlay run https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44349821186: workflow success; inspect per-job proof before treating it as compilation.
- Native F7 candidate run https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44349821257: quick source checks **success** (job 134962084539), full native F7 compile/strict update inspection **skipped** (job 134962088016), native TGZ draft publisher **skipped** (job 134962088930). Overall green is NOT a native build.
- Android PR #74 https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/74 SHA `8eca68fd72acbea116b0cb2b84e0f2815e4d7940`; combined APK workflow https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44340028689 succeeded, but signer/versionCode upgrade compatibility and device AI1 handshake are not proven.
- Integration prior PR #134 https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/134 at `03f7ae0bc8641b7d31fcebbebbb5b744ee9ccabb` passed smoke https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44343314572.
- Historical encrypted firmware run https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 custom-firmware job succeeded; NOT evidence for current source revision. Historical PR #22 remains open at `32f631c846db67d5f581887c00bbd06599b665c6`.

## Fail-closed acceptance
1. Require same exact firmware SHA for non-skipped native F7 compile and TGZ packaging; check C2 memory boundary, real `firmware.dfu` suffix CRC, complete updater checksums, artifact provenance and encrypted-only public transfer. Never retry quarantined CRC 9-99 updater. Keep flashing owner-gated.
2. Require Android APK signer fingerprint match with installed app, package ID, monotonically compatible versionCode, and non-destructive update path. Otherwise hold; no replacement/uninstall.
3. Compare BLE AI1 UUID, characteristic permissions, CCCD authenticated subscription policy, RX frame bounds, reconnect revocation, sequence and version negotiation at paired firmware/Android SHAs. Host tests are not a physical BLE handshake.
4. Maintain two consecutive completed failures per identical workflow+branch (or repeated pre-job failure) as fallback trigger. Attribute trigger run IDs, dispatch ID, source SHA and executed fallback job; do not infer infrastructure/billing cause. Missing private Actions:read or dispatch permission = BLOCKED, not success.
5. qFlipper recovery, Termux remote diagnostics, Pi/ESP32 and radio remain separate opt-in acceptance gates. Never publish private diagnostics or promote an unverified peripheral.
6. Only integration-testing workstream owns the combined release ledger; avoid concurrent edits to shared candidate branch.

## Next owner handoffs
Firmware owner: produce native C2-safe updater evidence at exact PR SHA, without disabling safety checks. Android owner: provide non-sensitive signing compatibility result and matching AI1 contract evidence. Integration owner: pair commits, reconcile fallback attribution, and promote only after all gates pass. No production merge, hardware flash or install authorized.
