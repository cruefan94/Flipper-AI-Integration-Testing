# MAIN integration evidence closure — 2026-11-19 19:00 ET

This is a public-safe, documentation-only evidence handoff. It does not certify firmware, device, Android upgrade, or paired BLE operation.

## Current exact-head evidence
- Android PR #89: `c6e83950428476afe7d8c29c0f60400ac19b7b03`; Actions [44632497713](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44632497713) completed successfully. Debug APK compilation does **not** establish upgrade-signature continuity.
- Pi/qFlipper read-only backup evidence PR #198: `a260c6d3443086b7903432069347b476ab0ae06d`; exact tests [44635265115](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44635265115) passed. No physical recovery proof.
- Receive-only radio URL preflight PR #199: `f27ccaab92c150257ad3d4a7b9dbacd0b5cfd722`; isolated [44637340465](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44637340465) passed. No feed reception or hardware proof.
- Momentum PR #71: `238a54bfc0b1708a827d489cee5d43197871bfb3`; same-workflow failures [44568518970](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568518970), [44568544991](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44568544991). Root cause not classified.
- Historical encrypted native run [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) passed at `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`, **not** current head.
- Prior public-safe fallback [44587016728](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44587016728) passed diagnostics only; firmware/Android/protocol jobs were skipped. Do not treat as native repair.

## Promotion evidence required (fail closed)
| Gate | Exact evidence required | Current verdict |
|---|---|---|
| F7 native | Pinned private source SHA, authoritative C2 boundary, native compiler success, real `firmware.dfu` suffix CRC, internal updater SHA-256, encrypted-only identity, recoverable qFlipper path | HOLD |
| Android test APK | Pinned source SHA and artifact SHA-256, signer certificate digest of installed vs proposed package, same application ID, monotonic versionCode, safe side-by-side route if signer differs | HOLD |
| BLE AI1 | Versioned common packet schema; paired firmware and Android commit SHAs; 12-case acceptance matrix including stale GATT/reconnect/background; hardware handshake separate from stock Momentum RPC | HOLD |
| Pi / ESP32 / radio | Exact CI test counts, physical safety and compatibility checks; optional modules remain separate until proven | HOLD |
| Remote diagnostics | Termux/GitHub bridge must redact secrets, BLE addresses, paths and personal logs; read-only by default | HOLD |

## Two-failure response
After two consecutive completed failures for one workflow and branch, or repeated pre-provision failures, invoke the approved public-safe fallback. Record both private run IDs, branch/SHA, failure classification (code vs runner vs permissions vs unknown), fallback dispatch ID and exact job outcomes. A successful diagnostics-only fallback does not clear native release holds. If Actions:read or dispatch permission is absent, record **BLOCKED**; never claim dispatch. No unlimited reruns or relaxed gates.

## Safe installation/recovery sequence (not authorized to execute)
1. Preserve existing Android app/data; never uninstall to overcome a signer mismatch. Compare signer and versionCode before any owner-approved install.
2. Preserve official working Momentum and SD backups. Never retry the known CRC 9-99 artifact.
3. Only after genuine native artifact validation and explicit owner approval, use documented qFlipper recovery and device-specific backup checks; CI alone is not hardware proof.

Integration-testing owns the single combined candidate ledger. Feature branches must hand off tested SHA, CI run, artifact provenance and blockers; no shared release-candidate branch mutations from parallel tasks.
