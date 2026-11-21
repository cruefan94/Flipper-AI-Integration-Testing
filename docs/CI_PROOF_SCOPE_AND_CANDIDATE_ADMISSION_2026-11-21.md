# CI evidence scope and candidate admission — 2026-11-21 05:57 ET

Public-safe integration-only handoff. This document contains no private firmware source, binaries, logs, tokens, device identifiers or signing fingerprints. It is **not** a release authorization.

## Exact commit workflow evidence checked

| Component | Exact head | Workflow run | Observed result | Scope |
| --- | --- | --- | --- | --- |
| Integration audit PR #284 | `d458d5dd54f72a2a2fe850b195894acb7e501a70` | [44891885845](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44891885845) | completed/success | Public runner and contract smoke only |
| Android Worker PR #111 | `994400674429cd5d05eec0bb1a6999bff151f95f` | [44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886) | completed/success | Worker contract workflow, **not** APK/signing or cloud deployment |
| Radio CI PR #283 | `b5a457a19972d8e4303ffebf2d4f877c89fe6906` | [44889686597](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44889686597) | completed/success | Generic public smoke; dedicated nine-test provenance suite **not established** |
| Pi health PR #285 | `d32d0f704abfca97dcc65f24d056947afff87779` | [44893583411](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44893583411) | completed/success | Generic smoke, **not** Pi sampler acceptance |

A successful workflow with the wrong test scope MUST NOT satisfy the feature-specific gate. Confirm job steps and exact test counts separately before promotion.

## Release admission checklist (fail closed)

1. **Android**: exact source SHA and passing APK build, artifact SHA-256, applicationId, signing certificate match with installed version (or explicitly separate applicationId), monotonic versionCode, BLE AI1 version/UUID/characteristic and authentication contract parity, consent and offline/online fallback checks, optional physical acceptance. Never uninstall/replace the installed app to bypass signing mismatch.
2. **F7 native updater**: exact private source SHA attested privately, upstream Momentum pin and F7 target, native `.tgz` manifest and internal file hashes, extracted actual `firmware.dfu` suffix CRC verified (not synthetic fixture), memory/C2 boundaries, recovery/qFlipper path and separate owner flash approval. Never retry failed CRC 9-99 image. Keep all private artifacts encrypted and private.
3. **BLE AI1**: compare protocol version, service and characteristic UUIDs, message framing, sequence/replay handling, authorization, reconnect, negative responses and maximum payload behavior against **both** tested exact commits. Stock Momentum RPC is not AI1.
4. **Peripheral and radio**: Pi, ESP32, FlipperHTTP, Arduino and receive-only radio prototypes remain separate until feature-specific CI and board-safe physical evidence; FlipperHTTP insecure TLS fallback prohibits sending secrets.
5. **Two-failure policy**: count consecutive completed failures for the **same workflow and branch**; repeated pre-job provisioning failure also triggers fallback. Distinguish runner failure from code failure; do not assume billing. Approved public-safe private-firmware fallback only; if private Actions:read returns 403, label **BLOCKED** and request permission configuration. Record failed run IDs, fallback dispatch ID or BLOCKED status and corrective step. Do not publish private logs.

## Outstanding blockers / owner boundaries

- Momentum S3 #75: [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063), [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160). Prior public-safe diagnostics do not prove native acceptance; private Actions:read 403 reported BLOCKED.
- FlipperHTTP #76: [44866082379](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866082379), [44866117174](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866117174). Child PR #77 is a different branch; do not combine failure counts. Root cause needs authorized job evidence.
- Historical native [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) custom-firmware job completed successfully, including native package verification step; this alone does not expose or attest the **exact current** F7 `.tgz` CRC, SHA and provenance. Obtain encrypted-only private attestation.
- No Android candidate or F7 updater is promoted by this document. No production merge, flash, APK install, or cloud deployment.

## Next handoff

Integration-testing ledger owner: privately verify artifact attestations and Android signing continuity, obtain authorized S3/FlipperHTTP job failure classification, verify dedicated radio/Pi test suites, then admit only exact passing refs into a controlled non-production unified candidate. Record private evidence in [canonical tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).
