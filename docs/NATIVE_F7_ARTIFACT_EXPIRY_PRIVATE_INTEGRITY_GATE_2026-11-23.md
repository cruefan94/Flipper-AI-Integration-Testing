# Native F7 encrypted artifact preservation and private integrity gate — 2026-11-23

This is a **public-safe procedure only**. It does not authorize flashing or disclose firmware, decrypted binaries, credentials, or private build logs.

## Pinned evidence
- Momentum PR #89 source head: `0cae6e1fb7a81928566306a53a17abb6cac75d96`; qualifying failed full builds: [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882) and [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592).
- Approved fallback [45160017502](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45160017502) completed successfully. The run's public workflow head is **not** evidence of the fetched private firmware SHA; inspect the private build attestation.
- Encrypted Actions artifact ID `14811097270`, `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`, Actions archive digest `sha256:2cd9145e31430359b3f4978535d9249b1d017fc859e0a9e7a78f4c793be2eefe`. Reported expiry: **2026-11-30**. This digest is **not** the updater TGZ SHA or DFU member CRC.
- Historical native run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) passed, but has no currently listed artifact; do not substitute it for exact-candidate proof.
- Public synthetic CRC regression PR [#22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) is not a real DFU verification.

## Before artifact expiry (private authorized operator only)
1. Verify private Actions:read and artifact download authorization. If denied (including HTTP 403), mark **BLOCKED**, record the HTTP status privately, and stop; never copy sensitive output to public CI.
2. Retrieve artifact ID `14811097270` **only to an access-controlled private workspace**. Preserve the original encrypted archive byte-for-byte and record its own local SHA-256, download time, run ID, artifact ID, and encryption-envelope version in a private manifest. Compare local archive digest to GitHub's archive digest only when the exact hashing scope is established; do not assume zip download bytes equal API artifact digest.
3. Using the approved private decryption route, verify authenticated decryption and exact source SHA. Record private decrypted TGZ SHA-256, TGZ member inventory and SHA-256 for `firmware.dfu` and other updater members; do not publish member names or metadata that reveal private implementation details.
4. Verify the **actual** `firmware.dfu` suffix signature, declared length and CRC against its bytes (not synthetic fixtures). Verify updater packaging structure, target F7/Momentum compatibility, and recovery prerequisites.
5. Store only non-sensitive, fixed-label gate outcomes publicly: `encrypted_artifact_present`, `private_source_attested`, `native_tgz_hash_verified`, `real_dfu_crc_verified`, `recovery_documented`, each PASS/FAIL/BLOCKED with run ID. Never expose secrets, raw private logs, firmware files, decrypted hashes, or personal diagnostics publicly.
6. On any mismatch, stop candidate promotion; retain encrypted artifact securely for triage. **Never retry the known CRC 9-99 failed updater.**

## Cross-project release hold
Android APK requires package ID/versionCode, signing certificate continuity, APK SHA-256, BLE AI1 exact-version contract and explicit owner opt-in. Never uninstall/replace the existing differently signed app. Pi/ESP32/Termux evidence is optional until separately accepted; diagnostics must be opt-in, read-only, redacted and never upload tokens or device identifiers.

The integration-testing workstream alone maintains the combined candidate ledger. No production merge, device flash/install, or release promotion is authorized by this checklist.
