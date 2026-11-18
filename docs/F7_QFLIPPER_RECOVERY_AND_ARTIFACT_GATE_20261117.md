# F7 qFlipper recovery and artifact-evidence gate (public-safe)

Status: documentation only; no flashing authorization. Updated 2026-11-17.

## Quarantine and stop conditions

- The updater previously rejected by the physical device with **DFU CRC 9-99** is permanently quarantined. Do not retry it, rename it, or treat a ZIP SHA-256 as proof of a valid embedded DFU.
- The native AI1 trial [44023046497](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497) failed **DFU header size** validation. No new updater from this route is flash-ready.
- A successful workflow job, a synthetic CRC fixture, or an encrypted ZIP digest alone does not establish device compatibility.
- Do not uninstall the owner's existing Android app; signer mismatch means upgrade is blocked. Side-by-side APK installation is opt-in only.

## Required evidence BEFORE proposing a device recovery or flash

1. Private tracker records the exact private firmware source commit and its approved encrypted-only build workflow/run ID. Never put private source, binaries, logs, access tokens or personal device diagnostics in this public repository.
2. Inside the authorized private build route, validate actual **firmware.dfu** DfuSe header target/element lengths, embedded suffix, and whole-file CRC (expected residue `0xffffffff`); reject inconsistent framing even if CRC is recomputed.
3. Independently calculate SHA-256 for the exact native updater `.tgz`, its contained `firmware.dfu`, and any manifest. Match them to a privately retained, exact-source provenance record; distinguish these hashes from the encrypted transport ZIP hash.
4. Confirm encrypted-only delivery, artifact identity, Momentum/F7 compatibility, and the updater's original functionality preservation. Do not publish the native firmware or diagnostics in public CI artifacts or logs.
5. Confirm a recovery route is available: the official qFlipper application, a known-good official firmware package obtained from an authoritative source, working data-capable USB cable, sufficient battery and a backup of important user data/settings where possible. Verify the device model and available recovery mode with official documentation before any operator action.
6. Record operator approval and a separate device test plan; no automated flashing or unattended recovery.

## Recovery decision tree (operator guide, NOT an instruction to flash now)

- **Device boots normally:** do not retry the failed update. Preserve diagnostics privately, compare source/run/CRC evidence, and wait for an approved new candidate.
- **Device is stuck during update but qFlipper recognizes it:** stop and use qFlipper's official repair/recovery guidance after obtaining owner approval. Do not bypass updater validation or use the quarantined archive.
- **Device is not recognized:** verify the cable, power, USB port and official recovery-mode instructions before concluding hardware failure. Do not invent key combinations or use unverified recovery images.
- **Recovery succeeds:** confirm normal boot, stock Momentum features and data preservation before any AI1-specific testing. Record hardware outcome in the private tracker only.
- **Recovery fails:** stop further attempts, preserve private logs and request manual review; do not loop flashes.

## Cross-project release handoff

- Android [PR #62](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/62) at `3919ce339e95bf9ca4ac300058c0fad9ac2855a4` has [host CI success](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44087115570), **not** installed-app certificate parity.
- Integration [PR #81](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/81) at `e8e39ea7b0b81bdd2b1259f4d2157d74f195d1d0` has [CI success](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44088692054), **not** real F7 image proof.
- Firmware [PR #41](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/41) is still gated; do not infer hardware readiness from an overlay compile.
- For two consecutive failed attempts on the same workflow and branch, invoke only the approved public-safe fallback. If private Actions:read or dispatch permissions return 403, mark **BLOCKED**, preserve run IDs and never claim fallback success.

**Promotion decision:** HOLD until native evidence, matched BLE AI1 contract tests, Android signing, and owner-authorized physical validation are recorded in private canonical issue #5.
