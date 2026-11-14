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

## Public AI1 contract test expansion (2026-11-12)
- Added boundary tests for 180-byte maximum frames, multi-byte UTF-8 characters, control characters and the maximum unsigned 32-bit request ID.
- GitHub Actions runs the tests on push; success for this revision has not yet been observed.
- This remains a standalone protocol fixture suite, **not** the Android application's JVM tests or APK compilation.
- Next: use the public Android source repository to build a complete APK, and validate the private firmware BLE adapter only after source/license review.

## Unified Flipper AI project coordination

This repository is indexed in the [eight-repository Flipper AI ecosystem](https://github.com/cruefan94/Flipper-AI-Integration-Testing/blob/main/PROJECT_ECOSYSTEM.md). The [private project hub and future-ideas ledger](https://github.com/cruefan94/Flipper-AI-Momentum-/blob/main/docs/UNIFIED_PROJECT_HUB.md) records cross-repository priorities, dependencies, deferred concepts and testing boundaries (requires access to private repository).

**Linking a repository does not merge its source or change its integration/approval rules.** Continue to honor this repository's own release, privacy and testing restrictions. The owner's primary ChatGPT project conversation is the coordination point, not an automated chat or GitHub syncing service.
