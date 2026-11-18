# Fail-closed CI triage: unexpected unittest success (2026-11-18)

This public-safe record contains no private source, logs, firmware artifacts or credentials.

## Evidence at pinned private source
- Repository: cruefan94/Flipper-AI-Momentum-
- Branch: `test/ai1-gatt-callback-reentrancy-20261118-1640`
- Source SHA: `f9fd6bc2659a411f87ec58e9e50d519f0584bdd0`
- Workflow A: [44403990366](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44403990366), F7 candidate: quick source checks **failed**, native F7 compile and TGZ **skipped**.
- Workflow B: [44403968056](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44403968056), full executable inventory: Python syntax **passed**, installer/packaging regression **failed**, downstream builds **skipped**.
- Both failed test jobs reported `FAILED (expected failures=7, unexpected successes=1)`. This is an **unexpected-success (unittest expectedFailure) regression**, not evidence of an infrastructure/billing failure or a successful firmware compile.

## Owner triage
1. Inspect the single unexpected-success test identifier and its expected-failure decorator **inside the private repository only**. Determine whether the behavior was actually fixed or the test no longer exercises the intended path.
2. If fixed, replace the expected-failure marker with a normal positive assertion and keep negative/regression coverage. If not fixed, correct the test setup and retain the safety gate.
3. Rerun each affected workflow once on the corrected exact SHA, preserving failing run IDs. Never suppress the exit status, remove checks solely to turn CI green, or count a skipped native job as a build.
4. The two failed runs above are **different workflow names** on one branch, not automatically a qualifying pair of consecutive failures in the same workflow. Check attempt history per workflow+branch before dispatching the approved public-safe fallback. If repeated failure occurs before job provisioning, use the fallback policy immediately. Report missing Actions:read permission as BLOCKED, not passed.
5. Keep source and artifacts private. Public fallback may receive only approved non-sensitive status/contract metadata; no private binaries, logs, secrets or firmware source.

## Coordinated release gates
- F7: native non-skipped compile, C2-safe memory layout, actual firmware.dfu suffix CRC and updater SHA-256 at exact source SHA, encrypted-only provenance, and owner-controlled qFlipper recovery remain required. Never retry the known CRC 9-99 image.
- Android: [combined APK workflow 44384518105](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44384518105) is now **completed success** at `b1dfbd572bea42c4fffb53d8372b7eb1b1633ead`, superseding an earlier in-progress failure observation. Signing identity, versionCode, data-preserving upgrade and device acceptance remain unverified.
- BLE AI1: exact firmware/Android protocol version, GATT identity, authentication/session/CCCD semantics and real-device handshake still need matched proof.
- Pi/ESP32/radio/voice: optional until interface and safety gates pass; no candidate promotion.
- Neither a debug APK nor historical F7 CRC CI proves a flash/install-ready paired release.

No protected merge, physical flashing, app install, production deployment or unified candidate promotion is authorized by this document.
