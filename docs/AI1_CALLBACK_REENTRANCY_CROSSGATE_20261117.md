# AI1 notification reentrancy: cross-project release gate (2026-11-17)

Scope: public-safe acceptance criteria only. Do not publish private Momentum source, firmware, binaries, private Actions logs, credentials or personal device traces.

## Evidence and ownership
- Private firmware [PR #43](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/43) adds a **test-only** audit of notification lock ownership. A deliberate expected-failure marker identifies a **possible** callback reentrancy risk; it does not prove a deadlock or a firmware fix. Its provisioned [run 44116871005](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44116871005) failed packaging/syntax jobs (root cause pending authorized logs).
- Android [PR #61](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/61) previously passed host CI [44059283296](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44059283296) for policy revocation. Android [PR #63](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/63) previously passed [44106822997](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44106822997) for offline-only consent. Neither proves device BLE interoperability.
- Public integration [PR #87](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/87) commit 777154e0c6b37cb08997f9fce901044335e5b38f has passing [smoke run 44121257277](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44121257277); documentation smoke is not firmware or APK validation.

## Required cross-component AI1 scenarios
Record exact **firmware commit**, **Android commit**, AI1 protocol/spec version, test command, run ID and outcome for each:
1. Establish authenticated BLE AI1 connection and subscribe to notifications; verify HELLO/ASK/REPLY framing, exact length and request correlation. Distinguish stock Momentum RPC from the custom AI1 channel.
2. Force a disconnect/CCCD disable during a queued notification; verify no stale reply, no use-after-disconnect and no permanently held lock. Repeat with rapid reconnect and subscription toggles.
3. Force Android policy revocation while inference is in flight; verify stale replies are suppressed, including on reconnection. Cloud-disabled mode must never send network inference requests.
4. Exercise notification callbacks that may synchronously re-enter firmware code; capture lock-order assertions or bounded timeouts in private tests. Do **not** mark a deliberate expected-failure as fixed merely because the suite reports success.
5. Confirm recovery after error, timeout and malformed/oversized frames without weakening auth, consent or queue bounds.

## Candidate release gates (fail closed)
- Android: reproducible versionCode/package ID, exact signed APK SHA-256, signing certificate digest matched to installed app for in-place upgrade; otherwise a **separate opt-in test package** only with owner approval. Never uninstall/replace the existing app.
- F7: native encrypted-only updater identity, pinned private source SHA, actual firmware.dfu DfuSe framing and suffix CRC, native .tgz SHA-256 and manifest cross-check; **never reuse CRC 9-99 artifact**. Synthetic fixture success is insufficient.
- Hardware: owner-approved physical BLE and qFlipper restore/recovery verification before any claim of end-to-end success. No flash/install in CI.
- Pi/ESP32/Arduino/radio/voice: remain optional and unpromoted until versioned contract, power/electrical safety and independent CI acceptance exist.

## Mandatory failure routing
Count **completed failures of the same workflow and branch**; after two consecutive failures, or repeated failure before a job is provisioned, use only the approved public-safe fallback route. Preserve failing run IDs, fallback run ID, classified root cause (code vs runner/infrastructure vs access), and corrective action. Private Actions:read 403 or missing dispatch authority = **BLOCKED**, not successful fallback. Never copy private source/binaries/logs to public; never infer billing from missing runners.

Handoff: integration-testing workstream alone owns combined candidate ledger. Firmware/Android feature owners hand off exact passing SHA, dependencies, artifact provenance and blockers; do not mutate their branches or shared candidate concurrently. Canonical private tracker: [Momentum issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5). No protected merges or owner-device actions.
