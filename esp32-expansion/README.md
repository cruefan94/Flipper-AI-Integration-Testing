# Flipper AI ESP32 Expansion — independent starter project

Status: **source prototype only**. No known board-specific hardware verification, firmware flash, Momentum compatibility confirmation, or end-to-end AI integration.

This standalone subproject is staged in the **public integration-testing repository on an isolated branch/PR** until a dedicated `Flipper-AI-ESP32-Expansion` repository can be created. Its sources contain no private Momentum firmware, credentials, or artifacts. It does **not** replace the established Flipper AI Momentum or Android Satellite repositories.

## Components

- `firmware/`: separate Arduino/PlatformIO ESP32-WROOM-32/ESP32 DevKit example firmware; safe, explicit UART commands and a passive Wi-Fi network survey. Build target `esp32dev` is **only a provisional reference** until the owner's board is identified.
- `flipper/`: new **ESP32 Manager** standalone Flipper FAP source. UI queries status and capabilities; controls the optional LED. It does not silently flash firmware.
- `firmware/src/protocol.*` and `tests/`: bounded command parser with host-side tests.
- `.github/workflows/esp32-companion.yml`: source/CI validation and separate candidate artifacts.
- Existing [upstream ESP Flasher](https://github.com/0xchocolate/flipperzero-esp-flasher) handles **binary flashing**. The repository already has `.github/workflows/public-esp-flasher-fap.yml` to compile that third-party tool independently. ESP Flasher is GPL-3.0; do not copy its code into this project without satisfying its license.

## Wiring for likely classic ESP32 DevKit V1 (30 pins) — confirm board first

**Important:** USB-UART pins (RX0/TX0) on many DevKits are also electrically connected to the onboard CP2102/CH340 USB-to-serial bridge. An external Flipper TX can conflict with that bridge, even with USB used as power. Keep a working recovery path, disconnect any simultaneous USB serial host, and check exact board hardware before attempting a UART0 flash. Do not override a struggling pin with stronger drivers. If needed, isolate the onboard USB-UART TX connection or use a separate compatible power arrangement under an electronics technician's guidance.

### Mode A — Firmware programming / upstream ESP Flasher (USART 13/14)

| Flipper Zero LPUART | ESP32 DevKit V1 |
| --- | --- |
| Pin 13 / USART TX | RX0 / GPIO3 |
| Pin 14 / USART RX | TX0 / GPIO1 |
| Any ground e.g. pin 8 | GND |

The inspected upstream ESP Flasher version uses **FuriHalSerialIdUsart (pins 13/14)**, rather than the LPUART pins used by our manager. This may vary with fork/build; inspect the exact app before wiring.\n\nTo enter ESP32 ROM download mode: hold **BOOT** (GPIO0 low), tap **EN/RESET**, release EN, then release BOOT after the flashing tool initiates communication (exact timing varies). Flash only board-matched images/offsets, and read back/verify as supported by the tool.

### Mode B — Normal ESP32 Manager runtime (LPUART 15/16; recommended)

| Flipper Zero LPUART | ESP32 DevKit V1 |
| --- | --- |
| Pin 15 / PC1 / TX | RX2 / GPIO16 |
| Pin 16 / PC0 / RX | TX2 / GPIO17 |
| Any ground e.g. pin 8 | GND |

The included ESP32 firmware uses `Serial2.begin(115200, SERIAL_8N1, 16, 17)` for the FZ1 commands. **After flashing, disconnect Flipper 13/14 from RX0/TX0 and connect Flipper 15/16 to RX2/TX2.** Common GND stays connected. Future portable builds can expose separate labeled PROGRAM (USART) and MANAGER (LPUART) headers. Never short UART drivers together.

Both sides use **3.3V logic**. Never attach the 5V Arduino UART directly to Flipper. Keep the ESP32's USB power supply separate for initial bench setup; **do not connect Flipper 5V/3.3V rails to ESP32 VIN/3V3**. An external USB power bank can power the board for Mode B, but don't assume UART0 will be free from USB-serial contention in Mode A. LPUART is owned by one app at a time: exit Flipper AI before opening ESP32 Manager or ESP Flasher. Other ESP32 models may use different pins.

## Compile and flash workflow

1. Confirm the precise ESP32 **module and development board**, power requirements, labeled RX/TX, EN/BOOT controls and flash layout **before selecting or flashing any binary**.
2. For a supported classic ESP32 DevKit, compile reference firmware with `cd esp32-expansion/firmware && pio run -e esp32dev` (or review CI artifacts). The `platformio.ini` target must be adjusted for other models.
3. Build ESP32 Manager against the matching Flipper/Momentum SDK: `cd esp32-expansion/flipper && ufbt`. The public CI build uses official SDK only; a successful build cannot establish Momentum ABI compatibility.
4. Install a **Momentum-compatible** upstream ESP Flasher FAP independently, and place the **correct board-matched** precompiled .bin files on the Flipper's SD card under `apps_data/esp_flasher/`. Follow upstream instructions for firmware / bootloader / partition placement and exact offsets. **Do not use guessed offsets or binaries**.
5. Connect Mode A UART0 and validated separate power. Put the ESP32 into ROM download mode by its board-specific BOOT/EN procedure. Use ESP Flasher to flash, confirm write/verification, then reboot normally.
6. Disconnect Mode A (Flipper 13/14, ESP RX0/TX0) and connect Mode B (Flipper 15/16, ESP RX2/TX2). Open ESP32 Manager on the Flipper; use Detect / Capabilities / Passive Wi-Fi scan. If LPUART is occupied, exit the other app first.
7. Preserve the existing firmware and recovery backup. Never flash an ESP32 image to the Flipper itself.

## Protocol v1

115200 8N1 UART, one command at a time; ASCII lines terminated with LF, max 95 bytes excluding LF.

Flipper sends `FZ1|PING`, `FZ1|INFO`, `FZ1|CAPS`, `FZ1|STATUS`, `FZ1|WIFI_SCAN`, `FZ1|LED|ON` or `FZ1|LED|OFF`.

ESP32 replies as bounded lines `FZ1|OK|...`, `FZ1|DATA|...`, `FZ1|ERR|...`, always followed by `FZ1|END`. Unrecognized commands are rejected. Network SSIDs are sanitized and capped; never log passwords or automatically connect to Wi-Fi. Scan is a **passive** receiver scan, not an association or active-probe workflow.

**LED support defaults OFF** because GPIO numbers differ between boards. To opt in, define `FLIPPER_ESP_LED_PIN` for a verified onboard LED pin in PlatformIO build flags. Test polarity and pin use for the exact board.

## Roadmap / integration boundary

Phase 1 (this source): buildable UART firmware and standalone Flipper Manager; reuse separately compiled ESP Flasher.
Phase 2: identify physical board, test connections and actual flash/rollback; validate Momentum FAP.
Phase 3: status/capability-based integration with main Flipper AI using a reviewed protocol adapter and non-conflicting UART ownership.
Phase 4: optional I2S audio, sensors, OTA/USB expansion only after safety and device testing.

Do not imply this code is already merged, flashed, functional on user hardware, or available within the live Flipper AI menu.