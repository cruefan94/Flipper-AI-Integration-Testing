# Unified candidate proof matrix — 2026-11-21 (public-safe)

This is an **evidence request and non-production handoff**, not an artifact attestation. Do not publish private firmware source, updater bytes, binary hashes that identify confidential builds, credentials, device logs, personal diagnostics, or signing certificates/keys here. Put private attestations only in Momentum issue #5.

## Evidence categories and current gates

| Candidate | Required exact-head proof | Current decision |
| --- | --- | --- |
| Native F7 Momentum updater | Private firmware source SHA; native F7 target; exact `.tgz` SHA-256; extracted `firmware.dfu` whole-file CRC check; package member hashes; C2 boundaries; encrypted-only delivery identity; qFlipper recovery plan | HOLD. Historical workflow 43828499328 has ESP32-named artifacts; 44782522608 has an encrypted UNTESTED output. Neither is a verified flash-ready F7 candidate. Never retry failed CRC 9-99 updater. |
| Android AI Satellite APK | Exact Android commit and successful build run; APK SHA-256; package ID; versionCode higher than installed; matching signing certificate fingerprint or separately named side-by-side app; physical AI1 acceptance | HOLD. PR #105 exact-head combined APK run 44863378694 passed, but signing and physical tests remain unverified. No replace/uninstall. |
| ESP32-S3 AI1 | Host regression exact commit and two-failure history; native build; authenticated AI1 protocol parity; safe voltage and power; hardware test | HOLD. Momentum PR #75 run IDs 44755541063 and 44755560160 failed. Earlier public-safe fallback 44782519310 provided diagnostics only, not native acceptance. Private Actions:read 403 = BLOCKED. |
| Pi/Arduino/radio/voice | Exact source/CI, consent and electrical/receive-only safety gates, compatible transport version, device acceptance | OPTIONAL, not included in either core candidate. |

## Cross-component AI1 BLE acceptance contract

Before promotion, the integration owner must record the same AI1 contract version on F7/S3 bridge, Android, and Pi adapters; message framing, UTF-8 byte limits, authentication challenge/replay rules, command IDs, response/error codes, readiness negotiation, MTU/chunk reassembly, disconnect/reconnect epoch handling, timeout behavior, and a cross-component test run ID. Stock Momentum RPC readiness does **not** prove custom AI1 readiness. A passing single-repository source regression is not a paired-device test.

## Two-failure route (strict)

Group failures by **repository + workflow + branch**, and record completed attempt IDs, conclusion, exact SHA, and whether a runner was provisioned. After two consecutive completed failures, or repeated pre-job failure, invoke only the approved public-safe private-firmware fallback. If private Actions:read returns HTTP 403 or the fallback cannot be dispatched, record **BLOCKED**, never success. Different branches do not reset or satisfy one another's evidence. Distinguish code failure from checkout/runner/infrastructure using actual job steps; never infer billing. Never rerun indefinitely or relax release gates.

## Handoff contract

Every source owner supplies: repository, exact commit, PR, successful Actions URL, test scope, artifact identity/hash stored in its permitted visibility, dependencies, blockers, and recovery procedure. Only integration-testing owns the combined candidate ledger. This file does not promote any build, authorize flashing, or certify installation. The private canonical tracker is https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5 .
