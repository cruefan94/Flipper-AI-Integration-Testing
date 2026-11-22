# AI1 v0.8 dual-transport integration admission — 2026-11-22 (public-safe)

Status: **HOLD**. This is a test/coordination specification, not a validated firmware image, FAP, Android APK, or device result.

## Exact source handoff
- Private Momentum draft [#84](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/84): v0.8 external FAP, Android via stock Momentum RPC as primary; FlipperHTTP ESP32-S2 via independent USART 13/14 at 115200 as optional explicitly selected diagnostics. Local parser tests are reported in its PR, but **no native v0.8 FAP build artifact** is attested.
- Android [#118](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/118): bounded Java RPC codec; no verified BLE transport AppStart/AppData peer, inference dispatch or physical connection.
- Private release blockers [Momentum #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23); failover permissions [Integration #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23); real DFU CRC gate [Integration #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22).
- This note deliberately does not publish private source, artifacts, logs, identities, tokens, or board-specific diagnostics.

## Acceptance matrix (each row requires exact immutable commit, run ID, outcome and evidence)
| Test ID | Stimulus | Expected fail-closed behavior | Required evidence |
| --- | --- | --- | --- |
| AI1-01 | Android BLE connect then authenticated stock RPC AppStart | App starts once, no legacy UART substitute | Android/Flipper protocol trace **sanitized privately** and exact-head tests |
| AI1-02 | Fragmented 180-byte bounded AI1 AppData, multi-fragment BLE | Reassembly and request ID matching; no truncation or cross-request mixing | Host codec and native FAP tests plus physical trace |
| AI1-03 | Disconnect during response, then reconnect | No stale response or duplicate inference; bounded retry | Device test with request IDs redacted |
| AI1-04 | Missing AppStart, malformed length, invalid UTF-8 | Reject and recover without leaking payload | Both host parsers tested |
| HTTP-01 | Select FlipperHTTP board ping/status/version | USART 13/14 only; strict whole-line PONG, timeout and error recovery | Native FAP build and device smoke test |
| HTTP-02 | Android AI1 active while board absent or unresponsive | Android primary remains independent; board diagnostic timeout cannot block AI1 | Device test |
| HTTP-03 | FlipperHTTP AI prompt/token transfer attempt | **DENY** until TLS certificate verification, authenticated endpoint and consent are proven | Negative test, code review |
| UART-01 | Switch between legacy LPUART 15/16 and FlipperHTTP USART 13/14 | Correct peripheral ownership, bounded receive and release | Native build and device test |
| APK-01 | Compare installed app and proposed APK | Reject incompatible signer or unsafe versionCode; preserve installed data | Signed APK fingerprints, package IDs and version metadata in private ledger |
| F7-01 | Inspect actual encrypted native updater | Verify genuine firmware.dfu suffix CRC, internal SHA-256, source provenance and encrypted-only identity | Private exact-artifact attestation; **never** use failed CRC 9-99 updater |

## CI fallback and candidate admission
For each **same workflow + branch**, record consecutive completed failures (run ID, attempt, head SHA, job/step evidence). Two consecutive failures, or repeated pre-provisioning failure, trigger only the approved public-safe fallback route. An inaccessible private Actions:read endpoint (HTTP 403) is **BLOCKED**, not a green fallback. Keep infrastructure failures separate from source/test failures; do not infer billing. Public workflows must not receive private firmware source, binaries, tokens, private logs or raw diagnostics.

Only the integration-testing owner promotes exact passing source refs into the non-production candidate ledger. Require native FAP build, signed APK compatibility, physical AI1 and FlipperHTTP acceptance, genuine F7 updater attestation, and qFlipper backup/recovery before requesting owner authorization. No production merge, automatic install or flash.
