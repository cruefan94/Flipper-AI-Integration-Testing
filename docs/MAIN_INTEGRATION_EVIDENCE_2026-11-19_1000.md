# MAIN integration evidence checkpoint — 2026-11-19 10:00 America/Toronto

Public-safe coordination document only. No private firmware source, artifacts, credentials, device identifiers, or raw logs.

## Exact observed evidence

| Workstream | Reference | Observation | Candidate gate |
| --- | --- | --- | --- |
| Firmware flash-layout safety | cruefan94/Flipper-AI-Momentum- PR #66; Actions 44481566067, 44481581444, 44481593032 | Three completed failures on same workflow branch; native integrated updater not accepted | BLOCKED |
| Firmware C2 boundary tests | private PRs #67, #68, #69 | Open audit/test work; not evidence of a safe native updater | BLOCKED |
| Public-safe firmware fallback | integration-testing Actions 44491711278 | Previously observed successful firmware fallback; does not supersede private flash safety failure | HOLD |
| Historical native F7 | integration-testing Actions 43828499328; PR #22 at 32f631c846db67d5f581887c00bbd06599b665c6 | Native job passed at historical revision; no current-head flash proof | HOLD |
| Android BLE reconnect | Android PR #84 at 6ebb790539bfebc71f142b8107c61ec79f7645e9; Actions 44536357309 | Host CI success; signing continuity and device handshake not verified | HOLD |
| Pi exact dashboard suite | integration-testing PR #177 at 2d5336656cf59fc63dc0453eb13539b6d171f5b4; Actions 44530833357 | Smoke success only; require exact suite count and zero skips | HOLD |
| Pi device acceptance | integration-testing PR #179 at 3931a1937ae9554c857bf16aaaf93e97bc491534; Actions 44541880601 | Smoke passed; device acceptance remains separate | HOLD |

## Acceptance checks before promotion

1. **F7:** exact private source SHA; C2 layout boundary and actual flash plan approved; non-skipped native F7 compilation; actual firmware.dfu suffix CRC; internal updater .tgz SHA-256; encrypted-only artifact identity; qFlipper DFU recovery guide reviewed. Never reuse DFU CRC 9-99 artifact.
2. **Android:** exact APK SHA-256, applicationId, versionCode/versionName and signer certificate digest; compare signer to installed app before any upgrade. Existing mismatched-signature installation must remain untouched. Separate test install requires owner approval.
3. **BLE AI1:** pin both source SHAs and protocol version, verify UUIDs, packet framing, request/response semantics, timeout/reconnect behavior, status error handling, and actual paired-device handshake. Passing independent host suites is insufficient.
4. **Pi:** run the exact 11-or-more dashboard test suite with zero skips; record actual test count and Actions job, not smoke CI alone.
5. **Fallback:** after two consecutive completed failures for the same workflow AND branch (or repeated pre-provision failure), use the approved private-safe public fallback. Preserve failing run IDs and fallback run ID. If permissions are 403, report BLOCKED, not passed. Distinguish code failure from runner failure.
6. **Termux/GitHub bridge:** diagnostics must be opt-in, redacted and read-only by default; never publish private logs or device identifiers.

## Ownership and disposition

Integration-testing owns the unified candidate ledger. Firmware, Android, and Pi feature owners retain their existing source branches. This document is a handoff, not a candidate promotion, merge approval, or flash authorization. No production merge, device flashing, APK installation, or physical acceptance is claimed.
