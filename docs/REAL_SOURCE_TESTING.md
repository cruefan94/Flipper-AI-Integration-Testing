# Actual implementation test strategy

The public CI runner compiles the real Android `SatelliteProtocol.java` from a pinned commit of the **public Android** repository and runs the standalone Java smoke harness. No private firmware source is published.

The Flipper C parser `flipper_app/satellite_protocol/ai_wire.c` remains private. Running its actual C implementation requires a reviewed publication of only that file and header, or running the same harness inside the private checkout. **Do not substitute an independent C reimplementation and call it a Flipper test.**

This is a source-level Java protocol test, not a BLE GATT integration test, Android APK build, or Momentum firmware build.
