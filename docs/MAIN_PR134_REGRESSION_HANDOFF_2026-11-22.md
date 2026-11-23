# MAIN integration triage — 2026-11-22 19:01 America/Toronto

Public-safe handoff only. No private source, firmware binaries, credentials, logs, personal device identifiers or signing material.

## Exact heads and jobs

| Workstream | Ref | Evidence | Classification |
|---|---|---|---|
| Android general AI PR #134 | `ef3efd36166faf66597c27a39a84d1dee1612988` | combined APK [45085770237](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45085770237), metadata [45085770234](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45085770234) | FAIL — source/preflight regression before APK build |
| Android BLE PR #133 | `e05e44c3091df4a39ecea2e3141f8e92270b8a01` | combined [45085599744](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45085599744), metadata [45085599681](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45085599681) | PASS for host CI only; distinct branch |
| Momentum FAP PR #88 | `cf738f959de58a162a83db873bcbf66c0eac72ba` | [45067246324](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246324) | FAIL; native job root cause unclassified |
| Momentum F7 PR #88 | same head | [45067246380](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45067246380) | FAIL; no accepted updater |
| Release evidence validator PR #388 | `0a06488c0ea45207557be2f39109f3f5908bc1c2` | [45081211782](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45081211782), [45081211757](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45081211757) | PASS, synthetic offline checks only |
| Historical native encrypted F7 | pinned older ref, not current PR #88 | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | Native compile job PASS; physical flash and exact-artifact integrity not proven |

## Actionable regression handoff

Android PR #134 combined job `137403909285` failed in **One-time Android source, JVM and security regressions**; metadata job `137403909343` failed in **Source and preflight regressions**. Both provisioned runners and completed setup, so classify as **test/source failure**, not billing or runner provisioning. The combined log reports one assertion expecting the literal `sendMessage(prompt)` in an Android source inspection. The AI feature owner must inspect whether the new implementation changed a valid call site or whether the assertion became stale; do not weaken the assertion without demonstrating equivalent prompt dispatch and safety. Both APK build steps were skipped. Do not claim PR #134 produced a testable APK.

PR #133's green CI belongs to a separate BLE branch and cannot certify PR #134. Keep branch ownership separate; no direct Android source edit from integration coordination.

## Release admission and fallback

- **BLE AI1:** require identical version, command names, encoding, framing, errors, timeout/reconnect and cancellation behavior across C and Java at pinned tested refs. Host tests do not substitute for a device session.
- **Android:** record artifact SHA-256, package ID, versionCode, installed vs candidate signing certificate fingerprint in a **private** evidence route. Existing signing mismatch: never uninstall or replace stable app; isolated test APK only after owner opt-in.
- **F7:** require real `firmware.dfu` suffix CRC validation, updater internal checksum, full archive SHA-256, pinned private source SHA, encrypted-only artifact provenance and qFlipper recovery instructions. The CRC 9-99 updater must never be retried. Do not publish firmware artifacts or metadata revealing private contents.
- **Fallback:** count consecutive completed failures by **same workflow and branch**, not five different failed jobs. Earlier qualifying FAP runs [45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405) remain on record; historical encrypted firmware fallback [45039819048](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039819048) is not proof of a standalone FAP build. For any new qualifying pair use only approved private-safe fallback, record its actual dispatch ID and result; permission 403 means BLOCKED, never successful.
- **Pi/ESP32/radio/voice:** keep optional until independently accepted and compatible; do not silently include in either candidate.

## Next step

Android feature owner to fix or justify the PR #134 source assertion and rerun targeted host CI once; integration owner to verify exact-head outcome and update the sole combined release ledger. Private firmware owner to diagnose FAP failure using authorized private-only evidence. No candidate promotion, production merge, installation or flash.
