# Encrypted native F7 artifact: evidence handoff (public-safe)

Date: 2026-11-20. Scope: release evidence only; **NOT FLASH APPROVAL**.

## Known workflow observations

- [Native encrypted fallback run 44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608): the native firmware job completed private source retrieval, pinned upstream checkout, firmware compilation, .tgz verification/encryption, and encrypted-only artifact upload. This proves those job steps completed, **not** device safety or an independently inspected DFU suffix.
- [Historical pinned native run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) passed for an older source; do not promote it as current.
- Known CRC 9-99 failed updater: **never reuse or retry**.

## Required private-only artifact attestation

The authorized private runner should emit a minimal **private** machine-readable record with: workflow run ID and attempt; full private source commit SHA; upstream Momentum commit SHA; updater .tgz SHA-256 and byte length; firmware.dfu SHA-256; independently recomputed DFU suffix CRC-32 and embedded suffix CRC-32, with explicit match boolean; DFU target/alternate/flash address bounds; C2 exclusion check result; archive manifest and SHA-256 for each member; and a boolean that only an encrypted package was uploaded. Do not place firmware source, binaries, credentials, encryption keys, raw logs, device identifiers, or private attestation details in this public repository.

An authorized private reviewer must compare the **same artifact bytes** to all recorded hashes and the pinned source, not merely accept green CI or synthetic CRC fixture results. Any missing field, mismatch, unverified C2 boundary, or decryption/identity ambiguity is **HOLD**. Keep the private attestation in the private canonical tracker or an approved private artifact store, and publish at most a non-sensitive gate status and run link here.

## Paired release candidate gate

Android: extract the installed app signing certificate fingerprint without sharing personal device diagnostics; compare it to the exact proposed APK signer, application ID and strictly increasing versionCode. Signing mismatch means **do not replace or uninstall** the installed app. A separate test app is opt-in only with owner approval.

BLE AI1: pin both Android and firmware contract revisions; test UUIDs, authenticated roles, request/response framing, malformed UTF-8 rejection, stale-session epoch invalidation, consent revocation and reconnect on real paired hardware before claiming end-to-end success.

Recovery: document qFlipper backup, original Momentum restoration, verified updater identity, and owner-controlled recovery procedure before any flash request. No hardware flashing or protected-branch merges in this evidence phase.

## CI failure routing

After two consecutive **completed failures on the same workflow and branch**, or repeated failure before job provisioning, use only the approved public-safe private-firmware fallback route. Record both failed run IDs, branch, exact SHA, failure classification (code / runner / unknown), fallback run ID and outcome. A 403 on private Actions:read is **BLOCKED**, not a successful fallback. Do not retry indefinitely, leak private logs or relax gates.

## Release ledger handoff

| Gate | Evidence | Status |
| --- | --- | --- |
| Native encrypted compilation | 44782522608 | Passed workflow, untested artifact |
| Private source SHA / real DFU suffix CRC / C2 / internal hashes | Private attestation required | HOLD |
| Android signer + versionCode upgrade continuity | Device-side comparison required | HOLD |
| Physical BLE AI1 and qFlipper recovery | Owner hardware acceptance required | HOLD |

This document is a public-safe acceptance template, not a release manifest or a statement that a candidate is ready.
