# v47 public native protocol testing checkpoint

Date: 2026-11-12.

Source: `cruefan94/Flipper-AI-Momentum-` branch `fix/ai-client-zero-id-state-v46`.
Destination: `cruefan94/Flipper-AI-Integration-Testing` branch `test/ai-native-v47`.

Nine exact source/header/test files copied into `snapshot/v46/` with their original relative paths. This public snapshot contains the transport-neutral AI1 wire/client/link modules and native regression tests only. It does not include credentials, proprietary Android application code, Momentum UI assets, or ESP32-S2 code.

`.github/workflows/ai-native-v47.yml` compiles and executes three native test binaries with GCC and sanitizers on an ordinary Ubuntu runner. This is intended to avoid private Actions compute/billing restrictions, but a successful run has not been confirmed at checkpoint creation. Check the Actions tab for results before declaring success.

Do not merge snapshot files into the primary repository. Any future fixes should be ported deliberately to an isolated primary development branch after tests pass. This workflow cannot validate Flipper firmware builds, Android APK builds, authenticated BLE GATT wiring, real offline AI inference, or physical hardware.
