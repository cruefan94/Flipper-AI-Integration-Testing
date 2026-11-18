# qFlipper / F7 updater recovery evidence (PUBLIC-SAFE, no device actions)

Status: documentation only. No firmware image is approved by this guide. Owner approval and a physical recovery window are required before any flash, DFU recovery, or installation.

## Preflight and quarantine
1. Record the **private** firmware source commit, firmware branch, native build workflow/run/job, and updater archive SHA-256 in the private release ledger. Never publish private source, decrypted updater binaries, device identifiers, or diagnostic logs here.
2. Verify **inside an approved private runner** the actual `firmware.dfu` suffix CRC against the exact bytes packaged in the native F7 updater; validate DFU framing, targets, element sizes and the native `.tgz` SHA-256. A synthetic CRC fixture or an encrypted ZIP digest is **not** native firmware proof.
3. Keep the known CRC 9-99 failed updater quarantined permanently. Do not retry it, rename it, or treat a green host CI job as proof of device compatibility.
4. Record the exact Momentum version/target (F7), updater metadata, expected application retention, and a compatible known-good recovery package sourced through the authorized official channel. Do not assume an ESP32/WROOM peripheral build is a Flipper F7 updater.
5. Before any owner-approved device operation, ensure stable power, a known-good USB data cable, and a trusted computer with qFlipper installed. Back up user data through the supported qFlipper workflow and verify the backup exists. Never put backup contents or Flipper serial/device identifiers in public CI.

## Dry-run checks (no hardware writes)
- Capture the updater file name, byte length and SHA-256 **privately**. Match it byte-for-byte to the private build manifest.
- Confirm native DFU CRC verification passed on that exact image, not only on a fixture or separately generated DFU.
- Check qFlipper's installed version and platform, and whether the computer can see the device. Record only sanitized pass/fail in the public handoff.
- Verify the restore plan is feasible with the actual backup and known-good compatible firmware; keep these separate from the untested candidate.
- Stop if any provenance, signing, firmware target, CRC, backup, cable, or recovery prerequisite is unknown.

## If an owner-approved update fails
1. **Stop repeated attempts** with the same updater, especially on CRC 9-99. Do not run an automated retry loop.
2. Preserve the error code and minimal redacted observations in the private tracker. Do not post qFlipper logs, serial numbers, filesystem paths, tokens, or personal diagnostics publicly.
3. On the owner's approval, follow the current official qFlipper / Flipper Zero documented recovery procedure using a verified compatible known-good firmware package. Do not improvise a DFU image or bypass validation.
4. After recovery, verify basic stock/Momentum navigation and user-data restoration separately; BLE AI1, Android AI, ESP32, radio and peripheral acceptance require their own tests.
5. Record exact attempted image digest, observed result, recovery firmware digest, recovery result and owner approval in the **private** ledger.

## Cross-project release gate
- Android: verify package/application ID, versionCode monotonicity and signing certificate compatibility before any in-place update. Existing signing mismatch means **no replacement or uninstall**; isolated test APK is opt-in only with owner approval.
- BLE AI1: require pinned Android and firmware commits, matching contract version/hash, CI evidence and later a real-device handshake.
- CI: after two consecutive completed failures of the same workflow **and branch**, or repeated pre-runner failure, use only the approved public-safe private-firmware fallback route. Record both failure run IDs, fallback run ID and results. If permissions/dispatch are missing, mark **BLOCKED**, never claim a fallback succeeded.
- No protected merges, production deploy, hardware flash, or app installation from this document.

Evidence checklist: source SHA (private), workflow+run+job, artifact identity, encrypted ZIP SHA, native TGZ SHA (private), exact DFU CRC (private), target/version, signing provenance, AI1 contract hash, CI status, backup/recovery verification, explicit owner approval, physical test outcome.
