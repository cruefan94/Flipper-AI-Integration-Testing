# Unified Flipper AI Momentum + Android Satellite + ESP32 — Release Gates

**Status: integration development, not flash-approved.**
Firmware integration source `5501cb9b9205a87bec79e7810103a4757a8bb665`.
Android BLE candidate `c8ba436e19b7a78f05a3e7b12b77cfc3dc258a91`.
ESP32 source baseline `047257b2961ceb5c5ac5941230c0b7af617e5723`.

## Passed source-level gates (2026-11-15)

- Pinned private transport policy and ESP32 integration host C11/UBSan and Python tests: [run 43753033992](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43753033992).
- Pinned cross-repository Android GATT UUID, characteristic authentication and AI1 HELLO/ASK host tests: same run.
- Android BLE duplicate-GATT-callback candidate compiled and passed host tests: [run 43744065165](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/43744065165).

## Compilation gates (check live, never infer success)

- [Unified Momentum + ESP32 native build workflow](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43753113437): required to finish all steps before calling firmware/package compiled.
- Confirm exact pinned upstream Momentum F7 build includes the Flipper AI app, FZ1 ESP32 Manager and existing stock Momentum apps; verify .tgz and FAP inventories.
- GPL-3 ESP programmer FAP remains separately installed and independently licensed; never claim the AI app itself can directly erase/write the board.
- Encrypted-only artifacts, SHA/manifest and decrypt verification; no plaintext private Momentum source or firmware distributed through public artifacts.

## Hardware gates: NOT YET VERIFIED

1. Back up the known-working Flipper Momentum firmware and app configuration and make sure normal recovery / qFlipper works. Do not silently replace it.
2. On the **exact installed F7 firmware** verify all Momentum stock features still launch, including Bluetooth RPC, NFC/RFID, IR, Sub-GHz, applications, themes and dolphin; do not assume CI compilation proves functional parity.
3. On a paired Android phone verify dedicated authenticated AI GATT, CCCD, AI1 HELLO/ASK, MTU negotiation, reconnect after toggling Bluetooth, and explicit manual disconnect prevents unwanted reconnection. Stock RPC alone is **not** AI1 readiness.
4. Test Android OFFLINE, ONLINE opt-in and HYBRID fallback separately and verify no cloud request on explicit offline or when consent revoked.
5. Verify Android `applicationId`, monotonic `versionCode` and **identical signing certificate** to currently installed app before claiming an in-place APK update. CI currently reported no stable signing. Do not instruct uninstall before backups.
6. Identify ESP-WROOM-32 board family, actual flash capacity, USB-UART conflict, bootloader BOOT/EN behaviour, stable 3.3V UART and shared ground. Read-only FZ1 INFO/CAPS/STATUS/passive Wi-Fi scan first. For classic WROOM board, Flipper TX15/RX16 ↔ ESP UART2 RX16/TX17 **only with verified actual board labels/pin map**; programming UART0 is separate. Never connect Uno 5V TX to Flipper input.
7. For ESP Flasher require explicit user confirmation, correct flash offsets, firmware target, SHA256/MD5 readback, independent USB supply and recovery image. Never auto-erase.
8. Automatic transport switching **not yet implemented**: the integrated policy observes trusted BLE only. Home Wi-Fi, hotspot and USB adapters are pending, and no in-flight request handoff is claimed.

## Promotion rule

Only promote source to main after compile, API/ABI checks, reproducible encrypted package, hardware regression and explicit user decision. Track failures by commit, workflow run and hardware model, not estimated completion percentage.
