# AI1 service / native F7 evidence handoff — 2026-11-17 (public-safe)

Status: **NOT RELEASE-READY**. Documentation-only audit; no firmware source, binary, token, installed-app metadata, private logs or user device data.

## Verified public evidence
- Native encrypted build workflow: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 ; `custom-firmware` job completed successfully, including its named native TGZ verification step. This **does not independently prove** the actual DFU suffix CRC or the private source SHA.
- Exact public harness branch `fix/f7-dfu-crc-preflash-gate-20261116`, head `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`.
- Artifact `14207847319`: encrypted combined candidate only, digest `sha256:1ec260e25953df1c4b637c2e7e3207d91d4318d3f0c69fac73ac974cb772807d`, expires `2026-11-23T08:15:58Z`. This digest belongs to the encrypted artifact ZIP, **not** `firmware.dfu` or native updater `.tgz`. Do not publish/decrypt private payload in public CI.
- Synthetic public CRC gate: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22 ; no real-image acceptance inferred.
- Public Android signing metadata gate: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/61 ; associated smoke run https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44013700712 passed, but this run's step names do **not** prove execution of the new 12 signing regression cases. Verify exact test discovery separately.

## Cross-component integration handoff (no candidate promotion)
- Android service-owned AI1 draft: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/58 . Requires exact-head host/JVM checks, one combined APK build, package/versionCode/certificate and artifact hash evidence, plus explicit foreground/background and consent tests.
- Firmware GATT lifecycle draft: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/40 . Requires private exact-head GATT tests and physical custom-service discovery; stock RPC is **not** AI1.
- AI1 parity gate must compare: UUID and characteristic roles; protocol version/contract digest; HELLO/HELLO_ACK and ASK/ANSWER framing; request-ID replay rejection; per-connection epoch; notify authorization; disconnect cancellation; reconnect; offline-only background cloud policy. Publish only sanitized version/digest and pass/fail metadata.
- Signing: do not replace/uninstall existing Android installation with a differently signed APK. Separate opt-in package only after owner approval and package isolation proof.
- F7: keep failed CRC 9-99 updater permanently quarantined. Private runner must verify actual `firmware.dfu` suffix CRC, native TGZ hash, exact private source commit and recovery manifest. Hold any flash for owner approval.

## Two-failure fallback (mandatory)
- Previously identified same-workflow, same-branch failed runs: `43981306103`, `43981327475` in private Momentum. Classify provisioned test/syntax jobs as code/test failures, not assumed billing.
- Approved fallback coverage: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23 . **BLOCKED** until authorized public-safe dispatch and private Actions:read monitoring are demonstrated. No fallback run ID established. Never copy private firmware, artifacts, logs or credentials to public CI.
- Track every attempt as `repo, workflow_id, branch, commit, run_id, attempt, provisioned, conclusion, failure_class, fallback_run_id, corrective_action`; count consecutive completed failures only for identical workflow+branch.

## Candidate acceptance record (currently unfilled)
| Field | Android unified test APK | Native Momentum F7 updater |
| --- | --- | --- |
| Exact source SHA | UNVERIFIED | UNVERIFIED (private) |
| Matching AI1 contract hash | UNVERIFIED | UNVERIFIED |
| Exact-head CI / test discovery | UNVERIFIED | UNVERIFIED |
| Binary SHA-256 | UNVERIFIED | UNVERIFIED |
| Signing / native DFU CRC | UNVERIFIED | UNVERIFIED |
| Recovery / rollback | UNVERIFIED | UNVERIFIED |
| Hardware acceptance | NOT PERFORMED | NOT PERFORMED |
| Release decision | HOLD | HOLD |

No merges, device flashes, app installs, candidate promotions or secret exposure are authorized by this document.
