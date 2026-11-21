# Termux / GitHub remote diagnostics: public-safe contract (2026-11-21)

**Status: proposed procedure, not implemented on a device.** Applies to Android AI Satellite, Flipper Momentum, Pi gateway, and ESP32 optional components. Never place private firmware, APKs, logs, keys, radio captures, BLE addresses, serial numbers, SSIDs, location, user prompts, or device identifiers in public Actions or issues.

## Allowed transport and scope
1. Termux can locally collect **explicitly approved** diagnostic *status* for a single named component; it does not automatically execute GitHub comments or untrusted remote commands.
2. The only public report fields are: schema_version, component (enum: android, flipper, pi, esp32), test_kind (enum: contract, compile, metadata), outcome (PASS, FAIL, BLOCKED, UNKNOWN), sanitized reason_code (enum: SOURCE_TEST, RUNNER, PERMISSION, ARTIFACT, HARDWARE_PENDING, NOT_RUN), UTC timestamp rounded to hour, and a public GitHub run URL when already public.
3. Raw diagnostic logs stay on the owner's device or approved private workspace. Any private Actions run URL, source SHA, firmware artifact ID, and signing metadata must stay in the private canonical tracker when disclosure is not expressly authorized. Redact first, review manually, then publish only allowlisted fields.
4. Remote diagnostics is **read-only by default**. Never flash Flipper, install APK, change Android permissions, upload a key, or run a script from a GitHub issue/comment. Require explicit owner approval for any local command with side effects.

## Release safety acceptance
- BLE AI1 parity: both endpoints pin the same protocol version and request/response framing; validate disconnect, reconnect, timeout, duplicate message IDs, and malformed input with cross-component tests before claiming hardware integration.
- Android: compare installed and candidate applicationId, signing certificate digest, and monotonically increasing versionCode **privately**. Mismatch => HOLD. Side-by-side test builds require distinct package identity and owner opt-in.
- F7: inspect the **actual** native `firmware.dfu` suffix CRC and inner updater file SHA-256 in a private build; archive hash or synthetic fixtures alone do not count. Never retry known CRC 9-99 image. Preserve qFlipper official Momentum recovery path and verified backup.
- CI fallback: count only consecutive *completed* failures for the same workflow and branch, or repeated pre-job provisioning failures. After two, route through the established approved public-safe private-firmware fallback; record source run IDs, fallback run ID, conclusion, and corrective action. Missing private Actions:read (HTTP 403) => **BLOCKED**, not successful fallback. Distinguish code failures from runner failures without assuming billing.
- Release candidate promotion requires exact source commit, dependencies, native build proof, SHA-256 manifest, passing contract tests, and manual owner approval. No protected merge or hardware installation.

## Sanitized example (synthetic; not a real result)

```json
{"schema_version":1,"component":"android","test_kind":"metadata","outcome":"UNKNOWN","reason_code":"NOT_RUN","utc_hour":"2026-11-21T23:00:00Z"}
```

## Handoff and accountability
Public Integration Testing owns the combined release ledger. Firmware and Android feature workstreams provide exact tested ref, run link, dependencies, and private provenance through the private canonical tracker [Momentum issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5). Do not duplicate edits to feature branches. This document defines a safe interface only; no Termux bridge, BLE integration, firmware package, or APK was built by this change.
