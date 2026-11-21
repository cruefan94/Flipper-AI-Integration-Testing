# Arduino Uno / ESP32 I2C voltage gate — verified CI handoff (2026-11-21)

## Exact source and verification
- Parent draft PR: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/321
- Source commit: `7b1e2f00979e56e9b345a06cc2053d27e051692a`
- Dedicated offline regression: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44956586494 — completed SUCCESS
- Public runner/contract smoke: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44956586511 — completed SUCCESS
- These are synthetic tests, not schematic validation, physical voltage measurements or end-to-end compatibility.

## Conservative owner-operated acceptance gate
1. Record exact board and module revisions, supply rails and whether the sensor is 3.3V-only or 5V-tolerant; do not assume a breakout's onboard regulator level-shifts SDA/SCL.
2. With all boards unpowered, identify each SDA/SCL pull-up resistor and its supply rail from schematics or measurement. Multiple pull-ups may operate in parallel and reduce effective resistance.
3. Confirm a common reference ground, isolation of independently powered rails, and that no 5V pull-up can reach a non-5V-tolerant ESP32 GPIO. Use an appropriate bidirectional level shifter if required.
4. Do not connect the Arduino Uno's 5V logic directly to ESP32 input pins. Avoid powering modules through GPIO. Verify I2C bus voltage before connecting the ESP32.
5. Run the offline wiring-manifest checker against a board-specific plan, review the output, then request explicit owner approval before any powered hardware acceptance. No remote commands or flash actions are authorized.

## Release integration handoff
- Workstream: optional external Arduino/ESP32 sensor adapter; no AI1/BLE protocol change claimed.
- Android APK: NOT integrated. F7 Momentum updater TGZ: NOT integrated.
- Promotion blockers: schematic-specific voltage-domain validation; physical owner test; exact dependency/commit review by integration-testing release owner; cross-component contract tests if any API is introduced.
- Preserve private Momentum Phase 1 PR #23 and public integration-testing PR #23; two-consecutive-failure fallback; private Actions:read 403 BLOCKED until verified otherwise.
- Never retry the failed CRC 9-99 updater; never replace/uninstall the existing signed Android app; no protected merge, flashing, radio transmission, or production deployment.
