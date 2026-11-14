# Flipper AI ESP32 Expansion — independent starter project

Status: **source prototype only**. No known board-specific hardware verification, firmware flash, Momentum compatibility confirmation, or end-to-end AI integration.

This standalone subproject is staged in the **public integration-testing repository on an isolated branch/PR** until a dedicated \`Flipper-AI-ESP32-Expansion\` repository can be created. Its sources contain no private Momentum firmware, credentials, or artifacts. It does **not** replace the established Flipper AI Momentum or Android Satellite repositories.

## Components

- \`firmware/\`: separate Arduino/PlatformIO ESP32-WROOM-32/ESP32 DevKit example firmware; safe, explicit UART commands and a passive Wi-Fi network survey. Build target \`esp32dev\` is **only a provisional reference** until the owner's board is identified.
- \`flipper/\`: new **ESP32 Manager** standalone Flipper FAP source. UI queries status and capabilities; controls the optional LED. It does not silently flash firmware.
- \`firmware/src/protocol.*\` and \`tests/\`: bounded command parser with host-side tests.
- \`.github/workflows/esp32-companion.yml\`: source/CI validation and separate candidate artifacts.
- Existing [upstream ESP Flasher](https://github.com/0xchocolate/flipperzero-esp-flasher) handles **binary flashing**. The repository already has \`.github/workflows/public-esp-flasher-fap.yml\` to compile that third-party tool independently. ESP Flasher is GPL-3.0; do not copy its code into this project without satisfying its license.

## First wiring plan — provisional for classic ESP32 DevKit / WROOM UART0

| Flipper Zero | ESP32 development board |
| --- | --- |
| Pin 15 / PC1 / LPUART TX | RX0 / GPIO3 |
| Pin 16 / PC0 / LPUART RX | TX0 / GPIO1 |
| Any GND pin (e.g. 8) | GND |
| **No Flipper power rail connected** | Power via its own USB connector |

**Both devices use 3.3V UART logic.** Connect TX to RX, RX to TX and share ground. Do **not** attach a 5V Arduino UART output to Flipper GPIO. This is not universally valid for ESP32-S2/S3/C3 and may need changes for the owner's exact dev board. Flipper AI's existing ESP32-S2 app also owns LPUART: **only one app may use it at a time**. Exit Flipper AI before launching ESP32 Manager or ESP Flasher.

## Compile and flash workflow

1. Confirm the precise ESP32 **module and development board**, power requirements, labeled RX/TX, EN/BOOT controls and flash layout **before selecting or flashing any binary**.
2. For a supported classic ESP32 DevKit, compile reference firmware with \`cd esp32-expansion/firmware && pio run -e esp32dev\` (or review CI artifacts). The \`platformio.ini\` target must be adjusted for other models.
3. Build ESP32 Manager against the matching Flipper/Momentum SDK: \`cd esp32-expansion/flipper && ufbt\`. The public CI build uses official SDK only; a successful build cannot establish Momentum ABI compatibility.
4. Install a **Momentum-compatible** upstream ESP Flasher FAP independently, and place the **correct board-matched** precompiled .bin files on the Flipper's SD card under \`apps_data/esp_flasher/\`. Follow upstream instructions for firmware / bootloader / partition placement and exact offsets. **Do not use guessed offsets or binaries**.
5. Connect UART and separate power. Put the ESP32 into ROM download mode by its board-specific BOOT/EN procedure. Use ESP Flasher to flash, confirm write/verification, then reboot normally.
6. Open ESP32 Manager on the Flipper; use Detect / Capabilities / Passive Wi-Fi scan. If LPUART is occupied, exit the other app first.
7. Preserve the existing firmware and recovery backup. Never flash an ESP32 image to the Flipper itself.

## Protocol v1

115200 8N1 UART, one command at a time; ASCII lines terminated with LF, max 95 bytes excluding LF.

Flipper sends \`FZ1|PING\`, \`FZ1|INFO\`, \`FZ1|CAPS\`, \`FZ1|STATUS\`, \`FZ1|WIFI_SCAN\`, \`FZ1|LED|ON\` or \`FZ1|LED|OFF\`.

ESP32 replies as bounded lines \`FZ1|OK|...\`, \`FZ1|DATA|...\`, \`FZ1|ERR|...\`, always followed by \`FZ1|END\`. Unrecognized commands are rejected. Network SSIDs are sanitized and capped; never log passwords or automatically connect to Wi-Fi. Scan is a **passive** receiver scan, not an association or active-probe workflow.

**LED support defaults OFF** because GPIO numbers differ between boards. To opt in, define \`FLIPPER_ESP_LED_PIN\` for a verified onboard LED pin in PlatformIO build flags. Test polarity and pin use for the exact board.

## Roadmap / integration boundary

Phase 1 (this source): buildable UART firmware and standalone Flipper Manager; reuse separately compiled ESP Flasher.
Phase 2: identify physical board, test connections and actual flash/rollback; validate Momentum FAP.
Phase 3: status/capability-based integration with main Flipper AI using a reviewed protocol adapter and non-conflicting UART ownership.
Phase 4: optional I2S audio, sensors, OTA/USB expansion only after safety and device testing.

Do not imply this code is already merged, flashed, functional on user hardware, or available within the live Flipper AI menu.