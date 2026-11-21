# ESP32-WROOM and ESP32-S2 coexistence: board review gate

Status: LAB ONLY / NOT APPROVED FOR WIRING OR FLASHING. Parent: PR #286, commit ad31b96ba392c244fcca836cc559176b93e22ac9. Parent exact-head public CI: 44894274760 (success), public smoke: 44894274778 (success). These are synthetic checks, not physical verification.

## Hardware-family facts and limits
- Classic ESP32-WROOM-32 module supports 2.4 GHz Wi-Fi and Bluetooth (Classic/BLE), but specific breakout board power, strapping and USB-UART connections vary.
- ESP32-S2 supports 2.4 GHz Wi-Fi and native USB OTG; **it does not have Bluetooth/BLE**. Do not advertise S2 as a BLE bridge.
- ESP32-S2 USB download/boot entry and classic ESP32 UART0 boot strapping are not interchangeable procedures. Identify exact module, board revision and USB-to-UART bridge first.
- GPIO signal domains are 3.3 V; do not connect 5 V Arduino Uno output directly. Review bidirectional level shifters for I2C and the actual pull-up rail. Do not join 5 V and 3.3 V power rails.
- Both boards may coexist as independent USB peripherals on a Pi 4B if supply/current budget and cable/port identity are verified. No assumption that either board can power the other or Flipper Zero.
- Flipper GPIO is 3.3 V logic; validate pinouts and common ground before UART; TX->RX and RX->TX only after checking direction and voltages. Avoid Flipper 5 V supply assumptions.

## Pi 4B read-only operator checklist
1. Disconnect external GPIO wiring. Power only one ESP board at a time via its own appropriate USB path.
2. Record board silkscreen, chip/module marking, USB connector, regulator marking, and serial adapter ID; do not publish serial numbers.
3. On Pi, use `lsusb`, `ls -l /dev/serial/by-id/` and `dmesg --ctime | tail -n 30` to identify enumeration. These are observational commands; do not run esptool write/erase.
4. If enumeration is missing, check cable data support, port power, USB hub and permissions before attempting EN/BOOT changes.
5. For classic WROOM, document EN and GPIO0 state at reset, plus observed ROM serial text; for S2 document its own documented BOOT/RESET/USB procedure. Do not infer a successful download mode from button sequence alone.
6. If both boards enumerate independently, record only redacted VID:PID and logical device paths; never hard-code `/dev/ttyUSB0` as stable identity.
7. Before any future flashing, require owner consent, known firmware provenance, backup/recovery procedure, verified chip identity, stable power and explicit dry-run confirmation.

## Acceptance gates
- Offline coexistence checker passes exact-head CI.
- Independent board-specific documentation reviewed against official Espressif datasheets and exact devboard schematics.
- Pi USB read-only enumeration observed by owner for each board.
- Power and GPIO wiring independently reviewed and measured.
- No shared-release-ledger mutation or APK/F7 candidate promotion without integration-testing owner approval.

## Deferred
Flipper-initiated ESP flashing, simultaneous powered backpack wiring, radio transmission, remote physical control, Android APK integration, Momentum F7 updater integration and 2021 Civic integration.
