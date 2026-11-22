# APK/F7 release evidence handoff — 2026-11-22 12:55 ET

Scope: PUBLIC-SAFE release verification checklist; no private firmware bytes, logs, keys, or user diagnostics. This is not a release approval.

## Exact observed source and run references
- Android draft PR #130 head `649d55402ac25cc294cbad79445181f10ded621b`, based on `4414f8794055aa09609003f30958c51e4ba3e486`. Its change concerns BLE link-health status evidence; no physical BLE verification or exact-head CI has been established in this handoff.
- Momentum FAP PR #87: native FAP workflow run 45033821260 failed. Do not infer a compiler failure from a job with no executed steps; inspect private job diagnostics.
- Private-safe native firmware fallback 45039819048: firmware/custom-firmware job passed; contract, Android, protocol, diagnostic jobs were skipped. Separate protocol fallback 45039820581 passed; never aggregate skipped jobs as passing.
- Earlier native candidate 43828499328: compilation and encrypted artifact upload passed, but historical evidence does not certify a current artifact or a hardware flash.
- Prior same-workflow FAP failure pair: 45008101314 and 45008110405. Preserve two-failure routing, record any newly authorized fallback run ID, and mark 403 Actions:read as BLOCKED, not success.

## Android acceptance gate (private metadata only)
1. Pin exact APK build commit, run URL, artifact ID, versionCode, applicationId and SHA-256 digest.
2. Compare the **certificate SHA-256** of the currently installed APK with the proposed upgrade. Signing certificates must match for an in-place upgrade; never uninstall or overwrite the existing app to force a mismatch. Keep signing credentials private.
3. Verify versionCode is strictly greater for an upgrade; a separate test applicationId must be opt-in and cannot claim upgrade continuity.
4. Require exact-head JVM, Android build and BLE AI1 wire-contract evidence. A green metadata workflow alone does not prove BLE or installed-app safety.

## Native F7 acceptance gate (private-only artifact checks)
1. Pin the private source SHA and Momentum upstream SHA; retain build run ID and artifact identity.
2. Verify **actual** firmware.dfu suffix CRC against its real bytes (not synthetic fixtures), native updater manifest/checksums, and outer SHA-256 before decryption or release promotion.
3. Verify encrypted-only public delivery: no plaintext firmware binary, private source, token, raw logs or credentials in public artifacts.
4. Preserve qFlipper recovery procedure, original Momentum restore path, and explicit owner authorization before any physical flashing.
5. Permanently quarantine the known DFU CRC 9-99 updater. Never retry that artifact.

## Admission
Neither Android test APK nor native F7 .tgz is promoted by this document. ESP32/Pi/Arduino/radio remain optional separately gated components. Integration-testing owns the shared release candidate ledger; feature branches provide exact passing refs and dependencies without concurrent candidate edits.
