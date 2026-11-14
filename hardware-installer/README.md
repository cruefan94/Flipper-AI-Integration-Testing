# Flipper AI Hardware Installer — safety-first candidate

**Source-only experimental subsystem. Nothing connects, erases, flashes, resets, or rewires a board automatically.** This is an extension of [ESP32 Expansion draft PR #9](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/9), with compatible functions staged for the private custom Momentum [Issue #10](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/10). The owner's working firmware and Android Satellite remain unchanged.

## Detection vs programming

- ESP32 Manager's **Auto-detect attached (toggle)** sends **read-only `FZ1|INFO`** over the 3.3V LPUART connection about every five seconds while the app stays open. It detects a *previously programmed* FZ1 companion, not an unprogrammed ESP32 ROM, an arbitrary USB serial device, the official ESP32-S2 Wi-Fi Devboard's stock debugger firmware, or an Arduino Uno. The response is unauthenticated; it is a useful hint, **not chip identity verified for flashing**.
- Flipper AI's separate, explicitly selected FZ1 menus provide read-only info/status/capabilities and passive Wi-Fi scans. AI cannot silently flash or control an unknown board.
- Firmware builds are **precompiled in GitHub Actions**. Flipper Zero does not compile ESP32 source or Arduino sketches.
- `verify_bundle.py` independently checks image SHA256, explicit board/chip match, declared ESP flash capacity, hex flash offsets, overlaps, safe relative filenames and optional Uno R3 Intel HEX checksums. Hashes validate downloaded file consistency **only**, not firmware publisher identity. A command-line `--approve-stage` is required to copy ESP images into an existing SD staging folder; copying never starts flashing.
- Actual classic ESP32/S2 writes are delegated to a separately installed **Momentum-compatible** [ESP Flasher](https://github.com/0xchocolate/flipperzero-esp-flasher), GPL-3.0. Verify the exact app ABI, pinout, board model, image provenance and readback/MD5 on real hardware. The script does not claim an on-device selection/confirmation screen; the flasher provides the physical approval UI.

## Profile capabilities

| Board profile ID | Hardware | Installer support |
| --- | --- | --- |
| `esp32_wroom32_devkit` | Owner's photographed **38-pin ESP-WROOM-32** board in screw-terminal adapter | Precompiled ESP32 image preflight/staging, user-approved separate Flipper ESP Flasher |
| `flipper_wifi_devboard_s2` | Official Flipper Wi-Fi developer board, ESP32-S2 | Separate ESP32-S2 images only; preserve existing Black Magic firmware unless explicitly replacing it |
| `arduino_uno_r3` | ATmega328P Uno R3-compatible board | Intel HEX validation only; **no direct Flipper AVR flash backend**; use Raspberry Pi/PC + validated USB bootloader/avrdude |
| `arduino_uno_r4` | RA4M1 Uno R4 variant | Unsupported; not AVR and cannot use Uno R3 image |

**Voltage:** ESP32 UART logic is 3.3V; never connect Uno R3 5V UART straight to Flipper 3.3V pins. For classic ESP32 runtime: Flipper pin 15 TX to GPIO16 RX2, 16 RX from GPIO17 TX2, common GND. For current upstream ESP Flasher UART0 mode: Flipper 13 TX to GPIO3 RX0, 14 RX from GPIO1 TX0, common GND, manual BOOT/EN. **Validate actual compiled flasher pinout and inspect onboard USB-UART driver contention before programming.** Power ESP32 separately over USB initially and do not join voltage rails blindly. Close Flipper AI and ESP32 Manager before ESP Flasher and switch wires physically between modes.

## Preflight example (no flashing)

Prepare an authoritative `manifest.json` beside the firmware `.bin` files. Its required structure is shown below; insert **real**, verified digests and the actual chip's flash capacity.

~~~json
{
  "schema": 1,
  "board_id": "esp32_wroom32_devkit",
  "chip": "esp32",
  "version": "approved-release-1",
  "flash_size_bytes": 4194304,
  "images": [
    {"file": "bootloader.bin", "offset": "0x1000", "sha256": "REPLACE_WITH_64_HEX_SHA256"},
    {"file": "partitions.bin", "offset": "0x8000", "sha256": "REPLACE_WITH_64_HEX_SHA256"},
    {"file": "firmware.bin", "offset": "0x10000", "sha256": "REPLACE_WITH_64_HEX_SHA256"}
  ]
}
~~~

Offsets above are **examples only**, not guaranteed correct for your target. Inspect the source build manifest and chip flash map before staging. The verifier rejects placeholder digests and images that exceed the confirmed capacity.

~~~sh
python3 hardware-installer/verify_bundle.py /path/to/manifest.json --board esp32_wroom32_devkit
# After matching exact chip, boot mode, image source, size, SHA and offsets:
python3 hardware-installer/verify_bundle.py /path/to/manifest.json --board esp32_wroom32_devkit \
  --stage-to /path/to/FlipperSD/apps_data/esp_flasher --approve-stage
~~~

This stages precompiled files for manual selection inside ESP Flasher. It does not make a Flipper-mounted SD card magically accessible from a different computer/phone and it never overwrites existing firmware files. The Flipper itself cannot currently run this Python validator.

## Outstanding work

- Integrate/compile FZ1 Manager natively against pinned custom Momentum; keep the independently maintainable public source and custom firmware fork separate.
- Build and validate the exact upstream GPL ESP Flasher FAP against the custom firmware's SDK, and test physical UART0 wiring and readback verification.
- Firmware package identity/flash metadata beyond SHA is not authenticated; a trusted signing/provenance process and true MCU chip-ID readback must gate production updates.
- Safe external Flipper-to-ESP32 boot/reset control requires a hardware switching/level-shifting interface. This prototype only guides manual BOOT/EN.
- Full plug-and-play and **automatic firmware flashing are not implemented**. Automatic detection is opt-in and limited to the already installed FZ1 protocol; user approval is mandatory for destructive operations.
