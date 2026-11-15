# Next custom Momentum ESP32 programmer candidate — isolated encrypted CI

## Purpose

The next custom Momentum firmware for the owner's Flipper Zero should preserve
Flipper AI, Android Satellite BLE development, Momentum themes/stock tools, and
include the separately authored ESP32 Manager internal app. A compatible
**ESP Flasher** GPIO programmer is a distinct GPL-3.0 application built against
the exact same pinned Momentum SDK.

This development branch validates, encrypts and provides **two separate
artifacts** from the same CI run. This avoids breaking the native firmware
updater format and stops the app programmer from being mistaken for firmware:

1. `encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED` — the
   existing encrypted outer delivery, containing a verified native F7
   `flipper-z-f7-update-*.tgz`, its SHA256 manifest and warning.
2. `encrypted-esp32-programmer-momentum-sdk-GPL-UNTESTED` — a new,
   separately encrypted `esp32-programmer-UNTESTED.tar.gz`, containing
   `esp_flasher.fap` + individual checksums, full upstream GPL-3.0
   `LICENSE`, immutable upstream/patch/SKD provenance and install guidance.

Both packages are intended for **owner-only local decryption**. No Action
uploads source from the private firmware repository, a plaintext FAP,
plaintext updater, passwords, cloud API secrets, or model weights. The second
artifact is GPL-licensed software; preserve the license and corresponding
source offer from `SOURCE_PROVENANCE.txt` if it is redistributed.

## Technical gates performed by public-safe CI

- Fetch private firmware read-only through a short-lived secret held on the
  runner; confirm private source CI SHA and pinned upstream Momentum revision.
- Recheck Momentum AI BLE/GATT source contracts, ESP32 Manager/source tests,
  F7 firmware full native compilation, and the native updater package.
- Fetch ESP Flasher from its immutable GPL-3.0 upstream commit and apply the
  reviewed public-source patch for chip MD5 write verification, error
  propagation, and no automatic target reset after failed flashing.
- Compile its actual FAP against **that exact Momentum SDK**. Verify ELF
  header, size, GPL license, patch SHA, package contents, target identity,
  SHA256, encrypted/decrypted roundtrip and archive safety constraints.
- Publish only encrypted and explicitly `UNTESTED` artifacts.

The *programmer FAP does not get silently installed* by the firmware
`.tgz` updater. The user must individually approve app transfer/installation
and later approve every destructive flash inside ESP Flasher. A successful
CI compile does **not** prove any electrical GPIO connection, ESP32 ROM
identity, actual flash capacity, BOOT/EN behavior or on-chip MD5 on the
owner's real 38-pin ESP-WROOM-32 board.

## Physical gates before release

1. Keep the successfully installed custom Momentum firmware and a valid
   qFlipper/DFU recovery route. No bulk auto-install.
2. Confirm the ESP32 WROOM 38-pin actual board, 3.3V UART0 wiring and
   USB-to-UART contention; use independent USB power plus shared GND.
3. Verify chip ROM identity and actual flash capacity, precompiled image
   offsets and partition layout. Never flash an ESP32-S2 or Arduino Uno
   firmware onto the classic ESP32.
4. Review the SD `FZHW1` image manifest in ESP32 Manager; it is an
   **advisory text plan**, not hardware identity or authorization.
5. Manually transfer the compatible GPIO programmer FAP via supported
   Flipper SD/app installation. Connect UART0 only after closing Manager
   and Flipper AI; select firmware and affirm erase/write on the Flipper.
6. Verify the completed write with on-chip MD5 and a reboot/function test;
   record failure/recovery behavior before considering production release.

Current status: source/CI candidate; **NO physical flash** and **NO
installed upgrade**. Progress tracking: private firmware Issue #10 and
public isolated PRs for the independent ESP32 expansion.
