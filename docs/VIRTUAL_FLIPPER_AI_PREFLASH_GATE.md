# Virtual Flipper AI preflash gate

This is a **host-side simulator and protocol test gate**, NOT an emulator of Flipper Zero MCU, BLE radio, bootloader, or flashing.

## Purpose
- Verify AI1 framing and state transitions against synthetic BLE traffic.
- Exercise disconnect, stale response, replay, malformed payload, and authorization cases.
- Run Android-side transport contract tests in CI.
- Verify the updater package structure, SHA256 manifest and encryption roundtrip in the firmware workflow.
- Require manual hardware verification for boot, BLE GATT, SD storage and recovery.

## Release gates
1. Private overlay unit tests pass.
2. Public host protocol tests pass.
3. Full Momentum firmware compiles using pinned upstream source.
4. Updater directory includes DFU image; hashes and encrypted archive roundtrip pass.
5. Android APK builds and contract tests pass.
6. **Physical flash remains BLOCKED** until SD backup and a recovery path are available. A working official mobile app does not replace qFlipper recovery.

## Virtual test limitations
No claim of complete Flipper emulation, accurate power draw, hardware BLE radio behavior, bootloader compatibility or guaranteed safe flashing. A passing CI run is a build-quality gate only.

## User baseline
Current installed Momentum: mntm-012, 2025-12-31, commit e1784e74 (photo reported). Official Flipper Mobile App pairs over Bluetooth. User currently has no computer for recovery.

## Current verified artifact
Run https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43544527859
Encrypted artifact 14092829927 expires 2026-11-21 UTC. Do not publish passphrase.
