# F7 C2 memory overlap: release-stop evidence (2026-11-18)

## Scope and provenance
This public-safe summary contains **no private source, binary, credentials, raw logs or user diagnostics**. Private Momentum workflow run [44267860731](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44267860731), branch `test/f7-c2-overlap-fail-closed-20261118-0331`, source SHA `165191bfee8dad357362eebd2627cb1453521c39`, completed **failure**. The native integrated-update job `134676851326` failed with exit code 2 after the firmware packager rejected an image overlapping the C2 region. This is a **firmware memory-layout safety failure**, not demonstrated runner/billing failure. **Do not override the guard with the unsafe confirmation flag.**

Two earlier same-workflow failures on branch `fix/esp32s2-merged-bin-output-20261118`: [44260352832](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260352832) at `ea14b03af37bdc96b7144e42acfc2d04c1c5d307` and [44260368327](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260368327) at `edc4a8fca49407ca5df3990f258a44e06dd61d45`. This pair triggered mandatory approved public-safe fallback. **Fallback dispatch remains BLOCKED/unverified; no fallback run ID.** The newer test branch failure is distinct and must not be combined into a same-branch count.

## Required corrective acceptance
1. Firmware owner investigates size and linker/memory layout privately; preserve the C2 overlap guard and existing Momentum features. Do not disclose proprietary source or private build output in public CI.
2. Produce a new **non-production** native F7 build with the actual updater packaging job completed successfully, explicitly showing **no C2 overlap**. Never reuse the quarantined CRC 9-99 updater.
3. Verify actual `firmware.dfu` suffix CRC (not synthetic fixtures), updater archive manifest, SHA-256 hashes, exact source SHA, encrypted-only private artifact identity and qFlipper recovery instructions through approved private-safe routes.
4. Match Android APK signing certificate and monotonically increasing versionCode before any upgrade; no uninstall/replacement of installed app. Verify BLE AI1 protocol parity, physical handshake and restore path separately.
5. The integration-testing workstream owns the release ledger; only promote passing, exact-head, independently attested artifacts. Pi/ESP32/radio/voice remain optional until proven.

## Status
**HOLD: F7 updater unsafe/unverified; Android test APK signing unverified; no hardware flashing or app installation authorized.** A green source check or standalone FAP is not a native updater pass. Do not weaken CI or use an override to force packaging.
