# Flipper / ESP32 portable backpack: power-isolation acceptance contract

Status: **LAB-ONLY / NOT ELECTRICALLY VERIFIED**. 2026-11-18. No device control or flashing.

## Scope and architecture
- Keep ESP32-WROOM UART development module and ESP32-S2 Wi-Fi devboard as **separate** independently addressable peripherals. Do not tie their USB power rails or TX outputs together.
- Use a **single defined supply path per board**. The Pi 4B, Flipper Zero, USB power bank and ESP32 devboard USB ports must not be connected as competing power sources through a shared 5V net.
- Connect grounds only after the specific board power topology and isolation arrangement have been reviewed. A shared logic reference is normally required for wired UART, but must not create a power-return bypass.
- No pin-number assumptions: ESP32 module pinout, devboard USB-UART circuit, boot strapping, regulator limits, Flipper GPIO voltage/current limits and Arduino Uno revision must be checked against actual board schematics before wiring.
- ESP32 and Flipper GPIO are **3.3V domains**. Never directly drive them from Arduino Uno 5V GPIO. Select a level translator with verified direction and voltage thresholds.
- Do not power attached sensors or ESP32 modules from an unverified Flipper 3.3V pin budget. Record startup/peak current, regulator headroom and battery/USB protection before a portable assembly.
- Add inline overcurrent protection on external supply paths as appropriate to the chosen regulator, wiring gauge and enclosure; verify polarity and connector keying.
- Never join two push-pull outputs (Flipper TX, Pi TX, Arduino TX, ESP32 TX). For multi-board communications use isolated ports, explicit muxing or a bus topology designed for multiple nodes.

## Pre-power checklist (all required)
| Gate | Evidence required | If missing |
| --- | --- | --- |
| Board identity | Photographs, exact part/revision, schematics | BLOCK |
| Supply topology | Drawing identifying one supply source per rail, no backfeed paths | BLOCK |
| Voltage compatibility | Measured idle rail voltage and verified GPIO maximum ratings | BLOCK |
| Current budget | Sensor/board startup and peak estimates with regulator margins | BLOCK |
| UART direction | TX-to-RX only, correct logic-level translation, common reference | BLOCK |
| Boot controls | Board-specific EN/BOOT circuitry, no permanent strap forcing | BLOCK |
| USB coexistence | No competing USB-host/5V sourcing; separate WROOM and S2 interfaces | BLOCK |
| Mechanical | Strain relief, insulated pins, accessible power disconnect | BLOCK |
| Owner consent | Explicit approval before energizing or programming hardware | BLOCK |

## Suggested modular harness
- **Power module:** protected USB battery supply, board-appropriate regulator and disconnect switch; do not assume Flipper can supply the ESP32.
- **Logic module:** removable UART connector with ground, TX, RX, optional EN/BOOT through verified open-drain or transistor interface; no direct 5V GPIO.
- **Sensor module:** removable 3.3V I2C or UART sensor daughterboard with board-specific pull-ups; Arduino Uno requires verified level conversion.
- **ESP32-S2 module:** its own power and data harness, not a parallel connection to WROOM UART.
- **Radio module:** receive-only SDR on an authorized Pi/Android USB host, or lawful internet streams. No transmitter or interception functions.

## Integration gate
This is a **wiring review checklist**, not an approved schematic or bill of materials. Do not promote to Android APK or Momentum F7 .tgz candidate until board identities, electrical measurements, firmware/transport contracts, passing exact-commit CI, and owner-run physical tests are recorded. Preserve private Phase 1 PR #23, public-safe failover PR #23, two-consecutive-failure CI policy, Android signing protection and CRC 9-99 updater quarantine. Civic integration remains deferred.

## Next lab action
Obtain board-specific schematics and produce a reviewed pin-to-pin harness diagram plus power budget with actual component ratings. No physical operations in this document.
