# CI attempt identity and fallback evidence — public-safe gate

This document defines the decision procedure for the unified Flipper AI test coordinator. It contains **no private source, binaries, logs, credentials or device identifiers**.

## Attempt grouping

Use the tuple `(repository, workflow_id or workflow path, head branch)` as the failure counter key. Sort completed attempts by `run_started_at` and `run_attempt`, recording the immutable run ID and head SHA. A workflow's multiple jobs in one run count as **one attempt**, not multiple failures. Distinct workflow names on the same commit do **not** count as consecutive attempts of the same workflow.

Only `status=completed` and `conclusion=failure` increment a consecutive-failure counter. A completed success resets that key. Pending, queued, cancelled, skipped, neutral, timed-out, action-required or inaccessible history must be classified explicitly, not silently counted as a code failure. Classify provisioned job failures as code/test or runner/infrastructure from job evidence; never infer billing without evidence.

A repeated identical failure before any job is provisioned is the separate pre-runner trigger. Record the attempts and reason; do not infer this trigger merely from different workflows failing together.

## Trigger and dispatch

After **two consecutive completed failures for the same key**, or a verified repeated pre-runner failure, invoke **only** the approved public-safe private-firmware fallback route in this repository. The public workflow may consume sanitized result metadata only; never upload private firmware, binaries, keys, tokens, raw private logs, private source or personal diagnostics.

Record triggering run IDs, workflow path, branch, exact SHAs, job-provisioning evidence, failure class, fallback workflow/run ID and conclusion. If private Actions history returns 403 or the required Actions:read token is absent, mark **BLOCKED: permissions** and record that no dispatch was confirmed. A green monitor does not mean fallback ran. Never weaken tests, endlessly rerun, or merge automatically.

## Release acceptance remains separate

* Native F7: verify actual `firmware.dfu` embedded suffix CRC and native updater `.tgz` SHA-256 **inside the approved private build boundary**; the encrypted delivery ZIP digest is not a substitute. Quarantine the known CRC 9-99 failure.
* Android: compare signing certificate digest, application ID and versionCode against installed stable app before considering an update; signing mismatch means separate opt-in test APK only, no replacement/uninstall.
* AI1: pin firmware and Android source SHAs, protocol version, contract hash, matching test vectors and BLE hardware acceptance before promotion.
* Pi/ESP32/radio: keep separately gated until compatible, safe, reproducible builds exist.

## Handoff schema

`repo | workflow_id | branch | head_sha | run_id | run_attempt | completed_at | conclusion | job_provisioned | failure_class | fallback_status | fallback_run_id | source_provenance | artifact_digest | blockers`

Unknown values must be `UNVERIFIED`, not guessed. Integration-testing owns the combined candidate ledger; this document does not promote any candidate.
