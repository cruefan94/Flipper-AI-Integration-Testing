# Unified Flipper AI release evidence ledger (2026-11-16)

This is a **public-safe evidence index**, not a release authorization. Private source, firmware binaries, encrypted payload bytes, credentials, and device diagnostics must not be copied here. The private canonical coordination tracker is Momentum issue #5. Every artifact requires exact-source provenance and physical acceptance before release.

## Candidate matrix

| Deliverable | Current evidence | Gate / disposition |
| --- | --- | --- |
| Native F7 Momentum updater | [Native encrypted build run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): custom-firmware job completed **success**; encrypted artifact `encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED` (artifact ID 14207847319). Public [DFU CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) at `32f631c846db67d5f581887c00bbd06599b665c6`. | **HOLD**: success is CI/build evidence only. Require private manifest containing exact private source SHA, firmware.dfu embedded suffix CRC result, archive SHA-256, encrypted payload identity and successful private-side independent verifier. Prior CRC 9-99 hardware failure; **never retry old failing artifact**. No new hardware flash approved. |
| Android Satellite test APK | [Side-by-side PR #36](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/36) at `5ee2de0dab36d0ea1109a02e1c0bb62bc1687767`; [APK CI 43817339981](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/43817339981) reported pass. | **TEST-ONLY**: distinct `com.flipperai.satellite.test` package; existing production signing differs, so no overwrite/uninstall. Need exact artifact digest, signing certificate fingerprint, versionCode, install and on-device AI/BLE acceptance. |
| BLE AI1 contract | [Android AI1 parity PR #22](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/22); [private firmware BLE generation hardening PR #24](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/24). | **NOT INTEGRATED/NOT ACCEPTED** until pinned contract version, UUID/characteristic/authentication/framing vectors and both sides' exact CI refs match, then hardware BLE handshake/reconnect and inference are verified. Stock Momentum RPC does not prove AI1. |
| Pi, ESP32, radio and voice | Separate optional prototypes and workstreams. | **OPTIONAL** until interface, safety, reproducible artifact and hardware gates pass. Do not silently bundle unverified peripheral components. |

## Two-consecutive-failure policy

For the **same workflow and branch**, count completed failed build/test attempts, or repeated failure before runner provisioning. On threshold, use the approved public-safe integration-testing fallback. Distinguish code/test failure from infrastructure/runner failure. If private Actions:read returns HTTP 403, mark **BLOCKED: missing Actions:read authorization**, do not claim automated fallback. [Failover visibility PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23) is draft. Record primary run IDs, fallback dispatch/run IDs, conclusions and corrective action in private issue #5. No endless reruns, bypassed gates or automatic flash.

## Acceptance checklist

1. Pin exact source SHAs, contract/API versions, build job IDs and package/artifact IDs.
2. Independently verify native F7 `firmware.dfu` suffix CRC **on the exact newly built image**, then archive hash, encrypted transport hash and decrypted round-trip, with evidence stored **privately**.
3. Verify Android APK identity, signing cert, versionCode and test-only isolation; never replace the existing owner app.
4. Run cross-component BLE AI1 vectors and source/build regressions; link actual passing run IDs.
5. Keep rollback/recovery instructions and a verified backup. Physical qFlipper flash, Android installation and end-to-end acceptance require explicit owner approval.
6. Promote only after passing criteria, through controlled non-production integration branches. No protected-main merges.

## 2026-11-16 handoff

The native build job in run 43828499328 succeeded and uploaded encrypted artifacts. This is **not** proof of physical update success or proof, from public metadata alone, of exact embedded DFU CRC contents. PR #22 is still open; the previous failed hardware artifact is quarantined. Next: private-side artifact provenance and DFU CRC evidence review, then pinned Android/BLE candidate matrix update. Overall project completion remains a conservative **64%**, not increased by CI-only evidence.
