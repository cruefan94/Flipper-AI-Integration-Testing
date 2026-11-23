# MAIN integration: pre-provisioned runner failure and release hold (2026-11-22 20:00 ET)

Public-safe metadata-only handoff. No private firmware source, binary, logs, secrets, credentials, or personal diagnostics.

## Confirmed runner classification
Private Momentum branch `fix/flipperhttp-nul-frame-reject-20261122-1534`, workflow `Build Flipper AI - custom Momentum + full executable inventory`:
- [45067223436](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067223436), head `1192e95cb9f8ebe18f2af2b0159d29abe292c920`, completed failure.
- [45067233153](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067233153), head `cf738f959de58a162a83db873bcbf66c0eac72ba`, completed failure.
- Both have two initial failed jobs with `runner_id=0`, no runner name, and zero job steps; dependent build jobs were skipped. **Classification: runner/job provisioning failure, not a proven source regression or billing diagnosis.** These are consecutive failures on the same workflow and branch (different heads), and independently meet the repeated-before-provisioning fallback trigger.
- [45067246324](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246324), standalone FAP: its only job also failed with `runner_id=0`, zero steps. No actual FAP compile evidence.

## Required public-safe fallback
Route the qualifying pair through the existing approved **private-safe** integration-testing workflow; only use an encrypted private build path, never publish firmware/source/binary or raw private logs. Historical successful encrypted native firmware fallback [45039819048](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039819048) is **not** an execution for this new failure pair. New fallback run ID: **NOT DISPATCHED / UNVERIFIED**. If private Actions:read or dispatch permissions return 403, mark **BLOCKED**, not PASS. Do not retry failed private jobs indefinitely.

## Android correction and release gates
Android [PR #134](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/134) latest head `8b8fcea613299df5af2c967fb1e56ce843e3182e`: combined APK [45088808433](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45088808433), metadata [45088808474](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45088808474), and standalone test APK [45088808450](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45088808450) all completed success. This supersedes the earlier failing PR #134 head; **not proof of signer continuity or physical AI1 BLE**.

## Release admission: HOLD
- APK: capture exact artifact SHA-256, versionCode, installed and candidate signer fingerprints, opt-in side-by-side package identity, and physical BLE AI1 protocol parity. Do not replace/uninstall existing app.
- Native F7 updater: inspect exact real `firmware.dfu` suffix CRC, native updater manifest/checksums, encrypted-only artifact identity, source SHA and documented qFlipper recovery. **Never retry the failed CRC 9-99 updater.**
- FAP: require a provisioned runner, completed native compilation and artifact hash; firmware fallback alone does not satisfy FAP gate.
- Pi/ESP32/radio: remain optional until individually tested and dependencies confirmed.

Historical F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed success; no exact current firmware image verification or physical flash established. Phase 1 policy references: private Momentum PR #23 and public-safe integration PR #23. Integration-testing alone owns combined candidate ledger; no candidate branch mutation, production merge, flash or install.
