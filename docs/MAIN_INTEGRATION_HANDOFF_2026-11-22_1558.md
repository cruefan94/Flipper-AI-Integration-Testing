# MAIN integration handoff — 2026-11-22 15:58 America/Toronto

Public-safe release admission checkpoint. This is evidence bookkeeping, **not** a release authorization. Do not place private firmware source, updater archives, tokens, signing material, private runner logs, or device diagnostics in this repository.

## Exact-head checks (2026-11-22)
| Component | PR / tested head | Workflow / outcome | Interpretation |
|---|---|---|---|
| Android | [PR #132](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/132), `e054c9f4cc7689da87a92e2f32edeb18015fedaa` | [combined APK #45068584230](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45068584230) SUCCESS; [metadata #45068584221](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45068584221) SUCCESS | Host regressions, debug APK build, integrity report and artifact upload passed. No signing continuity or BLE device proof. |
| Momentum | [PR #88](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/88), `cf738f959de58a162a83db873bcbf66c0eac72ba` | [FAP #45067246324](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246324) FAILURE; [F7 #45067246380](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246380) FAILURE | F7 quick source-check job failed; native compile jobs were **skipped**, not compiled and failed. FAP job failed; classify from authorized private logs before asserting source vs runner. Other exact-head protocol workflows also failed. |
| Public integration | [PR #379](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/379), `ccbc990fddefa93f2e5676a39eef805e48ecbed6` | [smoke #45063619960](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45063619960) SUCCESS | Public-safe Termux documentation smoke passed; not device testing. |
| Pi/ESP32 lab | [PR #381](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/381), `fb739fbcf98289d9ad8afb71ef27de45e64a67d1` | [smoke #45066293710](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45066293710) SUCCESS | Offline power-budget test only; no integrated peripheral release admission. |
| Historical encrypted F7 | Pinned historical candidate | [native #43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) SUCCESS | Native build job passed, **not** evidence of current PR #88 updater integrity or physical flash safety. |

## Required release-admission evidence (fail closed)

- **FAP:** exact head SHA, Momentum target/API version, native `.fap` compile job, artifact SHA-256, and independent BLE AI1 protocol vectors. A failed or skipped job is not a passing compile.
- **Android:** exact head SHA, versionName/versionCode/applicationId, APK SHA-256, certificate SHA-256, and whether installed signer matches. A debug-signed APK must not replace the owner's installed app. Side-by-side install requires separate package ID and explicit opt-in.
- **F7 updater:** exact private source SHA and pinned Momentum SHA kept in private tracker; real `firmware.dfu` suffix CRC check, all updater-internal checksums, manifest and archive SHA-256, encrypted-only delivery identity, and verified qFlipper recovery instructions. **Never retry CRC 9-99 artifact.**
- **BLE AI1:** prove firmware and Android agree on UUIDs, framing, length limits, auth/permissions, reconnect behavior, error codes and protocol version. Passing host tests is not physical pairing evidence.
- **Pi/ESP32/radio/voice:** remain optional until separately verified dependencies and safety gates pass.

## Two-failure fallback decision record

Earlier same-workflow/branch FAP failures [#45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [#45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405) met the mandatory threshold. Approved encrypted native firmware fallback [#45039819048](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039819048) passed its firmware job; separate protocol fallback [#45039820581](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039820581) passed. **Neither proves the standalone FAP builds.** For new PR #88, determine whether a second consecutive failure on the *same branch/workflow* exists before marking a new threshold. If monitoring returns HTTP 403 or lacks private Actions:read, mark monitoring BLOCKED and request private configuration. Do not conflate a green monitor with a dispatched fallback.

## Next owner handoff

1. Privately inspect PR #88 exact-head failed FAP and F7 source-check job steps/logs; classify source, runner or permission failures and record sanitized failure category only.
2. Compare Android #132 signer/version metadata against the installed app without changing it.
3. Run the public-safe AI1 cross-language vectors at exact pinned refs, then attach passing run IDs.
4. Require genuine F7 artifact CRC/hash and recovery evidence in private issue [#5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5) before any non-production candidate promotion.

No production merge, hardware flash, APK install, or source disclosure authorized.
