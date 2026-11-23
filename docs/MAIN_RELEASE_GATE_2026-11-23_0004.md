# MAIN integration release evidence gate — 2026-11-23 00:04 EST

Public-safe coordination only. No firmware source, binaries, credentials, private logs, or device diagnostics are stored here. This document is NOT a release approval.

## Exact source/CI evidence observed
- Android PR #143: `c8a7c88412c2b2e961eb131502f7bba34b44014b`; combined APK run 45106703969, M7 preview 45106703986, metadata 45106703984: completed/success. Signature continuity, APK artifact SHA-256, on-device AI1 BLE and M7 encrypted-memory behavior remain UNVERIFIED.
- Android PR #144: `494829cf4c25df01ae24f130f4da75f24340c894`; Worker contract run 45113647300 completed/success. Does not establish combined APK or production Worker deployment.
- Momentum PR #88: `cf738f959de58a162a83db873bcbf66c0eac72ba`; FAP 45067246324, F7 45067246380, protocol 45067246313/45067246351/45067246394 completed/failure. Distinct workflows are not a two-attempt pair. Private diagnostics required for classification.
- Momentum same-workflow full-build attempts 45067223436 and 45067233153 completed/failure; previously recorded pre-runner. Mandatory approved fallback applies. Historical fallback firmware jobs 45097671207 and 45097674197 passed; protocol fallback 45097676662 passed four jobs. Skipped jobs do not establish integrated success.
- Integration PR #403: `cd9f179aeb36567961b0607060163540afa0ba71`; smoke 45109136102 completed/success.
- Integration Pi PR #404 smoke 45110920081 success; ESP32 PR #405 smoke 45111558279 success. Both remain peripheral-only and unpromoted.
- Historical encrypted F7 CRC workflow 43828499328 completed/success. Exact real `firmware.dfu` suffix CRC, updater archive checksum manifest, encrypted-only artifact identity and current source SHA are not independently evidenced here. PR #22 head `32f631c846db67d5f581887c00bbd06599b665c6` is still open. Never reuse CRC 9-99 failed image.

## Required fail-closed admission checklist
1. Record exact source SHA, branch, workflow name, completed run ID, artifact ID, artifact SHA-256, and provenance for each component. Reject missing, mismatched or skipped evidence.
2. AI1 BLE: compare C and Java request/response framing, version, lengths, error codes, reconnect behavior and negative vectors against a pinned contract; require exact-head cross-language pass and physical-device approval separately.
3. Android: extract signer certificate SHA-256 from the candidate and currently installed package using owner-controlled read-only checks. If mismatched, BLOCK replacement; do not uninstall or clear app data. Isolated test installation requires explicit owner approval.
4. Native F7: verify actual generated `firmware.dfu` suffix CRC and archive contents/checksums, F7 target identity, encrypted-only private artifact handling, native compile, and reproducible qFlipper recovery/backup instructions. Never infer real CRC from synthetic fixtures or green job summary.
5. On same workflow+branch after two completed failures, or repeated failure before runner provision, use only approved public-safe private-firmware fallback. Capture both failing run IDs and fallback run IDs. Mark 403/missing private Actions read as BLOCKED, not success; do not blame billing without evidence.
6. Pi/ESP32/radio/voice: do not promote until dependency, power/safety, transport compatibility and targeted tests are proven; retain optional separate builds.
7. Do not merge protected branches, deploy Worker, flash Flipper, install APK or distribute production artifacts without explicit owner approval and physical tests.

## Handoff status
Android unified test APK: HOLD. Momentum F7 .tgz: HOLD. Standalone FAP: BLOCKED. No combined release candidate promoted by this audit. Next: privately classify PR #88 job failures and correlate fallback provenance; obtain signer fingerprints and real F7 CRC/artifact hashes; keep the sole candidate ledger in integration-testing.
