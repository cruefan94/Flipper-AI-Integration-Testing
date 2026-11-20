# Exact-artifact evidence gate: reviewer checklist (2026-11-19)

Scope: PUBLIC-SAFE release review only. This checklist never requests firmware source, plaintext binaries, signing keys, private CI logs, phone identifiers, or token values. Do not publish confidential build outputs here. Release ledger ownership stays with the integration-testing workstream; this document is not a release candidate.

## Evidence tuple (required for every proposed promotion)

Record **repository, exact 40-character source SHA, branch/PR, Actions run ID and attempt, completed conclusion, artifact filename, SHA-256 digest, provenance/attestation reference, dependency SHA, and gate outcome**. A green run for another SHA or a synthetic fixture is not transferable. A skipped job is NOT a passing job. Missing/403/private Actions evidence is BLOCKED, not PASS.

## Android upgrade gate

Before offering an opt-in test APK: independently compare the installed application's package ID, signing certificate digest, and versionCode against the candidate; verify candidate versionCode increases and signer continuity. Never collect or publish the owner's installed-app metadata in this public repo. A debug APK build, even with integrity report, does not prove in-place upgrade compatibility. Signing mismatch = HOLD; never uninstall/overwrite the installed app.

## Native F7 updater gate

For the **exact** intended source SHA, require private native F7 compilation and real `firmware.dfu` suffix CRC validation, updater internal file sizes/hashes and full .tgz hash, verified C2 image boundary, compatibility with original Momentum functions, and tested recovery instructions. The prior CRC 9-99 failed updater is forbidden. Only an approved encrypted artifact may cross the public boundary; never upload unencrypted firmware, raw private logs, or secrets. Synthetic CRC fixtures cannot substitute for a native artifact.

## BLE AI1 and peripherals

Require firmware/Android paired version and frame-limit parity, HELLO/ACK, request-ID correlation, malformed-frame rejection, stale callback suppression, reconnect and background transitions, stock Momentum RPC distinction, and AI engine unavailable response. Host tests are necessary but not hardware proof. Pi/ESP32/radio/voice remain separate until exact dependency SHA, isolated tests, transport/power safety and integration acceptance are documented.

## Two-failure route

Count consecutive **completed** failing attempts per workflow + branch; also detect repeated pre-provisioning failure. After two, route through the approved public-safe private-firmware fallback. Record original run IDs, fallback run ID, jobs actually executed versus skipped, failure class (code / runner / permission / unknown), and corrective action. Never retry indefinitely or infer billing. If Actions:read or dispatch permission is unavailable, mark BLOCKED; do not imply a fallback succeeded. An independent diagnostics-only fallback does not clear native firmware gates.

## Current evidence boundaries (as last observed 2026-11-19)

- Android PR #91 SHA `fc7f6196181b5b4bef26851af98cea70a8d48a80`, Actions #44656713440: completed success for source/JVM/security and debug APK build; signer/versionCode upgrade not proven.
- Momentum PR #71 SHA `238a54bfc0b1708a827d489cee5d43197871bfb3`: F7 audit failures #44568518970 and #44568544991; cause unresolved.
- Integration fallback #44587016728: diagnostics passed, native firmware job skipped; cannot clear F7 hold.
- Historical native #43828499328: older build evidence only; not current exact-artifact acceptance.

**Promotion decision: Android test APK HOLD; F7 updater HOLD; paired BLE AI1 HOLD.** No flash/install/merge authorization is implied.
