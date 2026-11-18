# Release candidate evidence acceptance — 2026-11-17

Scope: **public-safe checklist only**. No private firmware source, DFU bytes, signing certificates, private logs, token values, or device identifiers may be copied to this repository.

## Evidence contract (all mandatory; missing = HOLD)

| Gate | Evidence recorded privately | Rejection condition |
|---|---|---|
| Exact heads | firmware SHA, Android SHA, integration SHA, AI1 protocol revision | Any unpinned or mismatched head |
| Firmware native F7 | latest completed Actions run ID + attempt; build target; encrypted-only artifact reference | Synthetic CRC alone, earlier successful attempt superseded by incomplete/failed latest attempt |
| Real DFU | parse actual firmware.dfu header/suffix, validate suffix length and CRC32 over bytes excluding stored CRC, compare updater manifest hashes | 9-99 quarantined image, missing real DFU, mismatch |
| Updater | .tgz member inventory, manifest SHA-256, reproducible private artifact identity | Unencrypted public artifact or unknown provenance |
| Android APK | full-feature APK build run, versionCode, package ID, artifact SHA-256, signing certificate SHA-256 | skipped APK build, unsigned build, missing stable signer |
| Android update | compare installed package certificate digest with candidate and require monotonic versionCode | signing mismatch; never uninstall or replace user app |
| BLE AI1 | same protocol version, UUIDs, characteristic properties, message framing, errors, timeout, consent behavior across both exact SHAs | spec drift, unknown firmware startup behavior |
| Device acceptance | owner-authorized Android/Flipper test records and recovery verification | CI-only evidence mistaken for hardware proof |

## Two-failure routing ledger

Key each sequence by **repository + workflow ID + exact branch**. Count only completed failing attempts; an infrastructure failure must be labeled separately from source/test failure. After two consecutive failures, or repeated pre-job-provisioning failure, attempt only the approved public-safe fallback appropriate to the component. Record trigger run IDs, fallback workflow ID/run ID, dispatch result and classification. A firmware-only fallback does **not** satisfy an Android build failure. If dispatch is unavailable or private Actions:read returns 403, record **BLOCKED**, do not invent a run ID or weaken gates.

Known Android trigger for workflow `420703090`: runs [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456). Android-compatible authorized fallback remains unverified.

## Current observation boundaries

- [Native F7 run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): latest jobs query reports custom-firmware success. [Run 44180961225](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225) likewise reports custom-firmware success. Job success does not disclose or independently establish private source SHA, real DFU checksums, or hardware acceptance.
- [Android run 44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456): latest jobs query reports host-regression failure; do not claim an APK exists.
- [Private release handoff PR 23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and [public-safe failover PR 23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23) remain the prerequisite policy sources.
- The failed **CRC 9-99** updater is permanently excluded from retry. Preserve qFlipper recovery documentation; no automatic flashing or installation.

## Handoff format

`component | repo | branch | exact SHA | workflow/run/attempt | result | artifact SHA-256 (private if sensitive) | AI1 revision | blockers | owner | next action`

The integration-testing workstream exclusively maintains the combined candidate ledger. Keep feature branches isolated; promote only after the exact evidence above is complete. No protected merges or production deployment.
