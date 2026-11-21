# qFlipper / F7 native updater: preflight and recovery evidence (public-safe)

Status: **HOLD**. This checklist is not a flash authorization. Never retry the known failed DFU CRC 9-99 image. Do not replace an installed Android APK with a different signing certificate.

## Read-only preflight — owner-operated, no flashing

1. Identify the intended native **F7 Momentum** updater by an exact private firmware source SHA, pinned upstream Momentum SHA, build workflow/run ID, and exact artifact name. A successful workflow or ESP32-named archive is not enough.
2. In a **private** build verifier, inspect the actual extracted `firmware.dfu` (not a synthetic fixture). Verify the 16-byte `UFD` DFU suffix, expected target/size, and whole-file CRC32 residue `0xffffffff` according to the pinned updater verifier. Fail closed on missing, truncated or ambiguous DFU input.
3. Independently hash the exact encrypted transport artifact and the decrypted `.tgz`, `firmware.dfu`, updater manifest, and every required internal payload. Keep artifact bytes, filenames revealing private design, decryption material, firmware source and diagnostic logs in private storage.
4. Verify F7 hardware target, updater manifest, C2 address ranges, upstream Momentum compatibility and BLE AI1 contract version against the exact Android candidate. Record test command, exit code, tool version and SHA in a **private** attestation.
5. On the owner's Pi/desktop, **read-only** verify qFlipper opens and recognizes the device, current firmware/version, USB stability and the owner's backup/restore route. Do not start Update/Repair/DFU as a diagnostic test.
6. Verify a documented recovery route and backups before requesting explicit owner approval for any installation. Recovery feasibility is not proven until owner-supervised testing; no automatic fallback flashing.
7. For Android, compare installed APK and proposed APK package identity, signing certificate digest, monotonically increasing versionCode and app-data-preserving upgrade path; a mismatch requires a separately identified opt-in test package, never uninstall/replace.

## Minimum private acceptance record

| Field | Required evidence |
|---|---|
| Firmware and Momentum source | Exact 40-hex SHAs and private build/run URLs |
| Build identity | Workflow run ID, job ID, pinned toolchain, artifact name/type |
| Integrity | SHA-256 of encrypted artifact, decrypted tgz, extracted firmware.dfu and manifest |
| Real DFU | UFD suffix bytes/length, independently calculated whole-file CRC, verifier version and pass |
| Target safety | F7 identity, C2 memory boundaries, updater manifest compatibility |
| BLE AI1 | UUID/roles/authentication, frame and UTF-8 bounds, protocol version and cross-component test run |
| Recovery | Owner-confirmed qFlipper detection, backup existence, documented rollback/repair plan |
| Android | Installed and candidate signer fingerprints, package IDs, versionCodes, upgrade disposition |
| Physical acceptance | Explicit owner consent, test date, device result; absent until actually tested |

Do not publish the completed private record or its binary/log attachments in this public repository. A public-safe ledger may say only PASS / FAIL / BLOCKED / UNVERIFIED, cite public-safe run IDs, and identify missing evidence categories.

## Current evidence boundary (2026-11-20)

- [Historical native run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): completed build; uploaded encrypted ESP32/integration-preview candidates. This is **not** unambiguous current F7 release attestation.
- [Encrypted native run 44782522608](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44782522608): compiled native firmware and uploaded `encrypted-flipper-ai-mobile-native-tgz-UNTESTED` (12,650,072 bytes); actual DFU CRC, internal SHA-256 and private source SHA have not been independently recorded here.
- [Offline evidence gate PR 263](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/263): synthetic release-evidence validation only; no binary inspection or hardware authorization.
- [Private Phase 1 release gate](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and [public-safe fallback PR 23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23) remain authoritative.
- S3 AI1 same-branch failures: [44755541063](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063), [44755560160](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160). The mandatory public-safe fallback diagnostics are not native board acceptance; private Actions:read HTTP 403 must remain **BLOCKED** until corrected. Do not infer billing or source root cause.

## Gate decision

**HOLD** both unified deliverables until exact tested commits and artifact attestation exist. No protected merges, production release, physical flashing, APK installation or private-source publication from this checklist.
