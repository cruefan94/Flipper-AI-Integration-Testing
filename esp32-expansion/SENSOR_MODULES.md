# Arduino-compatible sensors for Flipper AI ESP32 Expansion

## Status and preloading boundary

This project has **built-in, read-only ESP32 firmware profiles**, a Flipper Sensor menu and CI-produced binary candidates. The same ESP32 program supports these accessories without recompiling for each attached sensor. Physical sensors are **not automatically detected except BME280/I2C addresses**, and no accuracy or device operation has been verified.

**Not included in the owner's installed custom Momentum updater yet.** Candidate SD-card bundle is for review and later main installer integration, not an automatic firmware update. Do not treat an official SDK FAP as proven Momentum compatible.

The owner's photos confirm a classic **ESP-WROOM-32 38-pin development board**, USB-C, BOOT/RST buttons and a screw-terminal breakout adapter. The other board is an **Arduino Uno R3-compatible controller**. The photos do not show individual sensors.

## Precompiled component profiles and safe wiring

| Flipper Sensor Manager action | ESP32 screw terminal | Example component | Safety |
| --- | --- | --- | --- |
| Analog reading P34 | P34 / GPIO34 | 3.3V LDR divider / analog potentiometer | GPIO34 input only; maximum 3.3V signal; value is 12-bit raw ADC, not calibrated voltage/lux |
| Digital input P27 | P27 / GPIO27 | 3.3V button or PIR motion sensor | Internal pull-up; input reports raw 0 or 1, not a verified motion state |
| I2C module scan | P21 / SDA, P22 / SCL | BME280, I2C display or sensor module | I2C requires 3.3V power and safe pull-ups to 3.3V; a scan detects addresses only |
| BME280 readings | P21 / SDA, P22 / SCL | BME280 pressure, temperature and humidity sensor | Compatible 3.3V I2C BME280 at 0x76 or 0x77; reports missing if not found |
| DHT22 readings | P25 / GPIO25 | DHT22 temperature and humidity sensor | Use appropriate data pull-up and 3.3V-compatible supply; DHT11 is not identical |

**Do not connect Arduino Uno 5V UART or GPIO directly to Flipper or ESP32 3.3V pins.** Use appropriate level shifting or only 3.3V-compatible devices. Never supply >3.3V to the ESP32 ADC; do not wire 5V HC-SR04 echo pins or motors/relays directly. Identify the exact module's voltage requirements before connecting.

The Uno is optional for this version. Its existing Arduino sketch, if any, will not automatically become executable on the Flipper. A future safe UART/I2C bridge can integrate Uno-hosted components using a separate Arduino program.

## Flipper-to-ESP32 UART

For normal sensor operation: Flipper pin 15 TX -> ESP32 GPIO16 RX2; Flipper pin 16 RX <- ESP32 GPIO17 TX2; common ground. Power ESP32 independently through USB-C for the bench test, never by joining Flipper and ESP32 5V/3V3 rails without a verified power design.

The third-party ESP Flasher uses Flipper USART 13/14 to ESP32 RX0/TX0 for programming. Its connection can conflict with an ESP32 DevKit's onboard USB-UART circuitry; verify board details and use only one app/UART connection at a time.

## Fixed read-only UART protocol

Commands are newline-terminated, ASCII, max 95 bytes, 115200 8N1:

- FZ1|SENSORS lists supported profiles; BME280 detection status
- FZ1|SENSOR|ADC34 reads raw 12-bit ADC
- FZ1|SENSOR|GPIO27 reads logic level
- FZ1|SENSOR|I2C_SCAN lists up to twelve discovered I2C addresses
- FZ1|SENSOR|BME280 reads Celsius, relative humidity and pressure in pascals
- FZ1|SENSOR|DHT22 reads Celsius and relative humidity or reports sensor unavailable

The ESP32 always terminates supported responses with FZ1|END. Unsupported operations including arbitrary pin writes are rejected.

## Install packages planned for the main Momentum build

- A Flipper ESP32 Manager FAP compiled against the **matching Momentum SDK**, distributed with the main firmware's SD-card apps.
- A matching ESP32 firmware package compiled for the **confirmed ESP-WROOM-32 variant**, containing board image, partition information and a manifest.
- Sensor profiles built into ESP32 firmware rather than individually downloaded applications.
- A future firmware updater that can install the app and support **user-approved** board flashes; never auto-flash simply because an ESP32 is connected.

Current public CI uses the official Flipper SDK and reference esp32dev PlatformIO target. A candidate artifact or compiled image does not prove compatibility with the owner's device. Do not install production firmware until the correct binary layout, board revisions and recovery path are confirmed.

## Future additions

HC-SR04 (with 5V echo divider), DS18B20, DHT11, OLED display drivers, buttons, LEDs, motors/servos using external drivers, radio receivers and AI audio. Implement each as a bounded capability and maintain explicit consent for hardware outputs.
