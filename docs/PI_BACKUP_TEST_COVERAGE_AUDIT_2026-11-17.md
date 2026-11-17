# Pi qFlipper backup test-coverage gate — 2026-11-17

Status: **isolated audit, not a release gate passed**. Pi-only. No hardware actions.

## Exact evidence

- Parent draft PR #98: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/98
- Tested parent commit: `90011f7ebd325616883f88c8e7ec31877af2e2cc`
- Dedicated CI: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44176567893 — Python 3.11 and 3.12 jobs succeeded.
- Earlier discovery failure: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44167236277 — test import root, not provisioning.
- Workflow: `.github/workflows/pi-backup-readiness-ci.yml`, discovers `test_pi_backup*.py` and `test_pi_readiness*.py` from `raspberry_pi/tests`.
- Reported seven discovered tests do **not** establish coverage of the earlier full backup verifier suite. In particular, `raspberry_pi/tests/test_pi_backup_manifest_verify.py` and `raspberry_pi/tests/test_pi_backup_readiness_contract.py` were not found at the parent ref when queried. `raspberry_pi/tests/test_pi_readiness_privacy_contract.py` was found. Do not assume a file is absent from the project just because this candidate branch lacks it.

## Acceptance gate for integration-testing owner

1. Reconcile the stacked Pi PR dependency chain and list exact source files on the intended candidate ref, without editing the shared candidate branch concurrently.
2. Ensure backup-manifest verification, tamper rejection, root/symlink race rejection, readiness-summary fail-closed behavior and privacy contract are all represented by named discovered tests on the **same exact commit**. Test file presence alone is insufficient.
3. Record test names and counts for Python 3.11 and 3.12; require nonzero execution of every required suite and fail CI if any required suite is missing.
4. Confirm sanitized logs contain no backup filenames, device identifiers, hashes or private source.
5. Hand off exact commit, CI links, and dependency list to the integration-testing ledger; no APK or F7 firmware promotion is implied by this Pi-only gate.

## Standing safety boundaries

The Pi backup readiness summary is read-only and never authorizes restore. No device writes, fan/RGB/OLED control changes, firmware flash, real backup restore, privileged commands, APK replacement, or protected-branch merge. Two consecutive completed failures on the same workflow/branch require the approved public-safe fallback, subject to actual permissions. Private Momentum Actions:read HTTP 403 remains **BLOCKED**, not evidence of a dispatched fallback.

## Other Pi subprojects

Tracked, unchanged this checkpoint: first-generation Pironman reversible fan/RGB/OLED UI; 10-second read-only Pi/OLED/Flipper/ESP32 monitor; native Pi OS health and low-memory browser/cleanup; qFlipper USB diagnostics/recovery; existing-runtime Pi-local AI; opt-in secure phone remote access; BLE/Wi-Fi/USB gateways. All require separate implementation and hardware acceptance gates.
