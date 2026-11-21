# ESP32-WROOM EN/BOOT preflight — verified CI handoff (2026-11-21)

Scope: isolated, public-safe hardware-lab guidance only. This is **not** firmware acceptance, authorization to flash, or proof of an ESP32 device working.

## Provenance
- Source prototype: [PR #295](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/295), commit `1fa1e866adf710d5dac81fd71d8b530eb0718b79`.
- Dedicated regression workflow: [PR #297](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/297), commit `dad2375cf9c800cec563c5f846100475a218a610`.
- Exact-commit Actions runs: [nine-test boot preflight #44913570123](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44913570123) **completed/success**; [public runner smoke #44913570078](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44913570078) **completed/success**.
- Tests are synthetic and offline; no physical board, USB serial, voltage measurement, esptool or programming was exercised.

## Owner-operated, non-destructive board acceptance checklist
1. Record the exact module marking, devboard manufacturer/revision, USB-UART chip, and published schematic. Do not infer pin functions from the label 'ESP32' alone.
2. With power disconnected, inspect EN/BOOT switches, solder bridges, USB connector, regulator, and whether GPIO0 has a board-level pull-up. Never connect 5 V to ESP32 3.3 V GPIO.
3. Before any cross-board wiring, check supply and logic-level compatibility, common ground, USB power/backfeed protection, and any external pull resistors with a meter. An Arduino Uno TX signal requires appropriate level shifting before ESP32 RX.
4. If the board is connected by USB to the owner's Pi, **read only**: `lsusb`, `ls -l /dev/serial/by-id/`, `dmesg --ctime | tail -n 30`. Do not open ports, toggle DTR/RTS, reset the device, or run a flash command in this phase.
5. For a classic ESP32, GPIO0 low during reset requests the ROM download mode; EN resets the chip. Boot strap behavior, including GPIO2 and GPIO12/MTDI, is variant- and board-dependent. A GPIO12 strap can affect flash supply selection on some classic ESP32 designs. Verify against the exact Espressif datasheet and devboard schematic before changing connections.
6. Record observed boot messages only if collected locally by the owner in a later explicitly approved session. Redact device serial numbers and personal paths before public reporting.
7. If enumeration fails, check USB data cable, USB power and board identification first. Do not assume a firmware/bootloader defect or bypass safety gates.

## Integration gate
- Public-safe regression CI passing is **necessary but insufficient**. Require board schematic review, owner-operated read-only USB enumeration, electrical acceptance, and a separately approved non-production hardware test plan before promoting a peripheral.
- Android Satellite APK: **not integrated**. Momentum native F7 updater .tgz: **not integrated**. AI1 BLE contract: **not validated by this work**.
- Existing failed DFU CRC 9-99 updater remains quarantined; Android signing mismatch prohibits replacing the installed app.
- Private Actions:read monitoring historically returned HTTP 403: classify as **BLOCKED**, not as a passed fallback. Preserve two-consecutive-failure routing and do not expose private firmware in public CI.
- Canonical ledger ownership remains with the integration-testing release workstream; this document is only a dependency handoff.
