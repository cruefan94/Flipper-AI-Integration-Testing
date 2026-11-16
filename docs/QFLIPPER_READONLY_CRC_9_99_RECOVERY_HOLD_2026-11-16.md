# qFlipper CRC 9-99: read-only evidence and recovery hold (2026-11-16)

**Scope:** Raspberry Pi 4B with qFlipper; documentation only. No firmware, binaries, secrets, or private logs belong in this public repository. Do not retry the updater implicated in private Momentum issue #22.

## Known evidence, not hardware acceptance
- Native encrypted F7 build: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 — `custom-firmware` job completed successfully.
- Encrypted artifact ID `14207847319` (`encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED`). The artifact being uploaded does **not** demonstrate that the exact decrypted firmware image's DFU suffix CRC has been independently inspected.
- Public synthetic CRC gate: draft PR #22, head `32f631c846db67d5f581887c00bbd06599b665c6`. Synthetic tests are not hardware validation.
- The previously attempted physical qFlipper updater failed DFU CRC **9-99**. Preserve existing working firmware; never retry the failed package.

## Safe Pi-side collection (no writes to device)
1. Leave the Flipper running its existing firmware; do not start an update.
2. Verify qFlipper installation: `command -v qFlipper`.
3. List local log filenames, without uploading their contents: `find "$HOME/.local/share/qFlipper" -maxdepth 1 -type f -name 'qFlipper-*.txt' -printf '%TY-%Tm-%Td %TH:%TM %f\n' | sort`.
4. For local-only progress monitoring, choose a **file**, not the directory or a placeholder path:
   ```sh
   LOG=$(find "$HOME/.local/share/qFlipper" -maxdepth 1 -type f -name 'qFlipper-*.txt' -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
   test -f "$LOG" || { echo "No qFlipper log file"; exit 1; }
   python3 raspberry_pi/qflipper_progress.py --log "$LOG" --follow
   ```
   This observer follows one selected file; restart it if qFlipper rotates to a new file. The log can contain device-specific data: keep it private.
5. Stop the observer with Ctrl+C. Do not publish full qFlipper logs, device serial numbers, local usernames, IPs or tokens.

## Mandatory exact-artifact acceptance before any new flash approval
- Pin the **private source SHA**, native Actions run ID, updater archive SHA-256 and decrypted `firmware.dfu` SHA-256 in a **private** manifest.
- Independently check the **real** `firmware.dfu` 16-byte `UFD` suffix and CRC (the verifier's `zlib.crc32(data) == 0xffffffff` condition), not only a synthetic fixture or outer archive SHA.
- Confirm encrypted-only public artifact delivery; verify manifest/updater target F7 and archive contents through the approved private-safe route.
- Verify a known-good recovery plan and explicit owner approval **before** any physical update. No unattended flashing.
- If private Actions history is HTTP 403, label fallback **BLOCKED**, request least-privilege Actions:read, and do not claim the two-failure fallback ran.
- For two consecutive completed failures on the same workflow+branch (or repeated pre-provisioning failures), use only the approved public-safe fallback and record original and fallback run IDs; never export private firmware.

## Coordination
Canonical private ledger: https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5.
This runbook is a non-production aid; it does not change either the Android test APK or F7 updater candidate.
