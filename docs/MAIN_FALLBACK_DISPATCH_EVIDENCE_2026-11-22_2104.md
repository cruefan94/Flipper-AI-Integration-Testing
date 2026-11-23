# Public-safe fallback dispatch evidence — 2026-11-22 21:04 ET

Scope: public GitHub Actions metadata only. No private firmware, logs, credentials, binaries, or device diagnostics.

## Important correction to previous handoff

The automatic public-safe monitor has dispatched **new** fallback runs. Do not retain the older claim that no fallback dispatch route exists.

| Public fallback run | Trigger label | Observed status | What the result proves |
| --- | --- | --- | --- |
| [45097676662](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097676662) | private run 44981324511 | completed success | Four private-temporary-source C/Java protocol integration matrix jobs passed; no firmware or Android build job ran |
| [45097671207](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097671207) | private run 44993155895 | in progress | Native encrypted firmware compilation in progress at observation; cannot mark firmware passed |
| [45097674197](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097674197) | private run 44992221452 | pending, zero jobs provisioned | Dispatch exists but execution not established |
| [45097635063](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45097635063) | automatic failover monitor | completed success | Monitor ran; individual fallback job results must be inspected separately |

The older same-workflow Momentum pre-runner failure pair [45067223436](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067223436) and [45067233153](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067233153) remains a qualifying two-failure case. **Do not infer that any newly dispatched fallback maps to that pair without trigger/run metadata establishing the exact association.**

## Release admission remains closed

- Android [PR #139](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/139) exact head `c2fa42eb8efc4e2b21d7bf3ad9feef8b9c3b2492`: combined APK [45097461581](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45097461581) and metadata [45097461449](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45097461449) passed, isolated S25 model hub [45097461573](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45097461573) failed. This is one failure on that workflow/branch, not yet two consecutive failures.
- Momentum [PR #88](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/88) at `cf738f959de58a162a83db873bcbf66c0eac72ba`: native FAP and F7 gates failed. Private log triage required; do not equate with protocol fallback pass.
- Firmware updater: require actual `firmware.dfu` suffix CRC, native `.tgz` hashes, encrypted-only identity, exact source SHA and qFlipper recovery proof. Never retry CRC 9-99 failed updater.
- Android: require signing certificate continuity, package ID/versionCode upgrade check, artifact SHA-256 and physical AI1 BLE acceptance. Do not uninstall existing app.
- Pi/ESP32/voice/radio: optional until separate tested acceptance and dependencies.

## Next actions

1. Recheck the pending/in-progress fallback jobs for final conclusions and map each trigger to its source branch and failed attempts.
2. Diagnose isolated Android model hub failure using public job metadata; feature owner retains source changes.
3. Record exact F7 and APK artifact provenance in private issue #5, only after verification. No candidate promotion or physical installation.
