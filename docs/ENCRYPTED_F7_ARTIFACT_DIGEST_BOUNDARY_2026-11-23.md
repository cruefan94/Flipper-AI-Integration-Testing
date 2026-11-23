# Encrypted F7 artifact digest boundary — 2026-11-23 09:00 EST

Public-safe integration evidence. This is **not** a release manifest, proof of a valid firmware image, or permission to flash.

## Observed exact records

- Qualifying private Momentum full-build failures: [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882), [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592). Latest relevant PR [#89](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/89), head `0cae6e1fb7a81928566306a53a17abb6cac75d96`.
- Approved public-safe fallback [45160017502](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45160017502): completed success; **only** `firmware / custom-firmware` and `describe` succeeded; Android, protocol, contract and diagnostic jobs skipped.
- Artifact API for that run reports ID `14811097270`, name `encrypted-flipper-ai-mobile-native-tgz-UNTESTED`, size 12,649,912 bytes, `expired=false` as observed, expiry `2026-11-30T11:03:29Z`, and GitHub artifact digest `sha256:2cd9145e31430359b3f4978535d9249b1d017fc859e0a9e7a78f4c793be2eefe`.
- **Critical scope:** the GitHub digest identifies the Actions artifact archive (encrypted delivery), **not** decrypted `firmware.dfu`, the inner `.tgz`, or its members. Never use that digest to satisfy DFU CRC, updater-member SHA-256, or binary source-provenance checks. The fallback run's public workflow head `f1cac80854f26259534c032b2855dd609dd6c58e` is **not** proof of the private firmware source SHA.
- Historical [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) currently lists zero artifacts; no present-day integrity assertion can be made from its successful job alone.
- Public CRC regression [PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) checks synthetic suffix fixtures, not this decrypted image.

## Private-only admission checklist

1. In a permitted private workflow, bind the **private source commit** and exact build input to the encrypted artifact ID, and record an attestation without printing source, private paths, secrets, binaries or diagnostics publicly.
2. Verify authenticated decryption privately; inspect the actual updater `.tgz` and `firmware.dfu` suffix and whole-file CRC using the existing release verifier; record only sanitized pass/fail, artifact identifiers and approved hash fields.
3. Record separate SHA-256 values for encrypted delivery, decrypted updater archive and relevant firmware members in the **private** canonical ledger. The GitHub artifact digest is not interchangeable with those hashes.
4. Validate Momentum F7 packaging, updater metadata, compatible target, recovery via official Momentum/qFlipper, and the prohibition on retrying the previous CRC 9-99 image.
5. Independently verify Android APK package/version/signing lineage, APK SHA-256, non-destructive update behavior and BLE AI1 API/spec parity; Worker-only green CI does not admit the APK.
6. Keep Pi/ESP32/voice/radio optional until scoped compatibility gates pass. No shared candidate promotion, protected merge, flashing, APK installation or production deployment without owner approval and physical tests.

## Current decision

**HOLD both coordinated deliverables.** Native fallback is a scoped CI success, not end-to-end verification. Preserve the two-failure fallback policy, avoid repeated reruns, and hand off exact passing source/artifact evidence to the sole release-ledger owner.
