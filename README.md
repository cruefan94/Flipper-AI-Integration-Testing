# Flipper AI Integration Testing

Public CI workspace for **Flipper Zero AI Momentum + Android AI Satellite + ESP32-S2**.

> **TESTING ONLY:** Nothing in this repository is a validated flashable firmware or production Android release. Never install or flash unverified artifacts.

## Source boundaries

- Private firmware source of truth: `cruefan94/Flipper-AI-Momentum-` (not copied here).
- Public Android source of truth: `cruefan94/Flipper-AI-Android-Satellite`.
- This repository contains **public-safe contract tests, test fixtures, documentation and CI scaffolding only**.
- Do not commit API keys, credentials, tokens, user data, private firmware source, private logs, or unreviewed licensed assets.
- No automatic flashing, repository writes, or release promotion.

## Validation plan

1. Check transport message framing and request/reply contracts with standalone test fixtures.
2. Run public Android APK validation in its original repository; link run and artifacts.
3. Import **only reviewed, license-compatible** Flipper BLE adapter and protocol source for isolated compilation tests.
4. Build firmware using pinned upstream Momentum sources and reviewed overlays only after the publication/license review.
5. Publish only clearly marked **UNTESTED** artifacts until verified on hardware.

## Current limitations

A public GitHub Actions runner cannot automatically access the private firmware repository. This workspace intentionally does not clone it or require private access tokens. Firmware builds are not configured here yet.
