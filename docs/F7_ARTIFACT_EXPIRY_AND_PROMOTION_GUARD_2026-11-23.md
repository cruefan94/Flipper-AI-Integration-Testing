# F7 encrypted artifact expiry and promotion guard — 2026-11-23

Public-safe, read-only intake for the integration release ledger. **Do not publish or download decrypted firmware, source, keys, diagnostics or tokens into this public repository.**

## Exact observed artifact

- Repository: `cruefan94/Flipper-AI-Integration-Testing`
- Approved fallback workflow run: [45160017502](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45160017502)
- Artifact ID: `14811097270`; name: `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`
- Encrypted GitHub Actions archive SHA-256: `2cd9145e31430359b3f4978535d9249b1d017fc859e0a9e7a78f4c793be2eefe`
- Bytes: `12649912`; GitHub API reports `expired=false` as of November 23.
- Expires: **2026-11-30 11:03:29 UTC**. Preserve before that deadline using the **approved private-only route**; never attach encrypted or decrypted firmware to a public PR.
- Workflow's *public* head SHA: `f1cac80854f26259534c032b2855dd609dd6c58e`. This is the integration-testing workflow SHA, **not** proof of the private firmware source SHA.

## Required private verification (do not publish detailed results)

1. Authenticate with least privilege to the approved private artifact custody destination. Verify the download archive digest and byte count. Store it only in private restricted storage; document custody and expiry in the private tracker.
2. In a private isolated verifier, establish the exact private firmware source commit, dependency locks, build-run association, encrypted payload identity and decryption success. A green build alone does not prove this.
3. Hash the decrypted updater `.tgz` and each updater member. Validate the **actual** `firmware.dfu` 16-byte UFD suffix and whole-file CRC (expected `zlib.crc32(data) == 0xffffffff`) against the real artifact, not a synthetic fixture.
4. Check updater manifest, F7 hardware target, native build provenance and qFlipper recovery instructions. **Never retry the known CRC 9-99 failing updater**.
5. Keep release admission **HOLD** until native artifact integrity, Android signing-certificate continuity, APK SHA-256, BLE AI1 version/API parity and owner-approved physical testing have independent evidence.

## Two-failure fallback record

Momentum PR [#89](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/89) full-build failures: [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882), [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592). Approved public-safe fallback: [45160017502](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45160017502). Distinguish packaging/syntax and skipped native jobs in the source workflow from successful fallback compilation. Never interpret the encrypted artifact's digest as the decrypted firmware's CRC or hash.

## Handoff fields (private tracker only)

`private_source_sha`, `integration_workflow_sha`, `fallback_run_id`, `encrypted_artifact_id`, `encrypted_sha256`, `private_custody_location`, `decrypted_tgz_sha256`, `firmware_dfu_sha256`, `actual_dfu_crc_pass`, `updater_manifest_pass`, `recovery_check_pass`, `android_apk_sha256`, `android_signer_continuity`, `ai1_contract_version`, `hardware_test_status`, `owner_approval`. Unverified fields must be explicitly `UNKNOWN`, not inferred from green CI.
