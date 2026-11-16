# AI1 BLE cross-component acceptance and release handoff (2026-11-16)

Status: **TEST PLAN ONLY — NOT A PASS, NOT A RELEASE APPROVAL**. Public-safe document; no private source, binaries, device logs, credentials, or user diagnostics.

## Ownership and pinned inputs
- Firmware source and F7 candidate: private `cruefan94/Flipper-AI-Momentum-`; record an exact source commit and private Actions run only in the private tracker. Never mirror firmware files here.
- Android test APK: `cruefan94/Flipper-AI-Android-Satellite`; record exact source commit, build run, artifact identity, applicationId, versionCode, and signing-certificate SHA-256 in an access-controlled manifest.
- Public-safe integration tests: this repository. No combined release candidate branch mutation without the integration-testing owner.
- Consult private draft Momentum PR #23 and public-safe CI failover PR #23 before candidate promotion.

## AI1 contract matrix (fill with measured evidence, not assumptions)
| Gate | Firmware evidence | Android evidence | Result |
|---|---|---|---|
| Protocol identity/version and service/characteristic UUIDs | Exact source ref and specification revision | Exact source ref and specification revision | NOT VERIFIED |
| Request/response framing, maximum payload and encoding | Deterministic synthetic vectors | Same vectors | NOT VERIFIED |
| Fragmentation/reassembly, timeout, duplicate and out-of-order handling | Host test result | Host test result | NOT VERIFIED |
| Authentication/session generation, replay rejection, disconnect cleanup | Host test result | Host test result | NOT VERIFIED |
| BLE reconnect, notification subscription, cancellation | Host test result | Host test result | NOT VERIFIED |
| Actual Flipper↔Android AI1 request and response | Private hardware acceptance record | Private hardware acceptance record | NOT VERIFIED |

**Do not mistake stock Momentum RPC pairing for a working AI1 service.** Require a complete request/response with matching protocol revision and explicit disconnect/reconnect test before claiming hardware integration. Do not publish private GATT captures, pairing identifiers or device addresses.

## Android artifact gates
1. Record package identity and versionCode, APK SHA-256, signer certificate SHA-256 and exact Actions run/artifact ID.
2. Verify an in-place update is signature-compatible with the installed app **before** suggesting installation. Known signing mismatch is a hard STOP; do not uninstall or overwrite the owner's app.
3. A side-by-side test APK is opt-in only; its distinct applicationId and separate data directory must be checked against the produced APK.
4. JVM/CI passing does not prove real MediaPipe/LiteRT model inference, Cloudflare availability, voice, or BLE hardware.

## Native F7 artifact gates
1. Keep known DFU CRC 9-99 failed updater quarantined; never retry it.
2. Require exact source SHA, native F7 Actions run and job, encrypted-only delivery identity, decrypted private-side updater SHA-256, target identity, updater archive contents, and **actual firmware.dfu suffix CRC** verification.
3. A green synthetic CRC fixture or archive hash alone is insufficient. No private updater or decrypted payload may be published here.
4. Preserve original Momentum behavior, qFlipper recovery steps and explicit owner permission before any flash.

## CI two-failure routing
For the **same workflow + branch**, track two consecutive completed failed runs (IDs, attempt, conclusion, failure classification). Repeated pre-provisioning failure also triggers routing. Use only the approved public-safe fallback route. If private Actions:read returns 403 or token is missing, mark **BLOCKED**, never `success` or `fallback dispatched`. Do not retry indefinitely or infer billing. Public CI may receive only sanitized statuses and synthetic fixtures.

## Candidate promotion checklist
- [ ] Exact firmware and Android source SHAs pinned
- [ ] Both native F7 and Android test APK builds passed at those exact SHAs
- [ ] Private firmware.dfu suffix CRC and updater SHA-256 independently checked
- [ ] Android signing/package/version checks completed
- [ ] AI1 specification parity and deterministic cross-component vectors passed
- [ ] Physical BLE AI1 exchange and reconnect verified
- [ ] Recovery and rollback instructions validated
- [ ] No secrets/private firmware copied into public
- [ ] Explicit owner approval obtained for physical device actions

Unmet gates remain blockers. Maintain conservative overall completion; documentation commits do not increase hardware acceptance.
