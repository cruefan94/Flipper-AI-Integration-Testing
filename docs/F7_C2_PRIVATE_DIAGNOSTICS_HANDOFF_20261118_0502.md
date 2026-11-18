# F7 C2 overlap: private diagnostic acceptance and integration handoff (2026-11-18 05:02 ET)

## Source-of-truth and non-overlap
- Firmware diagnostics are owned by private Momentum PR #54 (`audit/f7-c2-size-diagnostics-20261118-0439`, SHA `76b9f8a1e25452257a6da1db35f8247c5036d36d`). Do not duplicate source modifications here.
- Fail-closed regression: private Momentum PR #53, run 44267860731, SHA 165191bfee8dad357362eebd2627cb1453521c39: integrated updater packaging rejected C2 memory overlap. This is a **source/image-layout safety failure**, not established runner/billing failure.
- Same-workflow same-branch failures 44260352832 (ea14b03a) and 44260368327 (edc4a8fc) triggered the two-failure policy. Approved public-safe fallback dispatch remains **BLOCKED/unverified**; no fallback run ID. Public monitor green is not proof of private Actions:read access or fallback dispatch.
- Older native compile/publish 44238360282 (1e7a4120) cannot attest the latest head. Green workflow 44252265247 (ce8b2258) skipped native compilation.

## Private diagnostic evidence required from firmware owner
1. Record exact firmware source SHA, Momentum upstream pin, F7 target, compiler/linker versions, actual flash footprint and reserved C2 boundary in **private** issue #5 or encrypted private artifacts.
2. Preserve fail-closed overflow rejection. A proposed fix must reduce or correctly relocate code/data without changing reserved C2 limits or suppressing the check.
3. On corrected SHA, show a non-skipped native F7 build and updater packaging job with successful completion, then verify **real** `firmware.dfu` suffix signature, full-file CRC and extracted updater file hashes; record private SHA-256 manifest.
4. Confirm encrypted-only artifact transfer identity and retention; do not upload private firmware, binaries, keys, internal logs or personal diagnostics to this public repository.
5. Keep original DFU CRC 9-99 artifact quarantined. qFlipper/SD recovery is a separate hardware acceptance step and requires owner approval before any flash.

## Android and AI1 candidate gate
- Android combined build 44214146838 passed at SHA 9da29c4fce8e82c981823c9aee0296671abfb335, but DEBUG-UNTESTED is not a safe replacement for the installed app.
- Require candidate package ID, versionCode increment, and exact installed/candidate signing certificate match; on mismatch, preserve existing install and data and use a separately named opt-in test app only.
- Pin both sides of BLE AI1 protocol/version and verify UUIDs, characteristics, CCCD subscription, disconnect cleanup, request IDs, response framing, timeout/reconnect and consent fail-closed behavior. No physical handshake is verified.
- Pi/ESP32/Arduino/radio/voice stay optional until independently tested compatibility and safety gates pass.

## Release ledger decision
**F7: HOLD** (C2 overlap); **Android APK: HOLD** (signer/device acceptance); **AI1: HOLD** (cross-component parity/hardware); **fallback: BLOCKED** (no authorized verified dispatch). This public document contains references and status only, no private payloads.
