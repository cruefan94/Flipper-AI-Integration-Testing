# Portable Flipper / Pi / ESP32 / Arduino power-isolation acceptance checklist

Status: LAB DOCUMENT ONLY; not an approved wiring diagram, verified hardware profile, or permission to energize hardware. Scope: portable cigar-box/backpack concept. No firmware, radio transmission, remote device access or production release changes.

## Mandatory pre-power inventory (record actual label/datasheet readings)
| Module | Power input / source | GPIO logic | Risk to resolve |
| --- | --- | --- | --- |
| Raspberry Pi 4B | Dedicated regulated USB-C 5 V supply; check official recommended current for attached peripherals | 3.3 V, **not 5 V tolerant** | USB power backfeed, brownout, shared-ground noise |
| Flipper Zero | Own supported USB/battery input; do not inject unverified 5 V into GPIO | 3.3 V GPIO; confirm exact pin/function against official docs | Backfeeding through GPIO, power switching |
| ESP32-WROOM devboard | Verify devboard USB/VIN regulator, not bare module power assumptions | 3.3 V GPIO | 5 V UART, EN/BOOT strap interference |
| ESP32-S2 devboard | Verify exact S2 board revision, native USB connector and power circuit | 3.3 V GPIO | USB host/device and VBUS conflicts |
| Arduino Uno | Confirm exact board revision, USB/VIN path and I/O voltage | Typically 5 V I/O on classic Uno | Direct Uno output to 3.3 V input is unsafe |
| Portable HDMI/audio display | Separate documented USB-C input unless manufacturer allows shared supply | Not a GPIO peripheral | Startup surge, ground-loop audio noise |

## Fail-closed wiring gates
1. **Identify exact boards and regulators** from photographs and manufacturer schematics. Generic module labels do not establish safe input limits.
2. **No shared positive power rails by default.** Keep Pi, Flipper, ESP32, Arduino and screen on independent known-good supplies for first validation. Never parallel USB power outputs or tie USB VBUS to GPIO power.
3. **Common ground only when required by a planned signal link**, after confirming isolation and no incompatible supply reference. Disconnect power before changing wiring.
4. **No direct 5 V Arduino digital output to Pi, ESP32 or Flipper GPIO.** Use a verified level-shifter/divider appropriate to signal speed and direction. I2C pull-ups must be reviewed separately on both sides of any translator.
5. **Power budget:** measure/obtain peak load for every rail including screen, USB peripherals, audio amplifier, radio receiver and conversion losses. Use the offline budget checker as a rejection aid, never as electrical approval. Derating is not a substitute for cable, fuse or thermal ratings.
6. **Protection:** use individually fused/current-limited outputs as appropriate; check polarity, wire gauge, connector current ratings, strain relief, enclosure ventilation, and accessible power-off. Do not enclose unprotected loose lithium cells.
7. **Boot/programming:** ESP32 EN/GPIO0 wiring must not be driven from 5 V. Do not connect Pi/Flipper programming lines until board-specific strap and USB-serial circuitry is confirmed.
8. **Receive-only radio:** USB SDR and lawful online feeds only; no transmit-capable GPIO control, interception or rebroadcast.
9. **Acceptance evidence:** capture supply labels, exact board models, isolated current readings, meter-verified voltage at idle and peak, and thermal observations. Never record private tokens, personal radio traffic or hardware identifiers in public CI.
10. **Release gate:** physical validation plus compatibility/protocol tests and exact-commit passing CI are required before any peripheral promotion into unified APK or F7 updater candidates. Production builds remain untouched.

## Safe offline review fixture
Example proposed load budget (illustrative only, **not measured hardware**): Pi 5 V × 3 A = 15 W; display 5 V × 2 A = 10 W; other peripherals 5 V × 1 A = 5 W. Combined illustrative peak = 30 W, before converter losses. At a 25% capacity reserve, a hypothetical supply would need at least 40 W nominal capacity **at the appropriate independently regulated outputs**. This does not imply a single 5 V rail or USB hub is acceptable.

## Outstanding manufacturer evidence
Exact WROOM and S2 board revision schematics; Uno revision; Pi power supply and USB-C cabling; Flipper GPIO/power docs; display power label; amplifier load; battery or power-bank protection specification. Mark physical wiring **BLOCKED** until these are known.

## Cross-workstream gates
Phase 1 firmware blockers: private Momentum PR #23; public-safe Actions coverage: Integration-Testing PR #23. Private Actions:read 403 remains BLOCKED until access is verified. Two consecutive failed completed attempts (or repeated pre-job failure) must route through approved public-safe fallback without disclosing private firmware. Quarantine DFU CRC 9-99 updater; preserve installed Android signing and data. No vehicle integration.
