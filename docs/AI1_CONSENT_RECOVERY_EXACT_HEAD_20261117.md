# AI1 consent regression recovery: exact-head evidence and release holds (2026-11-17)

Public-safe integration checkpoint. No private source, firmware binary, personal diagnostics, credentials, or device identifiers.

## Verified CI references (not device acceptance)

| Component | PR | Exact head | Completed Actions run | Outcome |
|---|---|---|---|---|
| Android consent fix | [#65](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/65) | `29b0c6c05e46011111a8f2d613926e2831741bc7` | [44161971844](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44161971844) | success |
| Android earlier consent test | [#64](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/64) | `952242ffa5772102428ee660f646e53a68725d59` | [44151562584](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44151562584) | failure |
| Integration triage | [#93](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/93) | `0072d95a5c378d78009158b1ea1d6e894cb3c540` | [44154222406](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44154222406) | success |
| Momentum GATT rollback test | [#45](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/45) | `03e96b8407fb85d2fa9d4420ac871d02c625d742` | [44149416713](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44149416713) | failure |
| Prior encrypted native F7 workflow | [run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | integration head `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | same | success, **not** proof of real DFU image integrity |

## Fail-closed acceptance gates

1. Do not infer Android APK upgrade safety from PR #65's host CI. Compare installed signing certificate against proposed APK, verify package ID/versionCode and backup/restore path; do not uninstall or replace installed app. Test APK requires owner opt-in.
2. Pin matching Android and private Momentum AI1 contract versions; test consent revocation, reconnect, notification subscription, stale-response rejection, callback reentrancy, and physical BLE exchange before candidate promotion.
3. The F7 native updater must have private source SHA, actual DfuSe header and suffix CRC evidence from the **real** `firmware.dfu`, native updater archive SHA-256, encrypted-only artifact provenance, reproducible build metadata and documented qFlipper recovery. The known CRC 9-99 updater must never be retried.
4. The [CRC source gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains synthetic/source-regression evidence only; it cannot clear the native artifact gate.
5. Preserve the two-consecutive-completed-failures rule **per workflow and branch**, or repeated pre-provisioning failure. Invoke only approved public-safe fallback with reference-only metadata; never publish private firmware, binaries, logs or tokens. Where private Actions:read or dispatch permissions fail (including HTTP 403), label **BLOCKED**, preserve failing run IDs and do not invent fallback IDs or attribute failures to billing without evidence.
6. Integration-testing owns the combined candidate ledger; firmware/Android/Pi feature branches hand off exact SHA, passing run, dependencies, and blockers. No protected merges, flashing, installs, or production deployment.

## Next action

Review Android PR #65's consent-fix diff and test coverage against AI1 spec; obtain authorized private firmware job logs for PR #45; obtain native F7 DFU evidence and Android signer comparison before any combined APK/F7 candidate is marked releasable. This document is a coordination checkpoint, not a signed or device-tested artifact.
