# ESP32-WROOM + ESP32-S2 FlipperHTTP coexistence — isolated lab gate (2026-11-22)

Status: **documentation-only / no device validation / NOT approved for release integration**.

## Why separate these boards
The ESP32-WROOM-32 classic board and the ESP32-S2 FlipperHTTP development board are **not interchangeable**. Classic ESP32 has Bluetooth Classic/BLE and 2.4 GHz Wi-Fi; ESP32-S2 has 2.4 GHz Wi-Fi and native USB but **no Bluetooth radio**. Board-specific GPIO, bootloader entry and firmware/flash targets must remain separate. Never select a target solely because a Linux serial port appeared.

## Proposed roles (subject to owner verification)
| Component | Proposed role | Interface | Acceptance gate |
| --- | --- | --- | --- |
| Flipper Zero with stock Momentum | Portable UI / host | GPIO UART or stock RPC as supported | Pinout + voltage + protocol validation |
| ESP32-S2 devboard running FlipperHTTP | Optional *secondary* status/ping over UART | FAP v0.8 proposal: Flipper USART pins 13/14 at 115200 | Verify board revision, ground, level, UART pinout, actual flashed firmware and whole-line PONG |
| ESP32-WROOM-32 | Separate Wi-Fi/BLE experiment / owner-operated Pi flash target | USB-UART 3.3 V **logic** | Verify exact carrier, adapter, EN/GPIO0, power, chip-ID before any flash |
| Raspberry Pi 4B | Local lab tools / serial inventory | Pi USB host + verified USB-UART adapter | Owner manually identifies VID/PID and stable /dev/serial/by-id symlink |
| Android AI Satellite | Primary phone BLE/AI compute | Phone native Bluetooth + stock Momentum RPC | AI1 service/protocol end-to-end evidence required; stock RPC alone is not AI1 |

## Electrical isolation and wiring acceptance
1. Photograph both boards and record exact carrier silkscreen, schematic revision, pin headers, firmware provenance, USB-UART bridge part and power requirements. Do **not** infer carrier pinout from ESP32 chip/module name.
2. Keep S2 and WROOM powered and programmed **independently** during initial verification. No shared 5 V rails, no competing USB and external 3.3 V supplies, no output-to-output pin ties. A shared ground is required only for an intentional wired signal link.
3. Verify UART **logic levels** are 3.3 V on both sides. USB adapter power-output voltage and UART I/O voltage can differ; an adapter labeled “3.3V/5V” is not sufficient proof.
4. Do not drive ESP32 EN/GPIO0 from the Flipper or Pi until GPIO polarity, pullups, boot strapping, and power domains are verified on the *exact* board. Avoid Flipper 5 V GPIO power output as a default ESP32 supply.
5. Separate S2's native USB/USB-serial-JTAG or CDC setup (firmware dependent) from WROOM's external USB-UART bridge; **never** use one chip's esptool target for the other.
6. If multiple ports exist, enumerate USB VID/PID, physical connection, by-id symlink and adapter markings. Never automatically select /dev/ttyUSB0 or /dev/ttyACM0, or scan arbitrary ports.
7. Preserve an explicit disconnect/rollback plan: remove added wiring and power, leave the owner's currently working S2 FlipperHTTP installation untouched, and restore stock Momentum functionality.

## Transport/protocol coexistence gates
- The v0.8 FAP proposal uses a secondary Flipper USART UART for S2 FlipperHTTP ping/status and keeps the legacy custom LPUART separate. This is a **source proposal**, not evidence that both serial peripherals work concurrently on real hardware.
- Only send fixed, nonsecret board-health commands after local owner approval and pin verification. **Do not send AI prompts, tokens, URLs with credentials or API keys** to FlipperHTTP until firmware TLS verification is proven; the reviewed upstream implementation reportedly contains a `setInsecure()` fallback.
- The WROOM must not claim or intercept the S2 UART pins. Use an explicitly chosen standalone Pi USB-UART path for initial WROOM diagnostics.
- BLE/Wi-Fi/USB-C transport arbitration, radio listening, Arduino sensor expansion and shared backpack power remain **future** gates, not implemented features.

## Public-safe offline test cases for future automation
- WROOM plan mistakenly declares S2 native USB flash mode => reject.
- S2 plan mistakenly requests ESP32-WROOM bootloader target => reject.
- Two peripherals claim the same Flipper UART pins => reject.
- Unverified adapter UART logic voltage or mixed power domains => reject.
- Serial port exists but has no user-confirmed physical board identity => reject.
- FlipperHTTP AI prompt transfer requested before TLS/certificate verification => reject.
- Board health/status command with no secrets, confirmed board, pins and owner consent => permit **planning only**, not execution.

## Integration handoff / release ledger
Source dependency: integration-testing PR #357, Momentum FAP PR #84 / CI PR #86; Phase 1 Momentum PR #23 and integration-testing PR #23. This document does not modify those branches. No tests, physical devices, APK, updater TGZ, CI permissions, or release ledger are changed by this document.

**Do not promote** until exact-head CI evidence, independent hardware pin/voltage validation, verified AI1 contract, owner-operated physical smoke tests, and integration-testing ledger owner acceptance. Preserve known CRC 9-99 updater quarantine, Android signing protection, and two-consecutive-failure PUBLIC-SAFE fallback; private Actions 403 is BLOCKED, not evidence of a code failure.
