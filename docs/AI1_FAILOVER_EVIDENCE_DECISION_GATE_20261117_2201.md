# AI1 release evidence and failover decision gate — 2026-11-17 22:01 ET

Public-safe coordination record; no firmware source, binary, credentials, personal diagnostics, or private build logs.

## Pinned evidence
- Private release blockers: Momentum draft PR #23 (head 3cdf6c940dacd5b800a9bac205b2b8aed4366ebe).
- Private Actions failover coverage: Integration Testing PR #23 (head 2cd0f201a740bf1d99ecd70c3f96c4588e6fcab3).
- F7 CRC source gate: Integration Testing PR #22 (head 32f631c846db67d5f581887c00bbd06599b665c6).
- Historical native encrypted F7 run 43828499328: completed/success; this is host workflow evidence, **not** physical validation.
- Native F7 run 44180961225: completed/success, attempt 2, public integration commit fc6c9e462295ff2fdfae9a481580965d5c408e55. Exact private source SHA and private artifact hashes must be confirmed through authorized private records.
- Automatic CI failover monitor run 44223466630: completed/success, job watch-and-route and its decision-policy test passed. This does **not** prove any specific failed Android workflow was dispatched or repaired.

## Two-failure decision table (fail closed)
| Condition | Required action |
| --- | --- |
| Two completed failures on identical repo + workflow ID + branch | Route once via an approved public-safe fallback appropriate for that workstream; log original run IDs, attempt IDs, fallback run ID, outcome |
| Repeated failure before any Actions job provisioned | Same fallback trigger; distinguish queue/provisioning from code failure |
| Different branch/workflow, pending attempt, or single completed failure | Do not aggregate as a failure pair |
| No authorized dispatch or required private Actions:read | Mark BLOCKED; never claim fallback executed |
| Public runner succeeds but no private provenance | Keep native firmware release on HOLD |
| Android host tests fail before APK compilation | Classify host/source regression; no installable APK evidence |

Android combined-build failures previously reported: workflow 420703090, runs 44181012277 and 44204936456 on the same branch. Recheck live run/attempt and branch identity before dispatch. Do not route Android to a firmware-only fallback.

## Candidate promotion checks
1. **AI1 parity:** record Android and firmware commit SHAs, UUIDs, framing delimiter, revision, MTU/fragmentation rules, consent state, reconnect/replay behavior and matching executable tests. No device-level pass without a real authenticated BLE handshake.
2. **Android:** verify signed APK SHA-256, package ID, versionCode monotonicity, installed-app signer match, and non-destructive upgrade path. If signer mismatch, hold; never uninstall the owner's app.
3. **F7:** verify actual firmware.dfu suffix CRC and header, updater archive members and SHA-256, exact private source SHA, encrypted-only artifact access and qFlipper recovery instructions. Never reuse quarantined CRC 9-99 image.
4. **Optional Pi/ESP32/radio:** retain as separate component until exact tested source, interface dependencies and physical acceptance exist.
5. **Ledger ownership:** integration-testing alone promotes a coordinated candidate; no shared candidate branch mutation by parallel tasks.

Next: collect sanitized run-level Android fallback evidence and job assertion; verify exact private F7 source/artifact attestations; maintain both deliverables on HOLD pending gates.
