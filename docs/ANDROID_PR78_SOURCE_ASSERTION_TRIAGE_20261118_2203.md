# Android PR #78 source assertion failure — public-safe integration handoff

Date: 2026-11-18 22:03 America/Toronto. No private firmware source, credentials, binaries, or device diagnostics included.

## Exact evidence
- Android PR #78 head `be1205762bb0160fab5f046a32e8f906628fdccb` (`fix/android-verified-channel-status-20261118-2047`).
- Combined APK workflow [44439583568](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44439583568): completed **failure**. Job `Host regressions + one full-feature Android APK` ID `135276793447` failed during Python source regression tests; APK production for this head is **not proven**.
- Failing test: `android_satellite/tests/test_ble_session_jobs_source.py::BleRequestCancellationWiringTest.test_connection_loss_invalidates_and_cancels_requests`, line 45. It expects literal `message.startsWith("AI BLE ready")` in `BleConnectionService`, but the new status-prefix implementation no longer contains that exact string. This is a source-assertion failure; determine whether the changed predicate preserves the intended session invalidation/cancellation behavior before adjusting the test. Do not weaken the negative cases.
- Prior Android PR #77 `6d43670ce38cfe5712904b6fc88f71f77b5fbd23` had passing combined workflow [44424057383](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44424057383); its APK does not certify PR #78.
- Momentum PR #63 `dc97ec774867b3e580ad2bfd4db448f1df713cfd`: [44422497544](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44422497544) quick source checks succeeded but native F7 compile and TGZ release were **skipped**. Separate inventory [44422482009](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44422482009) failed. No current native firmware artifact evidence.
- Historical encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) has successful `custom-firmware` job, but at an older pinned revision. Do not reuse failed 9-99 updater.

## Owner handoff / acceptance
1. Android owner: compare old and new `BleConnectionService` status classifiers and the failing test. Assert semantic boundaries: stock Momentum RPC must not signal AI1 ready; actual authenticated AI1-ready status must preserve the active session; genuine disconnect/revocation must invalidate requests and cancel stale work. Make focused tests follow the canonical classifier only after confirming behavior. Re-run the exact-head combined APK workflow and record run ID and SHA.
2. Integration owner: do not promote APK until successful exact-head build, manifest/package/versionCode, installed-vs-candidate signing certificate compatibility, and opt-in device upgrade evidence. Never uninstall/replace the owner's stable app without approval.
3. Firmware owner: obtain a non-skipped C2-safe native F7 build with real `firmware.dfu` suffix CRC, TGZ SHA-256 and encrypted-only artifact provenance; keep qFlipper recovery documented. Do not flash.
4. BLE AI1: pin paired firmware/Android SHAs and validate ATT frame size, characteristic UUIDs, CCCD/auth sequencing, session epoch, disconnect and stale callbacks before integration promotion.
5. Two-failure policy: count completed failures per identical repository + workflow + branch, not across distinct workflows/branches. PR #78 has one observed completed failing run. If a second consecutive completed failure occurs, use only approved PUBLIC-SAFE fallback; if private Actions:read is denied, mark **BLOCKED** with run IDs. Never copy private firmware, binaries, keys or logs into public.
6. Termux/Pi/ESP32/Arduino/radio/voice remain optional separate gates until proven compatible; no device diagnostics published.

## Release decision
**HOLD** both unified deliverables. This is a diagnostic documentation-only change, not a firmware or Android feature fix or physical test.
