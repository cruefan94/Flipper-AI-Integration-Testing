# Native fallback vs standalone FAP: release admission (2026-11-22 12:02 ET)

Public-safe coordination note; no private source, binary, credentials, or device diagnostics.

## Exact observed evidence
- Momentum PR #86 at `5eed030b206e15983624107bd794ae792138d5f2`: same workflow/branch failures [45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405). Two-failure fallback threshold reached.
- Approved public-safe fallback [45039819048](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039819048): `firmware / custom-firmware` **passed**, including private source fetch, native Momentum compile, updater verification, and encrypted-only artifact upload. `contract`, `android`, `protocol` and `diagnostic` were **skipped** in this run. Do not interpret skipped jobs as passed.
- Another native fallback [45039817534](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039817534) passed for a **different** source run; [45039820581](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45039820581) was a separate protocol fallback.
- Momentum PR #87 at `3b849075a7525c923155d303c6fb816e7e01ac2a`: standalone FAP [45033821260](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45033821260) and native F7 [45033821227](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45033821227) failed. Do not infer source/compiler defect without executed-step evidence.
- Android PR #129 at `4414f8794055aa09609003f30958c51e4ba3e486`: combined build [45040414698](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45040414698) and metadata [45040414746](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45040414746) passed. These do not establish installed-app signer parity or physical BLE AI1.

## Fail-closed admission checklist
1. **Native F7 updater:** record private source SHA, upstream Momentum SHA, native build run and job ID, artifact digest, verified *actual* `firmware.dfu` suffix CRC, internal updater checksums, encrypted-only delivery identity, and qFlipper recovery procedure in the **private** canonical ledger. Never reflash the known CRC 9-99 image. Historical run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) is not proof of the current image.
2. **Standalone FAP:** require an exact-source native FAP compilation result. Firmware compilation is not FAP compilation. Distinguish runner provisioning (no steps) from source/compiler errors (executed failing step). For each same-workflow+branch consecutive failure pair, log run IDs and authorized fallback run IDs; do not retry indefinitely.
3. **Android test APK:** capture exact tested SHA, versionCode, package/applicationId, artifact SHA-256 and signing certificate digest in a private release manifest. Verify existing installed app signer before considering in-place upgrade; if mismatch, do not uninstall or overwrite. Separate opt-in test APK only with explicit owner approval.
4. **AI1 BLE contract:** compare protocol version, UUIDs, framing, authentication/roles, timeout and reconnect semantics across exact firmware/Android commits. Passing isolated host tests does not prove physical connection.
5. **Optional Pi/ESP32/radio:** keep separate until transport, power/safety and device acceptance are proven. Do not include unverified peripherals in full-build claims.

## Current decision
**HOLD** both unified Android test APK and F7 updater release candidates; **BLOCK** standalone FAP promotion. Do not merge protected branches, flash hardware, install apps, or disclose private artifacts. Integration-testing remains the sole owner of the combined candidate ledger. Record any exact passing artifacts privately in [canonical issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).
