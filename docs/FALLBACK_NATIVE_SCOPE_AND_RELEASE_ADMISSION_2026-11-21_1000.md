# Native fallback scope and release admission — 2026-11-21 10:00 EST

This is a PUBLIC-SAFE metadata-only handoff. No private firmware source, binary, keys, logs, tokens, personal diagnostics or artifact download links belong in this document. **Not a release approval.**

## Exact completed evidence

- FlipperHTTP original branch `dev/flipperhttp-safe-adapter-20261120`, workflow `FlipperHTTP read-only probe FAP (no firmware update)`: completed failures [44866082379](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866082379) and [44866117174](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866117174). Two-failure policy applies to that exact workflow/branch.
- [Public monitor 44906990301](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44906990301) completed successfully. [Encrypted private native fallback 44907023267](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44907023267) completed successfully, associated with failing private run 44866117174. This is evidence of a completed fallback *workflow*, not device acceptance.
- Fallback workflow's public head SHA: `f1cac80854f26259534c032b2855dd609dd6c58e`. **This is the public integration-testing workflow SHA, not the private Momentum firmware source SHA.** Do not substitute one for the other.
- FlipperHTTP PR [#79](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/79) head `73d89c710f0217b1557a99a23bf31a945f07d5dd` had one completed failing workflow [44910071261](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44910071261) as of this audit. PR #79 is a different branch from PR #76; do not combine counts across branches.
- Android Worker PR [#111](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/111) exact-head contract run [44891637886](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44891637886) passed. Android combined APK workflow [44863378694](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44863378694) passed on a different branch. Neither result proves a signing-compatible install.
- Public ESP32 WROOM offline preflight [44913570123](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44913570123) passed on `dad2375cf9c800cec563c5f846100475a218a610`; synthetic tests do not prove wiring, bootloader or radio behavior.

## Required private-only F7 attestation (fail closed)

1. Pin the *private* Momentum source SHA, overlay SHA(s), exact compiler/toolchain and native job ID. Retain this mapping only in authorized private tracker.
2. Inspect the **decrypted exact artifact** in the approved private environment; identify native F7 updater `.tgz` and embedded `firmware.dfu`. Validate actual DFU suffix structure and CRC, manifest identity, updater compatibility, and per-file SHA-256. Archive/encrypted-container hash is not a substitute for inner-file hashes.
3. Verify the final candidate is built from the same tested refs, that the encrypted-only boundary holds, and that the private package and recovery manifest are reproducible. Keep the known failed CRC 9-99 image permanently excluded.
4. Validate Momentum stock behavior and qFlipper recovery instructions without flashing the owner's device. Physical acceptance requires explicit owner approval and later testing.
5. Independently verify Android package name, installed-versus-candidate signing certificates, monotonic versionCode and AI1 BLE protocol parity before proposing an opt-in test APK. Never replace/uninstall the owner's installed app to bypass a signature mismatch.

## CI fallback and ownership

Count consecutive completed failures only within the **same repository + branch + workflow**; pending/skipped/other-branch results do not advance the count. After two failures (or repeated pre-job provisioning failure), use only the approved public-safe private-firmware fallback. A 403 on private Actions:read is **BLOCKED**, not proof of a successful dispatch; do not guess billing as root cause. Keep failing run IDs, fallback IDs, classification and corrective steps in private [MAIN tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5). The integration-testing workstream alone owns the combined release candidate ledger; do not edit shared candidate branches concurrently.

## Candidate disposition

- **Android test APK: HOLD** — certificate/versionCode continuity, integrated AI1 and physical acceptance not established.
- **Native F7 updater: HOLD** — private exact-artifact CRC/hash/source attestation and recovery proof missing.
- **ESP32/Pi/radio/voice: OPTIONAL** until explicit compatibility and safety gates pass.

No production merges, flashing, installations or public private-source uploads are authorized by this handoff.
