# F7 updater admission and qFlipper recovery checklist (public-safe)

Status: **HOLD — procedure only; not a flash authorization**. Updated 2026-11-22. No private firmware, device identifiers, diagnostics, tokens, or binary content belong in this document.

## Exact-artifact admission (all required)

- [ ] Pin private source commit, Momentum upstream revision, F7 target, toolchain, build workflow/run/job and artifact identity in the **private** release ledger. Public tracker may show only non-sensitive gate statuses.
- [ ] Confirm native F7 updater build actually executed (not skipped or diagnostic-only); host synthetic DFU fixture tests do not qualify.
- [ ] Validate actual `firmware.dfu` suffix CRC from the candidate's bytes and archive integrity; compare internal updater manifest checksums to extracted contents; preserve SHA-256 of the **exact** candidate in private evidence.
- [ ] Verify encrypted-only public handoff policy: never upload firmware source, firmware binaries, updater archives, keys, raw logs or device diagnostics to the public integration repository.
- [ ] Verify F7/Momentum compatibility and required assets, and document expected original Momentum functionality and rollback dependencies.
- [ ] Require an independent private review of hash/provenance evidence and owner approval **before** any hardware action.

## Safe qFlipper recovery preparation (no automatic installation)

1. **Do not retry the previously failed DFU CRC 9-99 updater.** Preserve the existing working official Momentum installation and SD-card data.
2. Before any future approved test, record the currently installed firmware version and obtain an authentic, compatible recovery package from its trusted publisher; verify its documented checksum where available. Keep a known-good USB data cable and a functioning qFlipper installation available.
3. Back up SD-card content and Flipper settings through supported tooling. Do not paste raw qFlipper logs, serial numbers, device identifiers, or backups into public CI or issues.
4. If an approved future update fails, **stop retrying** and use the official qFlipper recovery instructions for the detected device state; do not bypass CRC or force an unverified image. Preserve error details privately with sensitive fields redacted.
5. Recheck official Momentum functionality, SD-card access and settings only after an owner-approved recovery. Hardware success requires a real device acceptance record; a green CI workflow cannot substitute.

## CI fallback distinction

For the **same workflow and branch**, two consecutive completed failures or repeated pre-job failure triggers the approved public-safe integration fallback. Record failing run IDs, branch, SHA, fallback run ID, and which jobs actually ran. A green diagnostics-only fallback is **not** a native F7 build. If private Actions:read is HTTP 403 or dispatch is unavailable, mark **BLOCKED**, not passed. Do not assume billing caused runner failures.

## Android release separation

The Android test APK is separately gated by exact commit/run, package identity, versionCode, signing-certificate continuity, data-preserving update verification and physical AI1 BLE acceptance. The existing installed app must not be replaced or uninstalled to resolve a signature mismatch; side-by-side testing requires explicit owner approval.

## Handoff status

This checklist is a public-safe **documentation-only** change. No native F7 CRC/hash evidence, Android signing proof, firmware release, flash, installation or protected-branch merge is supplied by this document.
