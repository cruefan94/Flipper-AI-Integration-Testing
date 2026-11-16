# Two-failure fallback and unified release evidence checklist

Public-safe operational checklist, 2026-11-16. **No private firmware source, updater binary, signing material, token, device logs, or personal diagnostics belong in this repository.** This document is a procedure, not a claim that fallback or device testing succeeded.

## Per-workflow, per-branch failure ledger

Record privately for each core workflow/branch: repository; workflow identifier; exact branch and head SHA; first and second *completed* failing run IDs and URLs; job provisioning status; failure class (source/test, artifact, permission, or runner/infrastructure); corrective action; fallback dispatch ID and result. Count failures on the same workflow and branch only; do not count a canceled run as a completed failure. Do not guess billing causes.

**Trigger:** two consecutive completed failures on the same core workflow+branch, or a repeated failure before any Actions job is provisioned. Use only the existing approved public-safe private-firmware fallback route. If private Actions:read returns HTTP 403 or its token is missing, record **BLOCKED — private Actions coverage unavailable**, with no claim of automatic dispatch. Do not retry indefinitely or relax gates. Fallback success requires an actual dispatched run ID and completed successful result, not a green coverage-monitor job.

## Firmware F7 promotion gate

1. Identify the exact private source commit SHA, native build run ID, target F7 and build inputs in the private tracker.
2. Verify actual native build job success and encrypted-only artifact identity; keep encryption key, package and plaintext out of public logs.
3. Verify the *actual* `firmware.dfu` embedded suffix/whole-file CRC, updater structure, target, manifest and archive SHA-256 in a permitted private runner. A synthetic CRC fixture test is insufficient.
4. Document a recovery route using qFlipper and retain the currently working firmware. Never retry the previously failed DFU CRC 9-99 package.
5. Require explicit owner permission before any physical flash; successful CI does not imply hardware success.

## Android test APK promotion gate

1. Pin exact Android commit, successful build run, artifact ID, package/application ID, versionCode and versionName.
2. Compare signing certificate SHA-256 against the *currently installed* package before any in-place upgrade. A mismatch is a hard stop; do not uninstall or overwrite user data.
3. Keep the separately identified test APK opt-in and do not install automatically.
4. Validate the BLE AI1 contract against the pinned firmware revision, then collect real phone-to-Flipper session evidence privately.
5. Do not infer offline model inference, online Worker availability, voice or radio hardware success from compilation.

## Unified handoff record (private canonical tracker)

Use `cruefan94/Flipper-AI-Momentum-/issues/5` for exact source SHAs, passing run IDs, artifact checksums and identity (only non-sensitive metadata), AI1 API/spec revision, firmware/Android compatibility, Pi/ESP32 optional dependency gates, hardware status, blockers and next owner action. Public summaries must omit any private source, binary, secrets and device-specific diagnostics.

## Reference evidence checked 2026-11-16

- Public provenance PR #30 head `e75b8c332ada62261a26ff0772697a956cb17140`: metadata gate run [43855258912](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43855258912) and smoke run [43855258895](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43855258895) completed successfully.
- Public DFU CRC PR #22 head `32f631c846db67d5f581887c00bbd06599b665c6`: synthetic gate [43828565939](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828565939) passed.
- Encrypted native F7 candidate [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) custom-firmware job completed successfully. This public job status alone does **not** establish independently reviewed exact-image DFU CRC, provenance or physical flashing.
- Android PR #38 head `a4af937843306f045971d040d99be20af0964d2c`: public APK run [43835481467](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/43835481467) and side-by-side APK run [43835481373](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/43835481373) completed successfully. Physical installation and signing compatibility remain unverified.

No release candidate is promoted by this document.
