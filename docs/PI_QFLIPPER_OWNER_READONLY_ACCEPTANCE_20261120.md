# Raspberry Pi 4B / first-generation Pironman: qFlipper read-only acceptance

**Status:** owner-device acceptance procedure only. No hardware validation or backup/recovery success claimed. This document does not authorize flashing, updating firmware, writing GPIO, changing cooling services, or reading private logs.

## Provenance and scope

- Parent qFlipper PATH-only preflight source: `raspberry_pi/qflipper_preflight.py` from draft PR #252.
- Parent isolated synthetic test gate: draft PR #254, exact source commit `28a9b09efb0f9f5f8d460c280546f13ed6d58855`.
- The preflight checks executable availability **only**. It does not open qFlipper, USB, serial ports, firmware files or backups.
- A passing GitHub Actions run is host-side evidence only, not Pi, Flipper or Pironman validation.

## Owner-controlled Pi acceptance (opt-in, no sudo)

Run only if the owner wishes to test, from a local terminal on the Raspberry Pi after inspecting the script. Do not run an arbitrary downloaded script. Ensure the current checkout includes the expected reviewed file.

```sh
python3 raspberry_pi/qflipper_preflight.py
python3 raspberry_pi/qflipper_preflight.py --consent
```

Expected first result: `status=not_authorized`, with qFlipper/USB/backup/recovery `unknown`.
Expected second result: `status=local_tool_check_unverified`, with qFlipper either `available_on_path` or `not_found_on_path`; USB/backup/recovery remain `unknown`.

Do **not** interpret PATH availability as working USB connectivity, a safe firmware updater, a valid backup, or recovery readiness. Do not start qFlipper or connect/disconnect devices as part of this acceptance.

## Evidence capture and privacy

Record date, Pi OS version (if already known), script commit SHA, the two sanitized JSON status results, and whether cooling/OLED/RGB appeared unchanged to the owner. Do not post usernames, serial numbers, device IDs, USB logs, home paths, tokens, or backup contents. Redact before any public issue comment.

## Stop / rollback

If unexpected output, exceptions, fan/OLED/RGB changes, or high load occur, stop the procedure and report observations. The two commands are one-shot and make no configuration changes; no service restart or rollback command is expected. Preserve existing Pironman fan and OLED services. No privileged remediation should be automated.

## Separate future gates (not performed)

1. Validate real USB enumeration with explicit owner consent and redacted evidence, no firmware update.
2. Validate qFlipper's read-only device identification and backup planning with no data export by default.
3. Test an owner-approved backup to a private destination, inspect integrity and recovery instructions without restoring.
4. Only after separate native artifact checks and explicit owner approval, consider firmware workflows; the previously failed DFU CRC 9-99 updater must never be retried.

## Parallel Pi project tracker

| Pi-side project | Next isolated acceptance gate |
| --- | --- |
| First-generation Pironman RGB/fan/OLED center | Read actual installed controller/service API; model reversible settings without writing to fan or OLED |
| 10-second Pi/OLED/Flipper/ESP32 monitor | Consent-gated, read-only live Pi sampling; unavailable peripherals must remain unknown |
| Pi OS health / low-memory browser | Measure memory pressure first; reversible per-user changes only |
| qFlipper workstation | This PATH-only owner acceptance, then separate USB/backup gates |
| Pi-local existing-runtime AI | Discover installed runtime without launching model or exposing prompts |
| Phone-to-Pi remote access | Opt-in authenticated local access design, no default listener |
| BLE/Wi-Fi/USB gateways | Protocol compatibility and permission gates before hardware access |

## Integration and CI safety

This optional Pi-side procedure is **not** an Android test APK or F7 Momentum updater dependency. Do not promote to unified release candidates without exact commit, passing exact-head CI, physical compatibility evidence, and integration-testing workstream approval. Preserve the two-consecutive-failures public-safe fallback policy; private Actions-read 403 is **BLOCKED**, not evidence of successful fallback. No private firmware source, credentials or device logs belong in public tests.
