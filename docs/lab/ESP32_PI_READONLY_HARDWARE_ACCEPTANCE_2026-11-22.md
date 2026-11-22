# Pi 4B ↔ ESP32-WROOM read-only bootloader acceptance (2026-11-22)

Scope: owner-operated, **non-flashing** serial identification only. This document is an acceptance gate, not a wiring certification or permission to operate hardware. Parent: PR #346, commit a17b6459010a84a810cbbf122080dad575e14863. Exact-head workflow 44998294867 and public smoke 44998294800 passed. The nine cases are synthetic and do not establish real hardware safety.

## Stop before connecting
1. Confirm exact ESP32 board model, regulator, connector labels and its vendor schematic. Do not treat the module's 3.3 V requirement as proof that every development-board power pin is 3.3 V.
2. Confirm USB-to-UART adapter TX/RX logic levels are 3.3 V **by documentation or measurement**; a selectable 3.3 V supply alone does not prove 3.3 V I/O. Never connect a 5 V TX signal directly to ESP32 GPIO.
3. Use a common signal ground and cross TX→RX, RX←TX only after confirming actual pin labels. Do not connect an external 3.3 V power source in parallel with USB supply without an approved power architecture. Pi GPIO UART is 3.3 V only and not a substitute for a protected USB-UART adapter.
4. For classic ESP32-WROOM manual ROM-download entry: hold GPIO0 low using the board's BOOT button, pulse EN low using RESET, release EN while BOOT remains held, then release BOOT. Board circuitry can vary. Do not force straps or bridge unknown pins.
5. With power off, inspect for shorts, heat damage, incorrect connector orientation and uncertain grounds. Any uncertainty means STOP and obtain board photos/schematic.

## Owner-operated read-only observation
- Prefer a verified 3.3 V USB-UART adapter on the Pi, and identify the expected /dev/serial/by-id/ entry. Serial naming is not proof of chip identity.
- Observe the serial boot log at the board's documented baud rate (often 115200 for classic ESP32 boot messages). Avoid shell commands that write to the port or toggle DTR/RTS automatically; some adapters reset or strap the target when a port opens.
- Record only sanitized observations: adapter VID/PID, expected port basename, boot-mode category, whether ROM download mode was observed, and power/logic-level evidence. Never include serial numbers, MAC addresses, tokens or private firmware in public CI.
- STOP if voltage is unverified, power rails conflict, unexpected current/heat appears, boot log is ambiguous, or an adapter auto-reset sequence is unknown.
- **No esptool write_flash, erase_flash, reset commands, firmware upload, Flipper remote control, or OTA updates in this phase.** Even esptool chip_id may toggle DTR/RTS; it requires separate explicit owner approval.

## Independent component boundaries
- ESP32-S2 FlipperHTTP development board: different USB/boot paths and Flipper UART pins; do not apply WROOM GPIO/serial assumptions to S2/S3.
- Arduino Uno: 5 V GPIO; any Uno↔ESP32 signal crossing needs independently reviewed level conversion, especially I²C pull-ups.
- Flipper Momentum FAP v0.8: Android stock-RPC remains primary; FlipperHTTP secondary UART is unverified on hardware. Do not route private prompts via FlipperHTTP pending TLS review.
- Android APK and native F7 updater: **not integrated**; no candidate promotion from this document.

## Release and CI gates
- Parent exact-head: [ESP32 static preflight 44998294867](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44998294867) SUCCESS; [public smoke 44998294800](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44998294800) SUCCESS. New branch needs its own exact-head check.
- Two consecutive completed failures on the same workflow/branch, or repeated pre-job failure, require the approved **public-safe** integration-testing fallback. Record original/fallback run IDs, classify code versus infrastructure. Private Actions:read 403 = BLOCKED, not success or proof of billing failure.
- Private Phase 1 Momentum PR #23 and test-only public failover PR #23 remain authoritative. Release ledger belongs solely to integration-testing workstream.
- Known F7 DFU CRC 9-99 artifact must never be retried; Android signing mismatch prohibits replacing/uninstalling the installed app. No protected merges, production deployment or owner-device flashing.

Next gate: inspect this branch's CI and the real adapter/board schematics, then seek owner-performed read-only observations. No hardware was accessed to produce this document.
