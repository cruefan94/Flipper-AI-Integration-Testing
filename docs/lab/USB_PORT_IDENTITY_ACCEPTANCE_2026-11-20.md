# Pi / ESP32 / Arduino / Flipper USB identity: owner-operated acceptance gate

Status: **PUBLIC-SAFE LAB ONLY — documentation, not electrical approval**. This document complements backpack USB-backfeed draft PR #240 (commit `7f251f4f27af21f72818a794f692c998f2039ebb`). Do not attach unverified USB power paths or run flashing commands as part of this procedure.

## Goal
Distinguish the actual USB bridge/ROM interface of each owner's board before proposing Pi-based serial diagnostics. ESP32-WROOM is a chip/module family, not a guarantee of a particular USB bridge; ESP32-S2 boards can expose native USB and/or external UART bridges. Arduino Uno may expose a separate USB-to-serial controller. Flipper Zero USB is **not** automatically an ESP32 programmer.

## Safety prerequisites (all required)
1. Owner opt-in and physical supervision; one board at a time. Use a known-good **data-capable** USB cable and a separately confirmed safe power configuration. Do not tie independently powered 5V rails together.
2. No GPIO wires connected, no common power wiring through the backpack, no external 5V on 3.3V pins, and no level-shifter assumptions. Keep Flipper, Pi, Arduino, ESP32-WROOM, and ESP32-S2 independent during identity collection.
3. On Raspberry Pi, do not stop or alter Pironman cooling/fan/OLED services. Avoid privileged commands and avoid collecting private serial numbers.
4. No EN/BOOT pin actuation, DTR/RTS toggles, ROM-loader entry, esptool writes, baud-rate changes, or firmware flashing. USB enumeration is **not** proof that safe flashing is possible.

## Optional local read-only commands (owner runs, not automation)
Before connecting a board:
```sh
lsusb
ls -l /dev/serial/by-id/ 2>/dev/null || true
```
Connect exactly one board by USB, then repeat the commands. Record only the **new vendor/product ID**, generic interface type and whether a new serial device appeared. **Redact** any serial number, full /dev/serial/by-id name, user name, hostname and unique device path before sharing. Do not run `sudo`, `esptool`, `stty`, `screen`, `minicom`, `picocom`, `dfu-util`, `qFlipper` flashing, or open serial ports in this stage.

Disconnect the board and confirm the observed entry disappears. Repeat separately for ESP32-WROOM development board, ESP32-S2 board, Arduino Uno and Flipper Zero. If a board is bare (no onboard USB), mark **NO DIRECT USB** and stop: a properly rated USB-to-UART adapter and verified board schematic are prerequisites, not assumptions.

## Minimal sanitized acceptance record
| Board label | VID:PID (no serial) | Interface category | New serial node? | Unplug removes it? | Status |
|---|---|---|---|---|---|
| WROOM | unknown | unknown | unknown | unknown | PENDING |
| ESP32-S2 | unknown | unknown | unknown | unknown | PENDING |
| Uno | unknown | unknown | unknown | unknown | PENDING |
| Flipper | unknown | unknown | unknown | unknown | PENDING |

Treat ambiguous multiple devices, changing power behavior, brownouts, unexpected resets, or overheating as **STOP / NEEDS REVIEW**. Do not infer boot mode, GPIO pinout, voltage tolerance, transport interoperability or board identity solely from a VID:PID. Require manufacturer board revision/schematic and explicit owner approval before any later ROM handshake or write-capable transport test.

## Integration gates
- Offline CI for PR #240 must pass at exact commit; it covers only synthetic topology logic.
- This identity worksheet is not an executable test and cannot establish device electrical safety.
- Real owner-provided sanitized observations and manufacturer board-specific documents are required for physical acceptance.
- Pi flashing tools, Flipper-to-ESP32 programming, and ESP32-S2 coexistence stay optional and **BLOCKED pending physical evidence**.
- No promotion into Android test APK or native Momentum F7 updater; the integration-testing workstream alone owns the unified release ledger.
- Preserve two-consecutive-failure public-safe CI fallback, private Actions:read HTTP 403 as BLOCKED, CRC 9-99 quarantine, Android signer continuity, and deferred Civic integration.
