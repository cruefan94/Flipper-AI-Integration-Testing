# BLE AI1 paired-acceptance evidence protocol (public-safe)

Date: 2026-11-19. **Test plan only; no paired test is claimed.**

## Scope and ownership
This file is a cross-repository release gate, not a new firmware or Android protocol definition. Firmware and Android owners must supply exact immutable source SHA, a matching public-safe protocol version/contract ID, their respective passing CI run IDs, and sanitized paired-test evidence. Do not infer compatibility from stock Momentum RPC connectivity or from separate green source tests. The integration-testing workstream alone promotes the combined candidate.

## Required public-safe evidence fields
- Firmware: private repository commit SHA, CI run URL/status, Momentum base revision, F7 native updater build provenance, exact real `firmware.dfu` CRC validation status, internal updater SHA-256 verified privately; **never publish private source, binary, internal hashes that disclose private payload identity, credentials or raw device logs**.
- Android: repository commit SHA, CI run URL/status, package/application ID, versionCode, signing-certificate continuity result (boolean only), side-by-side opt-in test APK identity.
- BLE AI1: protocol version, characteristic/UUID contract revision (only when approved public), negotiated capability set, positive/negative case counts, zero skipped required tests, and tested firmware/Android commit pair.
- Test context: simulator vs real device, Android API level, hardware model class, sanitized timestamps and outcome; never include MAC, pairing secrets, serials, personal paths, device identifiers, radio captures or sensitive logs.

## Required cross-component cases
| ID | Case | Acceptance |
|---|---|---|
| AI1-01 | Stock Momentum RPC reachable without custom AI1 service | Report RPC-only; do not mark AI ready |
| AI1-02 | Matching protocol version, explicit HELLO and ACK | Mark ready only after verified paired handshake |
| AI1-03 | Missing AI1 characteristic or wrong UUID | Fail closed; preserve stock RPC connectivity |
| AI1-04 | Mismatched protocol version/capability | Reject incompatible command; no false ready |
| AI1-05 | Disconnect during in-flight request | Invalidate session and stale callbacks |
| AI1-06 | Reconnect to same approved device | New session; no replay of stale queued commands |
| AI1-07 | Attempt to rebind to different GATT while active | Reject until explicit safe teardown/approval |
| AI1-08 | Background/foreground transition | Preserve truthful state; no phantom ready |
| AI1-09 | Timeout, duplicate ACK and malformed frame | Bounded retry or safe rejection; no duplicate execution |
| AI1-10 | Android offline engine unavailable | Truthful unavailable state; no false local AI response |
| AI1-11 | Optional Pi/ESP32 bridge absent | Core BLE operation unaffected |
| AI1-12 | Loss of transport during command | No unsafe command execution; recover only after handshake |

## Release decisions
1. Independent static CI is **source regression only**. Simulator protocol tests are **contract evidence only**. A paired hardware handshake is **device evidence**; none substitutes for another.
2. Record each result with firmware SHA, Android SHA, contract revision, CI run ID and a public-safe pass/fail/skip count. A missing field is HOLD.
3. Firmware release remains HOLD until real native F7 C2 flash-layout validation, real `firmware.dfu` suffix CRC and internal updater hashes are privately verified; never reuse CRC 9-99 artifact.
4. Android upgrade remains HOLD until the installed-app signer matches the candidate and versionCode is monotonic; do not uninstall/overwrite the installed app. Side-by-side test requires owner opt-in.
5. For two consecutive completed failing attempts on the same workflow and branch, or repeated pre-provisioning failure, route via approved public-safe fallback. Log both original run IDs and fallback run ID. A diagnostic-only green fallback does not prove native build or AI1 compatibility. On Actions 403, mark BLOCKED, never guess billing.
6. No protected merges, hardware flash, APK install, or production deploy without explicit owner approval.

## Evidence record template
```text
firmware_ref=PRIVATE_SHA_ONLY
android_ref=SHA
contract_revision=UNVERIFIED
firmware_ci=URL_OR_BLOCKED
android_ci=URL_OR_BLOCKED
paired_ci=URL_OR_NOT_RUN
paired_hardware=NOT_RUN
required_cases=12
passed=0
failed=0
skipped=12
native_f7=HOLD
android_upgrade=HOLD
candidate_promotion=HOLD
```

Related owner-approved blockers: private Momentum PR #23; public-safe failover PR #23; DFU CRC gate PR #22. The historical native build #43828499328 and diagnostic fallback #44587016728 do not establish acceptance for current heads.
