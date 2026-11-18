# AI1 release candidate: exact-job verification gate

This is a PUBLIC-SAFE process checklist. Do not publish private firmware sources, binary payloads, device logs, tokens, keys, or private artifact contents here.

## Decision rules

1. Match each acceptance record to repository, full commit SHA, branch, workflow ID, run ID, job ID, completion state and job conclusion. A green workflow with a skipped native compile is **not** a compiled firmware candidate. A successful source audit is **not** an updater artifact.
2. Require actual native F7 compile, strict C2 memory layout safety gate, extracted real firmware.dfu suffix CRC validation, updater manifest and SHA-256 checks, and encrypted-only private artifact provenance. Reject unsafe C2 overlap and quarantine any previously failed DFU CRC updater. Never disable the guard.
3. Require Android APK actual combined-build job, package identity, versionCode progression, and matching installed signer certificate before claiming in-place upgrade safety. A debug artifact cannot be presumed signature-compatible; never uninstall or replace the owner's app automatically.
4. Require a single matched BLE AI1 protocol version, service and characteristic UUIDs, CCCD/notification behavior, HELLO/ASK framing, session revocation on disconnect/lost HCI events, reconnection and error handling. Passing source-only tests cannot substitute for physical BLE handshake.
5. Treat Pi/ESP32/radio/voice as optional peripherals until their own exact-ref acceptance and compatibility evidence is recorded.
6. On two consecutive completed failures of the same workflow and branch, or repeated failure before job provisioning, invoke only the authorized public-safe fallback. Record both source run IDs and the actual fallback dispatch/run/job. If permissions are insufficient, mark BLOCKED, not PASSED. Distinguish runner provisioning from compile/test errors.
7. Before promoting any release candidate, cross-check the canonical private blocker matrix and sole integration-testing ledger owner. Keep production branches, stable APK, and user hardware unchanged.

## Public-safe evidence ledger schema

| Field | Requirement |
| --- | --- |
| Component | F7 / Android / AI1 contract / optional peripheral |
| Source | Repository + exact full SHA + branch |
| CI | Workflow/run/job IDs, completed result, skipped jobs explicitly recorded |
| Artifact | Private provenance reference, hash attestation stored privately; never upload private firmware |
| Compatibility | AI1 version and paired exact source SHAs |
| Gate | PASS / HOLD / BLOCKED with reason |
| Device | Untested until explicit authorized physical verification |

## qFlipper and recovery hold

Before owner-approved flashing, preserve an authorized known-good firmware recovery route, backups, and qFlipper recovery instructions. Do not treat a host build as device recovery validation. Do not retry quarantined CRC-failed updater images.

## Termux / remote diagnostics privacy

Collect only opt-in sanitized health summaries (component version, job status, non-sensitive error category). Redact credentials, Bluetooth addresses, device identifiers, private source paths and personal logs. No automatic upload or public diagnostics.
