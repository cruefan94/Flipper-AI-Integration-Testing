# Android/F7 release evidence chain — public-safe checklist (2026-11-20)

**Status: HOLD.** This document is a reviewer protocol, not a release manifest, verified APK, or firmware build. No production merge, flash, install, signing-key upload, private firmware transfer, or public diagnostic collection is authorized.

## 1. Immutable identity (private canonical ledger only)
For each proposed candidate, pin the repository, full 40-character source SHA, workflow name, completed run URL, job result, exact artifact filename, SHA-256 of actual bytes, build variant, and provenance. A green workflow is not equivalent to an accepted artifact. Record which candidate consumes each source commit and which other commits it depends on. Do not substitute an older successful run for a newer head.

## 2. Android data-preserving upgrade
Privately collect *only* package identifier, versionCode and signing-certificate SHA-256 for the currently installed app and candidate APK using approved Android package tooling (e.g. apksigner verify --print-certs on an APK from an authorized source, and aapt dump badging on candidate). Never publish the user's installed-app inventory, device identifiers, APK, keystore, certificate private key, passwords, or diagnostic logs. Compare package identifiers exactly; signing certificate continuity must be cryptographically checked, not inferred from debug/release labels; candidate versionCode must increase. If any input is unknown or differs, mark **BLOCKED** and preserve the installed app and its data. A separate test package is opt-in only with explicit owner approval. Record evidence privately without exposing the full device report.

## 3. Native F7 updater, not synthetic fixtures
Private route only: record pinned Momentum upstream SHA and private overlay SHA, actual native compile result, exact .tgz artifact SHA-256, validated archive members and hashes, and genuine firmware.dfu suffix CRC computed over actual bytes. Verify C2 flash boundary and recovery procedure against that exact image. A synthetic DFU CRC regression passing is not real-image evidence. Historical run 43828499328 (source 4cbdf863f5d7062ff34271bbd0687b843a6fbfc8) completed native build/packaging steps; it does **not** attest a current candidate. The previously failed CRC 9-99 artifact must never be retried.

## 4. AI1 parity and hardware gate
Record Android and F7 AI1 protocol versions, service/characteristic roles, encoding/length limits, HELLO/ACK and ASK/response correlation, cancellation on disconnect/device switch, and explicit consent revocation. Run host contract tests on exact pinned commits. Keep paired-device handshake, reconnect/background BLE and consent checks **UNVERIFIED** until physical owner-approved testing. ESP32/Pi modules stay optional until their hardware-specific gates pass.

## 5. Two-failure fallback and CI classification
Count consecutive *completed* failures separately by repository + workflow + branch. Also route repeated pre-run provisioning failures to the approved public-safe integration fallback. Capture failing run IDs, first failing step, whether a runner was provisioned, fallback run ID, outcome and next action. Classify code failure vs runner/infrastructure; do not guess billing. A private Actions:read HTTP 403 is **BLOCKED**, not success. The public workspace may receive only synthetic fixtures, allowlisted non-sensitive statuses, or encrypted-only outputs under the approved route; no private source, firmware binary, tokens, keys, personal logs or unencrypted archives. Never disable tests or retry indefinitely.

## 6. Release decision
Promotion requires exact-head passing build and tests, verified artifact hashes, compatible Android upgrade path, real F7 CRC and recovery checks, API parity, explicit owner approval for any device action, and private tracker acknowledgement. Otherwise **HOLD**. The integration-testing workstream alone owns the combined candidate ledger; feature workstreams provide exact refs and test evidence without concurrently editing that ledger.

References: private Momentum PR #23; integration-testing PR #23; private tracker Momentum issue #5; integration-testing PR #22 and #230.
