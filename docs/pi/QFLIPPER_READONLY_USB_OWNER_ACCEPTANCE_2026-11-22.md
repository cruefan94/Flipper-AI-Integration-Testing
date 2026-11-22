# Raspberry Pi 4B / first-generation Pironman — qFlipper read-only USB acceptance (draft)
Date: 2026-11-22. Pi-side only. No device validation performed.

## Source and release boundaries
Stacked on draft PR #366 (commit `6f7ce9742d0ad5e1a65a9fe046332d895c49c029`), itself following #361/#356/#351/#348. This document is not evidence that those changes are merged or hardware-proven. Private Momentum release blockers: PR #23. Public-safe failover coverage: Integration-Testing PR #23. Private Actions:read 403 = BLOCKED until authorized access and real monitoring are verified.

## Owner-operated observation (explicit opt-in only)
1. Do not disconnect or disable Pironman cooling, fan, OLED, RGB, existing services or working Flipper connection. Do not run sudo, modprobe, chmod, udev writes, reset, firmware updates, DFU, or qFlipper repair.
2. With Pi running normally, inspect `command -v qFlipper` and `qFlipper --version` only if supported; a missing version option is not a failure. Do not launch a second qFlipper while it is actively in use.
3. Capture `lsusb` once with Flipper disconnected, then once connected using a known data-capable cable. Compare entries locally; do not infer device identity from ST vendor ID alone.
4. Optionally inspect `ls -l /dev/ttyACM* /dev/ttyUSB* 2>/dev/null` and `journalctl -k -b --no-pager -n 30` as the unprivileged Pi owner. If journal access is denied, record 'unavailable'; never escalate privileges.
5. Before sharing output, remove serial numbers, unique identifiers, MAC addresses, personal paths, network identifiers, tokens and any private logs. Prefer only bus/device counts, VID:PID, generic product label and yes/no device-node observations.
6. Confirm cooling continues and Pi remains responsive; stop if fan/OLED behaves unexpectedly, USB disconnects repeatedly, power warnings occur, or qFlipper requests a write/flash.
7. Record Pi OS release, qFlipper version if known, cable type, whether each device was physically connected, and observed counts; keep raw logs local.

## Offline acceptance matrix (no device commands in CI)
| Case | Expected |
| --- | --- |
| Identical repeated addressed lines | One device counted |
| Conflicting VID:PID at same bus/device | Fail closed |
| Recognizable addressed line with missing/malformed VID:PID | Fail closed |
| STMicroelectronics VID present | Possible ST device only, never verified Flipper |
| No connected Flipper | No false verified-Flipper assertion |
| Missing permissions or missing journal | Unknown/unavailable, not success |
| OLED/ESP32/Flipper absent | Clearly unavailable; no fabricated telemetry |
| 10-second monitor interval | Only after explicit owner opt-in, read-only and no hardware writes |

## Subproject status and gates
- Pironman control center: planned; reversible RGB/fan/OLED UI must preserve working cooling and require owner-confirmed hardware interface.
- Pi/OLED/Flipper/ESP32 10-second monitor: offline parsing/prototypes; live sources and device safety not validated.
- Pi OS health/low-memory browser/cleanup: planned; diagnostics before any reversible opt-in changes.
- qFlipper USB diagnostics: synthetic CI previously reported for #361; this acceptance document needs exact-head review; backup/recovery must remain separate and explicitly authorized.
- Pi-local existing-runtime AI: planned; no custom runtime or unapproved model downloads.
- Phone-to-Pi remote access: planned; consent, authentication and revocation gate before network exposure.
- BLE/Wi-Fi/USB gateways: planned; protocol and permissions tests before real transport integration.

## CI and candidate policy
For each workflow/branch, record exact run IDs and classify code versus runner failure. Two consecutive completed failures or repeated pre-job failure triggers the approved PUBLIC-SAFE fallback; never copy private firmware, binaries, credentials or logs into public CI. If private Actions:read is unavailable, report BLOCKED and request owner configuration; never assert fallback worked. No Android APK/F7 .tgz integration or release ledger edit from this documentation. Never retry the known DFU CRC 9-99 updater. Android signing mismatch forbids replacing the installed app. No protected merge or physical flash.
