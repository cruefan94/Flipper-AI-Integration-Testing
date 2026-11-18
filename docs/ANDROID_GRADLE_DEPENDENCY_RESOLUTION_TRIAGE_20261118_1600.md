# Android AI1 APK dependency-resolution failure triage — 2026-11-18 16:00 ET

PUBLIC-SAFE metadata only. No private firmware, artifacts, device logs, credentials, or personal information.

## Exact failed source and job

- Android PR [#76](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/76), branch `fix/android-ai1-rpc-status-isolation-20261118-1447`, commit `b1dfbd572bea42c4fffb53d8372b7eb1b1633ead`.
- [Android run 44384518105](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44384518105): completed **failure**. Job `Host regressions + one full-feature Android APK` failed in `Build one complete Flipper AI Satellite APK (debug, not an automatic upgrade)`.
- Host Python source regressions ran successfully before Gradle. Gradle failed while configuring root project `FlipperAISatellite`, before application compilation: could not resolve `org.apache.httpcomponents:httpmime:4.5.6` and `org.glassfish.jaxb:jaxb-runtime:2.3.2` in the Gradle buildscript classpath. Maven repository URLs were searched.
- **Classification: dependency resolution / build environment, not demonstrated Kotlin or BLE AI1 source compilation failure.** The logs alone do not prove a transient outage, broken repository configuration, or billing issue. No successful APK from this exact commit was established.
- Prior [Android run 44361989778](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44361989778) passed at **different** commit `f4c60535788bd18b74b6888facae001d9eb3676a`; it cannot promote PR #76.

## Controlled next actions (Android owner)

1. Confirm availability and exact Gradle repository configuration for the missing coordinates without bypassing dependency integrity. Inspect Gradle's full `--info` resolution diagnostics on a controlled, non-production CI attempt; sanitize logs.
2. If reproducible, correct the dependency-resolution root cause on the Android-owned PR branch; do not modify it from integration testing. Record exact corrective commit and workflow run.
3. Count consecutive **completed failures on the same workflow and branch**. At the second failure, use the established approved public-safe fallback; if dispatch or private read permissions fail, record **BLOCKED** with HTTP status, not success. Do not endlessly rerun.
4. Rebuild and verify artifact name, size, SHA-256, package ID, versionCode and signing certificate before any paired candidate consideration. Do not overwrite or uninstall the existing signed app.

## Other exact release gates at this check

- Momentum PR [#61](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/61) at `eb4ce27cbd3728e557d2f70c574b88862989bcfb`: [F7 workflow 44370997639](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44370997639) green overall, but **native compile and TGZ jobs skipped**. No current native F7 artifact is accepted; C2 layout, real firmware.dfu CRC and SHA-256 remain HOLD.
- Public paired evidence validator PR [#142](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/142): [regression 44387353196](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44387353196) and [smoke 44387352908](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44387352908) passed at `17c59383a50626b09367b3600298d9aad268041e`. These validate metadata, **not** binaries or devices.
- Public fallback [44377563485](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44377563485) was green, but **firmware job skipped**; protocol matrix jobs passed. It must not be represented as a successful firmware build fallback.
- Historical [native run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) had a successful custom-firmware job at another source revision. Never retry the CRC 9-99 image.

**Unified candidate status:** Android APK HOLD; F7 updater HOLD; paired BLE AI1 hardware acceptance HOLD. No merges, installs, flashes, or promotion.
