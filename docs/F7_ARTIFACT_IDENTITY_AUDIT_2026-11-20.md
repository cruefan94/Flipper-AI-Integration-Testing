# F7 encrypted updater: artifact identity and promotion gate (2026-11-20)

## Scope and observed evidence

This is a **public-safe metadata audit**, not a firmware validation or release approval.

- Historical native Actions run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) has a successful `custom-firmware` job, but the first-page artifact listing returned **four ESP32-named encrypted artifacts**, **not an explicitly identified native F7 updater**: `encrypted-esp32-programmer-momentum-sdk-GPL-UNTESTED` (34,681 bytes), `encrypted-FlipperAI-ESP32-GATT-AUDITED-NEXT-FLASH-CANDIDATE-UNTESTED` (12,890,755 bytes), `encrypted-flipper-ai-esp32-integration-preview-tgz-UNTESTED` (12,655,597 bytes), and `encrypted-esp32-wroom32-component-compat-NOT-HARDWARE-VERIFIED` (200,267 bytes). A green workflow cannot establish the identity of the intended F7 candidate.
- More recent [run 44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608) has the encrypted artifact `encrypted-flipper-ai-mobile-native-tgz-UNTESTED` (12,650,072 bytes), but the encrypted public artifact alone does not expose a verified exact private source SHA, unpacked updater hash or actual DFU CRC.
- Public [CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) is a prevention check, not proof that the previously failed DFU image was repaired. Never retry the DFU CRC 9-99 image.

## Required private-only attestation (before any candidate promotion)

The authorized private build operator must record **inside the private tracker only**: exact private source commit, build workflow/ref/run/attempt, native F7 target, Momentum baseline, artifact ID and encrypted identity, archive filename and SHA-256, extracted `firmware.dfu` SHA-256, real 16-byte DFU suffix and CRC result computed on the **actual extracted image**, C2 memory boundary checks, and a reproducible verification command with tool version. Do not upload firmware, decrypted archives, binary, keys, private build logs or identifying device data to this public repository.

Independently validate archive contents and `firmware.dfu` from the same encrypted artifact, with the private verifier's real-image CRC check. Require the exact private source SHA to match the native build run and candidate ledger. Reject absent, ambiguous, mismatched or stale evidence. Synthetic fixture passes are separate evidence.

## Android and cross-project gates

The Android test APK requires independent comparison of the installed application's package ID, signing certificate SHA-256 and versionCode against the candidate, without uninstalling or replacing the installed app. BLE AI1 version, service/characteristic contract, frame bounds, reconnect/session semantics and permission-denial behavior must be tested against pinned firmware and Android heads. Pi/ESP32 remain separately gated until proven.

## Mandatory two-failure CI fallback

For the same workflow **and branch**, two consecutive completed failures (or repeated pre-job provisioning failure) trigger the approved public-safe private-firmware fallback route. Record both original run IDs, job provisioning status, fallback run ID and conclusion. If private Actions:read returns HTTP 403, classify fallback monitoring **BLOCKED**; do not mislabel a green diagnostics-only run as native firmware acceptance. Never publish private build contents or relax release gates.

## Recovery and owner authorization

Maintain a separate qFlipper recovery guide using verified official Momentum recovery media and exact supported steps; do not treat a CI pass as hardware success. Keep F7 flash and Android installation on HOLD until owner approval and physical testing. No protected merge or release-candidate promotion is authorized by this audit.
