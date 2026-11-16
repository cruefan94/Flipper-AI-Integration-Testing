# F7 encrypted artifact identity is not firmware.dfu CRC proof (2026-11-16)

**Scope:** public-safe evidence audit only. No firmware contents, secrets, decryption, download, flashing, or candidate promotion.

## Pinned observations

- [Native workflow run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed successfully on workflow head `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`. The run's public Actions job summary reports compilation, native package verification, encryption and encrypted upload steps as successful.
- [CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) currently points to `32f631c846db67d5f581887c00bbd06599b665c6`. **This is not the same SHA as the native run.** Do not attribute native-run success to the PR head without checking the ancestry/diff and exact workflow checkout.
- The run lists encrypted artifact ID `14207847319`, name `encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED`, with Actions artifact ZIP digest `sha256:1ec260e25953df1c4b637c2e7e3207d91d4318d3f0c69fac73ac974cb772807d`. This digest identifies the **outer encrypted upload archive**, not the decrypted native updater .tgz, embedded firmware.dfu, or DFU suffix CRC.
- GitHub lists expiry 2026-11-23 UTC for this artifact; availability after that date must be rechecked. Do not re-use the prior physically failed CRC 9-99 updater.

## Private-side evidence required before any release-candidate promotion

1. Record the private source commit SHA, pinned upstream Momentum SHA, public workflow SHA, checkout SHAs, toolchain versions and the exact native build run ID in the **private** canonical ledger.
2. On the trusted private runner, verify the actual compiled `firmware.dfu` contains the 16-byte UFD suffix and that `zlib.crc32(dfu_bytes) == 0xffffffff`. This must run on the *same* bytes included in the candidate updater; synthetic fixtures are insufficient.
3. Verify SHA-256 of `firmware.dfu` and native updater `.tgz`, the archive member inventory, F7 target and updater metadata. Record these hashes privately; do not publish source, image, updater, keys, or sensitive logs.
4. Verify encryption/decryption round-trip on the same native .tgz, then match its hash against the privately recorded pre-encryption digest. Keep only encrypted deliverables in the approved public-safe artifact store.
5. Pin matching Android test APK commit, package identity, versionCode, signing certificate fingerprint and SHA-256 in the **private** release ledger; a side-by-side test package is not a signature-compatible replacement for the installed app.
6. Run cross-component AI1 contract checks against exact firmware and Android commits. No physical BLE/flash acceptance can be inferred from host CI.
7. Obtain explicit owner approval before installing or flashing. Preserve qFlipper recovery and rollback instructions.

## CI failure handling

For the same core workflow and branch, two consecutive completed failures, or repeated failure before job provisioning, require the approved public-safe fallback route. Record both failure IDs, the fallback ID/result, and classify source failure versus runner/infrastructure failure. Private Actions:read HTTP 403 is **BLOCKED**, not evidence that fallback ran or that billing is the cause. Never copy private firmware, plaintext binaries, credentials or personal diagnostics into public CI.

**Disposition:** Native CI build observed PASS; artifact cryptographic identity partially evidenced at the encrypted ZIP layer; exact native DFU CRC, private source provenance, cross-device compatibility and hardware boot remain **UNVERIFIED / HOLD**.
