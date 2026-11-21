# Exact-head CI classification and release handoff — 2026-11-21 04:55 ET

Public-safe metadata only. No firmware, binaries, tokens, private logs, user identifiers, or diagnostic payloads.

## Newly checked exact-head evidence

| Workstream | PR and head | Actions run | Observed | Acceptance |
|---|---|---|---|---|
| Android Worker malformed upstream | [Android #111](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/111), `994400674429cd5d05eec0bb1a6999bff151f95f` | [44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886) | completed success, Cloudflare Worker contract tests | Worker contract only; NOT deployed; NOT APK signing or BLE acceptance |
| Radio provenance exact-head | [Lab #283](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/283), `b5a457a19972d8e4303ffebf2d4f877c89fe6906` | [44889686597](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44889686597) | completed success, public runner smoke; checked jobs show smoke/fallback regression, not the dedicated nine-test radio job | Dedicated radio provenance nine-test job **NOT VERIFIED**; do not promote |
| FlipperHTTP guard | [Momentum #77](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/77), `5c5684bf5fa906d48f844482658256f7f91ee50a` | [44890581029](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44890581029) | completed failure; app isolation, runner availability, C guard and checkout jobs all failed; FAP compile skipped | Failure cause **UNCLASSIFIED** without authorized job logs; no native FAP proof |
| Termux read-only preflight | [Lab #282](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/282), `fe8e4cd6632a579677a4b4559192feae83203e0b` | [44887136380](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44887136380) | completed success, public smoke | Documentation only, no live remote bridge |

## Two-failure routing and triage

* Prior same-branch FlipperHTTP #76 completed failures: [44866082379](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866082379) and [44866117174](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866117174). Mandatory public-safe fallback threshold previously reached.
* Prior S3 #75 pair: [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063) and [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160).
* New FlipperHTTP #77 run #44890581029 is a **different branch**; do not count it as the second #77 failure. Multiple jobs failing in one run do not equal two attempts. A repeated failure before provisioning may independently qualify, but require run/runner evidence.
* Private Actions:read previously returned HTTP 403. Until approved access and route are demonstrated, fallback monitoring/dispatch remains **BLOCKED**. Do not assume billing or code defect from job summaries. Do not dispatch private source or artifacts into public workflows.
* For each qualifying pair: preserve branch, workflow, run IDs, job provisioning status, failure category (code/runner/permissions/unknown), authorized public-safe fallback run ID or BLOCKED reason, and corrective action. Never loop reruns or relax gates.

## Unified candidate gates (unchanged)

* **Android APK HOLD**: exact APK hash, source SHA, versionCode, package identity, stable signing fingerprint compatibility and device-owner-approved BLE AI1 physical acceptance. Never replace/uninstall the installed app on a signing mismatch.
* **F7 Momentum updater HOLD**: exact private source SHA; native F7 artifact identity; extracted actual `firmware.dfu` suffix CRC and SHA-256; C2 boundary; encrypted-only transfer; manifest and qFlipper recovery proof. Historic CRC 9-99 updater must NEVER be retried. Synthetic verifier green is not actual firmware validation.
* **ESP32, Pi, radio, voice HOLD** pending independent protocol, safety and dependency acceptance. Do not combine into release candidates without exact passing source/CI provenance.
* Preserve [private Phase 1 blockers](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23), [safe failover PR](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23), and [DFU gate PR](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22). Integration Testing owns the combined candidate ledger; this audit does not mutate it.

## Next checks

1. Read authorized private job steps/logs for #44890581029 and distinguish runner/checkout failures from C guard code errors.
2. Verify whether the dedicated radio nine-test workflow on #283 ran at the exact head; do not equate generic smoke with its acceptance.
3. Collect private exact-artifact F7 attestation and Android signing evidence before promotion.
4. Report only verified status to [private MAIN tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).
