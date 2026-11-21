# Arduino Uno ↔ ESP32 / Flipper GPIO: offline operator guide

**Lab only.** This document explains how to use `lab/uno_gpio_review.py` to reject obvious unsafe proposed signal connections **before** assembling a circuit. A `REVIEW` result is **not approval to connect, power, or flash hardware**. The reviewer is not a board-specific pinout validator.

## Reproducible offline check (no hardware attached)

From the repository root, on a Raspberry Pi 4B or desktop with Python 3:

```sh
python3 lab/uno_gpio_review.py --self-test
python3 lab/uno_gpio_review.py lab/fixtures/uno_gpio_5v_block.json
```

The second command should print `BLOCK link 1: over-3.3V signal into 3.3V endpoint` and exit 1. It is a **synthetic fixture**, not a measurement of your boards. The script does not open USB/serial/GPIO ports, flash firmware, or transmit radio.

## Owner-operated measurement and wiring gate

1. Identify the **exact** Arduino Uno revision, ESP32-WROOM/S2 carrier board revision, Flipper GPIO pin and sensor module. A module's supply rating does not establish its signal voltage.
2. With everything disconnected, obtain the manufacturer pinout/datasheet and identify GPIO direction, permitted input voltage, boot/strapping pins, UART/I²C usage and required power rails. Do not assume ESP32-WROOM and ESP32-S2 pins are interchangeable.
3. On a separate safe bench, use a meter to confirm the actual supply rail and idle output-high voltage of each module. Do not measure unknown circuits by connecting them to Flipper or ESP32 GPIO first.
4. Treat **any 5V signal driving an ESP32 or Flipper 3.3V input** as unsafe without a suitable verified level shifter. A simple resistor divider may suit a *unidirectional* slow digital signal but is not a blanket I²C/UART or bidirectional solution. Confirm logic thresholds and edge rates.
5. For I²C, inspect **all** pull-up resistors and their voltage rail, including those already fitted on breakout boards. Use a bidirectional, protocol-appropriate level shifter where needed.
6. Confirm a common signal reference (ground), but never tie together uncertain power outputs or rely on a USB hub to prevent backfeeding. Power source, current budget, protection and USB power interactions require a separate schematic review.
7. Record only board **families**, link type, observed voltage and verification booleans in a synthetic/reduced JSON file. Exclude serial numbers, MAC addresses, locations, private firmware and any real device logs.
8. Run the offline checker. `BLOCK` means stop. `REVIEW` means **stop for manual pinout, power, level-shifter and measurement approval**; it does not mean safe to wire.
9. Any future owner-operated Pi serial/flash procedure must be a separately approved workflow with explicit chip identity, boot-mode confirmation, power checks, backup and recovery plan. This guide authorizes no flashing.

## Safety boundary and integration handoff

- No physical hardware test has been performed. No voltage or board-specific pinout is asserted as measured.
- This is an optional external lab tool, not an Android AI Satellite APK feature or Momentum F7 updater feature.
- Exact-commit passing CI and an owner-operated physical review are required before any integration promotion.
- Keep the failed DFU CRC 9-99 updater quarantined; never retry it. Preserve Android signing and installed app data.
- After two consecutive completed failures on the same branch/workflow, or repeated pre-job failure, use only the established **public-safe** fallback. If private Actions:read remains HTTP 403, label fallback **BLOCKED**; never publish private firmware or secrets.
