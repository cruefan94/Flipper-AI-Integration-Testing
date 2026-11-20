# Native encrypted fallback: proof boundary (2026-11-20 13:55 ET)

Public-safe release-evidence note. **Do not publish private source, unencrypted updater binaries, credentials, private job logs, or personal device diagnostics.** This document is not a flash authorization.

## Exact verified public GitHub Actions metadata

| Evidence | Exact reference | Verified status | Meaning |
| --- | --- | --- | --- |
| Native encrypted fallback | [run 44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608) | completed / success; workflow head `f1cac80854f26259534c032b2855dd609dd6c58e` | Fallback workflow completed; **workflow head is the public test harness SHA, not the private firmware source SHA** |
| Encrypted artifact listing | [artifact list](https://api.github.com/repos/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608/artifacts) | `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`, 12,650,072 bytes, not expired | Artifact exists; size is not a checksum and encryption is not firmware integrity proof |
| S3 AI1 exact-head failures | [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063), [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160) | both failed on `a37868b100dfdac4b575b3ff194b8e69155e9061` | Two-failure trigger; failure category needs private step inspection |
| S3 diagnostic fallback | [44782519310](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782519310) | completed / success | Diagnostic workflow success **does not** mean native S3 build success |
| Historical F7 native run | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | completed / success, public harness head `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | Historical only, not a current updater approval |

## Required private release evidence before any candidate promotion

1. Privately establish the **exact private firmware source commit** checked out by the native fallback (not the public workflow SHA), toolchain, target, native compilation step, and packaging command.
2. In an authorized private context, decrypt the exact encrypted artifact and record its ciphertext SHA-256, decrypted updater SHA-256, archive member list, `firmware.dfu` SHA-256, **actual embedded DFU suffix and CRC**, C2 boundary and target identity. Record only sanitized status/opaque provenance references publicly; keep binary, decrypted logs and sensitive identifiers private.
3. Confirm all checks refer to the **same immutable artifact**, rather than a separately rebuilt image or synthetic CRC fixture. Do not retry the known failed DFU CRC 9-99 updater.
4. Independently compare Android installed package signer and versionCode against the candidate APK; a synthetic signing test or successful APK build is insufficient. No uninstall or replacement of the installed app.
5. Record matching BLE AI1 contract/version and paired hardware acceptance separately. An external ESP32-S3/Pi prototype remains optional until proven compatible.
6. Classify consecutive CI failures as code, runner/infrastructure, or unknown using private job-step evidence. If private Actions:read returns 403, label monitoring/fallback **BLOCKED**, never green; use only the approved encrypted/public-safe route, never disclose source or logs.

## Release ledger disposition

Android test APK: **HOLD** (installed signer/versionCode and paired BLE acceptance unverified).

Native F7 updater `.tgz`: **HOLD** (exact private source SHA, real artifact DFU CRC, C2, internal hashes, and qFlipper recovery evidence not established).

No merge, flash, install, or candidate promotion is authorized by this note.
