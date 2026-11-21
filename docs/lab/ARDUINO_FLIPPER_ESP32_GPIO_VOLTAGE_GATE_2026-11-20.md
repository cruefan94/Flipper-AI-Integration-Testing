# Arduino Uno ↔ Flipper Zero / ESP32 GPIO electrical acceptance gate

Status: LAB ONLY · documentation/fixture · not validated on owner's hardware · 2026-11-20

## Purpose
Prevent a 5 V Arduino Uno GPIO output from being directly connected to a Flipper Zero or ESP32 3.3 V input during backpack-module prototyping. **No automatic flashing, GPIO toggling, or device commands.** A common ground does not make signal voltages compatible.

## Fail-closed interface matrix (conservative)
| Source → destination | Default lab decision | Evidence needed to change |
|---|---|---|
| Uno 5 V digital output → ESP32-WROOM GPIO | BLOCK direct connection | Suitable rated level shifter or proven voltage divider for one-way slow logic; verified board pinout |
| Uno 5 V digital output → ESP32-S2 GPIO | BLOCK direct connection | Same, independently confirmed S2 pinout |
| Uno 5 V digital output → Flipper GPIO input | BLOCK direct connection | Proper 5 V→3.3 V translation and Flipper documentation |
| Flipper/ESP32 3.3 V output → Uno 5 V input | REVIEW, not automatically safe | Uno input-high specification, actual logic threshold, common ground, pin mode, no pull-up to 5 V |
| Uno 5 V I²C pull-ups → ESP32/Flipper I²C | BLOCK | Bidirectional level shifter with verified pull-ups on each voltage rail |
| Uno 5 V power rail → Flipper/ESP32 3.3 V pin | BLOCK | Never use as substitute for a regulated 3.3 V supply |
| USB-powered boards with cross-connected 5 V/VBUS | BLOCK pending review | Power-source isolation/backfeed analysis |
| Any unknown module signal → any GPIO | BLOCK | Datasheet, measured voltage, direction, current, and safe pin assignment |

## Bench acceptance procedure (owner operated; no remote control)
1. Disconnect all power and USB before rewiring. Identify exact board revisions, module pinouts, and whether pins are input, output, analog or open-drain.
2. Record supply rail, idle voltage, worst-case high voltage, pull-up source, current limits and whether the module is powered when its controller is off. Do not guess from wire colors.
3. Confirm shared signal reference (GND) only where the documented power architecture permits it. Never connect two supply outputs together.
4. For 5 V→3.3 V digital lines, choose a suitable direction-aware level shifter; a properly calculated divider may be suitable only for slow **unidirectional** push-pull signals. Dividers are not a general solution for I²C, bidirectional buses, high-speed signals or power rails.
5. Check Flipper GPIO 3.3 V tolerance and power limits against official documentation. Verify ESP32 pin strapping, flash pins and boot modes before assigning GPIO; avoid boot-critical pins until reviewed.
6. Confirm that USB ports, Pi power, battery supplies and module regulators cannot backfeed one another. Add protection appropriate to the finalized design.
7. Measure idle and active signal voltages with a meter on the owner's bench before any powered interconnection. Stop if any reading or schematic is uncertain.
8. Only after explicit owner approval, proceed to separately supervised functional tests; do not treat this document as flash authorization.

## Public-safe fixture examples
```json
[
  {"source":"uno_digital_out_5v","destination":"esp32_wroom_gpio","direct_wire":true,"expected":"BLOCK"},
  {"source":"uno_i2c_5v_pullup","destination":"flipper_gpio","direct_wire":true,"expected":"BLOCK"},
  {"source":"esp32_s2_gpio_3v3","destination":"uno_input","direct_wire":true,"expected":"REVIEW"},
  {"source":"unknown_module","destination":"flipper_gpio","direct_wire":true,"expected":"BLOCK"}
]
```

## Release gate / handoff
This is a conservative documentation fixture, **not** a tested circuit or an integrated peripheral. Before promotion, require exact board revision, official pin specifications, wiring schematic, owner measurements, independent safety review, and dedicated synthetic checks. Remain optional to Android AI Satellite APK and native Momentum F7 updater; no release-ledger edits here. Preserve two-failure CI fallback and private Actions:read BLOCKED reporting. Do not retry the failed CRC 9-99 F7 updater or replace the installed Android APK. Receive-only radio only; Civic integration deferred.
