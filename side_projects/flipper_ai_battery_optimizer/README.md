# Flipper AI Battery Optimizer — independent side project (v0.1)

Standalone Android-compatible Java 8 core, **not installed in Momentum or the Android Satellite app**. This is a portable development/test fixture in an isolated **public testing branch**, ready to move into a new dedicated repository when one is created.

## Purpose
Use battery telemetry gathered locally on the Flipper Zero to advise its operator about power-saving decisions. AI on Android can eventually explain recommendations, but a deterministic safety policy makes all decisions. **No automatic setting changes, BLE commands, flashing, or Cloudflare uploads exist in this version.**

## Reuse rather than rewrite
- Flipper source: `cruefan94/Flipper-AI-Momentum-`, source branch `feature/momentum-ble-hardware-status-v62`. Its `flipper_app/flipper_ai.c` already reads `furi_hal_power_get_pct()`, `furi_hal_power_get_bat_health_pct()`, `furi_hal_power_is_charging()` for a local status view. This does **not** mean battery telemetry is transmitted by BLE.
- Android source: `cruefan94/Flipper-AI-Android-Satellite`, source branch `feature/android-radio-listening-v238`. Reuse `SatelliteProtocol.java`, `FrameCodec.java`, BLE trust gating, and `InferenceRouter.java` later.
- Public tests: `cruefan94/Flipper-AI-Integration-Testing`; this side project lives on an unmerged `sideproject/*` branch and is kept isolated from the main CI workflow.

## Stage 1 (included)
- Pure Java recommendation engine for low battery, thermal warnings, charging, and active hardware tasks.
- Optional discharge trend estimate from local samples (never an exact runtime promise).
- Fast host-only tests with javac/java; Android build and Flipper hardware tests are **not** included.

Run locally:
```sh
javac -d /tmp/flipper-battery-test src/flipperai/battery/BatteryOptimizer.java tests/flipperai/battery/BatteryOptimizerTest.java
java -cp /tmp/flipper-battery-test flipperai.battery.BatteryOptimizerTest
```

## Roadmap
1. Publish independent source repository when available and retain tests in the public testing workspace.
2. Add a read-only, permission-gated Momentum power snapshot provider; maintain existing AI1 limits and never interfere with active operations.
3. Add a read-only adapter in the Android Satellite; keep battery samples local by default.
4. Validate savings against a control device or repeatable usage profile; check disconnects, temperature, power cost of polling, and regressions.
5. Only after explicit authorization: optional user-confirmed, allowlisted settings adjustments.

The module is a **side project** until explicit integration approval. The app's existing package ID, signing, BLE and AI behavior must not change from this branch.
