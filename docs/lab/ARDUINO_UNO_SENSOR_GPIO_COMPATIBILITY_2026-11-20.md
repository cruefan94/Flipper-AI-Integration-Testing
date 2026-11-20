# Arduino Uno R3 ↔ ESP32 / Pi / Flipper: isolated sensor-wiring review matrix
Date: 2026-11-20. Status: DOCUMENTATION / REVIEW ONLY. No verified physical wiring, no automatic pin configuration, no flash authorization.

## Scope and assumptions
Assumes a conventional **5 V ATmega328P Arduino Uno R3**, ESP32-WROOM-32-class 3.3 V GPIO, ESP32-S2 3.3 V GPIO, Raspberry Pi 4B 3.3 V GPIO, and Flipper Zero 3.3 V GPIO. **Do not apply blindly to Uno R4, Uno clones, or unknown ESP32 devboards.** Confirm exact PCB revision, pinout, onboard pull-ups, power regulator, peripheral module operating voltage, and common ground before connecting anything.

| Signal / module | Uno R3 side | ESP32-WROOM / ESP32-S2 / Pi 4B / Flipper side | Review gate |
| --- | --- | --- | --- |
| Digital output / push-pull UART TX | 5 V HIGH possible | 3.3 V GPIO; not generally 5 V tolerant | **BLOCK direct connection.** Use a properly specified level translator or divider for one-way UART TX; check speed and logic margins |
| Digital input / UART RX | 5 V-domain input | 3.3 V HIGH from peripheral | **REVIEW** input-high threshold of exact ATmega/board and supply; do not assume a 3.3 V HIGH is reliable at 5 V VCC |
| I2C SDA/SCL | May have pull-ups to 5 V | 3.3 V bus | **BLOCK** until every pull-up rail is identified; use appropriate bidirectional I2C level shifting and bus voltage review |
| SPI MOSI / SCK / CS (Uno master) | 5 V outputs | 3.3 V inputs | **BLOCK** direct connection; level-shift each Uno-driven line |
| SPI MISO (3.3 V slave) | Uno input | 3.3 V output | **REVIEW** Uno VIH, timing and device data sheets; level-shift if uncertain |
| Analog sensor output | May swing 0–5 V | ESP32 ADC / Pi GPIO / Flipper GPIO are not 5 V analog inputs | **BLOCK** direct 5 V sensor output; use suitable divider/buffer and ADC-compatible range. Pi GPIO has no built-in general-purpose analog ADC |
| Passive dry-contact switch | Pull-up selection determines voltage | 3.3 V GPIO input | **REVIEW** pull-up to local 3.3 V rail only, debounce, and isolation of any external supply |
| HC-SR04-class ultrasonic echo | Common 5 V echo | 3.3 V input | **BLOCK** direct echo; use suitable level shift/divider; confirm module variant |
| DHT-style sensor module | Depends on sensor/module pull-up | 3.3 V input | **REVIEW** module voltage and pull-up; a module powered at 5 V can pull data high to 5 V |
| Servo / motor / relay module | High current or inductive load | GPIO only for logic | **BLOCK** direct GPIO power. Use driver, flyback protection where applicable, independent rated supply and shared reference/isolation as designed |
| Board power rails | USB / 5 V / 3.3 V | Different regulators and power domains | **BLOCK** backfeeding, connecting two powered 5 V rails, or feeding 5 V to 3.3 V pins; power budget required |

## ESP32 boot and shared GPIO
- ESP32-WROOM (classic ESP32): GPIO0 low at reset selects ROM download mode; EN/CHIP_PU reset behavior depends on the board's circuitry. Do not tie boot straps to external sensors without checking the exact board.
- ESP32-S2: boot and USB interface differ from classic ESP32; confirm the board's native USB vs USB-UART path and strap pins from its schematic. Do not presume a WROOM flash sequence or UART port name works.
- No generic pin mapping is authorized here. ESP32 GPIOs have board-specific boot/flash restrictions; Pi/Flipper headers also require exact pinout review.

## Portable backpack power and safety
- Use separate, clearly labeled connectors for 3.3 V logic, 5 V modules, and ground; key or color-code connectors to reduce reversal risk.
- Keep an inline fuse/current limit appropriate to the selected battery/power supply; do not derive it from this document.
- Keep ESP32, Pi, Flipper and Arduino USB power domains isolated from accidental backfeed; validate grounds and voltage with a multimeter before connecting signal wires.
- Do not repurpose salvaged antennas as transmitters or assume antenna compatibility. Receive-only radio and public lawful online feeds remain separate from GPIO work.

## Acceptance before integration
1. Identify exact board revision and sensor module datasheet; attach manufacturer URLs and confirmed electrical ratings.
2. Produce an annotated per-pin wiring schematic with direction, rail, translation, current limits and protection.
3. Run offline fixture-based voltage checker tests against that schematic; passing synthetic tests is insufficient.
4. With owner present, measure unconnected supply rails and powered idle signal levels using a multimeter before joining boards; no remote device operation.
5. Record consent, observations, and any failed tests. Promote to unified release ledger only with exact commit, passing CI and proven cross-device contract.

## Integration handoff
Optional external hardware document only; **not integrated** into Android AI Satellite APK or native F7 Momentum updater .tgz. No AI1 BLE contract change. No production branch merge, radio transmission, hardware flash or installation. Follow two-consecutive-failure CI fallback; private Actions:read HTTP 403 means fallback coverage must be marked BLOCKED, not silently passed. Never retry quarantined CRC 9-99 updater. Android signing mismatch prohibits replacing installed app. Civic integration deferred.
