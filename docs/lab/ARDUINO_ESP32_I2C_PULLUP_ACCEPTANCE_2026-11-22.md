# Arduino Uno ↔ ESP32 / Flipper I²C sensor admission gate (PUBLIC-SAFE)

Status: **documentation-only lab proposal**; no owner hardware was inspected, connected, powered or flashed. Builds on the isolated GPIO preflight in draft PR #373; does **not** supersede it or certify wiring.

## Critical electrical distinction

An Arduino Uno R3 normally uses **5 V** GPIO. ESP32 and Flipper GPIO are **3.3 V-domain** and must not receive 5 V signals. I²C SDA/SCL are open-drain lines: their **pull-up voltage**, including pull-ups hidden on a sensor breakout, determines the high level. Supplying a breakout from 3.3 V does not by itself prove its SDA/SCL are safe. A 5 V Uno and a 3.3 V ESP32 must not share SDA/SCL directly unless the entire bus electrical design has been verified safe for *every* attached device. Use an appropriately rated bidirectional I²C level translator when required; do not assume an arbitrary resistor divider works for bidirectional I²C.

## Before accepting a modular sensor

1. Record exact Uno revision, ESP32 module/board variant, Flipper pin interface, sensor breakout manufacturer/revision and datasheet URLs.
2. Confirm the breakout's VCC input range, I/O voltage limits, any onboard regulator, and **all SDA/SCL pull-up resistor destinations** using schematic or measurements with power disconnected where applicable.
3. Document which board supplies each rail; reject back-powering through GPIO, simultaneous USB/external supply conflicts and any unknown rail connection.
4. Record the common ground and verify that SDA/SCL are not shorted to supply or ground before power-up.
5. Specify bus voltage on **both** sides of any level translator, its OE/EN behavior, and whether pull-ups exist on both sides.
6. Confirm the I²C device address from its documentation; do not treat an address scan as proof of electrical safety.
7. Confirm bus topology, total pull-up resistance, cable length and bus speed are compatible with all connected devices.
8. Permit only owner-operated read-only identification first; defer output actuation, flash, relay, motors, radio transmission and remote control until separate acceptance.
9. Do not use Flipper GPIO power output as a default sensor supply; establish current budget, polarity, connector orientation and protective fuse/current limiting.
10. Log photos/schematics and an explicit owner sign-off **privately**. Public test fixtures must use synthetic board names, values and no identifying serial numbers.

## Fail-closed synthetic fixture matrix

| Fixture | Expected |
| --- | --- |
| Uno 5 V SDA/SCL directly connected to ESP32 3.3 V bus | REJECT |
| Unknown breakout pull-up voltage | REJECT |
| Breakout pull-ups tied to 5 V, ESP32 bus unshifted | REJECT |
| Missing common-ground evidence | REJECT |
| Translator direction or power domains undocumented | REJECT |
| Two competing power sources without isolation proof | REJECT |
| Address scan proposed as first electrical test | REJECT |
| Verified 3.3 V-only bus, board-specific evidence, no Uno 5 V connection | ELIGIBLE FOR OWNER REVIEW, not hardware-approved |
| Verified rated bidirectional translator, 5 V Uno side and 3.3 V ESP32 side | ELIGIBLE FOR OWNER REVIEW, not hardware-approved |

## Integration gate

This document is **not** evidence of passing code CI, real board electrical compatibility, AI1 BLE contract compatibility or a releasable peripheral. Keep it outside the unified Android APK and Momentum F7 updater candidate until exact board verification, isolated tests, owner-operated hardware acceptance and integration-ledger review. Preserve CRC 9-99 updater quarantine, APK signing protections and the two-failure public-safe fallback; report private Actions HTTP 403 as BLOCKED rather than inferring billing.

Next implementation: add isolated parser-level I²C pull-up evidence fields and fail-closed synthetic tests to the lab validator without modifying its production-facing interfaces.
