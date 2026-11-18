# Public-safe cross-project CI evidence checkpoint — 2026-11-17 20:00 ET

This document contains only public-safe GitHub workflow references, commit IDs, and release gates. It contains no private source, artifacts, credentials, logs, or personal diagnostics.

## Fresh exact-branch failures

- Android `feature/ai1-background-service-dispatch-20261116`: completed failures [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) at `1471d5898ecfad6303d397cbb7501311d2ebce4c` and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456) at `7aae70bd7fd7dc93a4f452025d5fdb960b84d8df`. Same branch, two completed failures: **mandatory public-safe fallback evaluation is triggered**. Confirm workflow identity and completed job outcomes before dispatch; do not equate unrelated workflows or infer root cause without job logs. No fallback dispatch is claimed here.
- Momentum `feature/momentum-ai1-next-flash-20261117`: [44204918856](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44204918856) completed success on attempt 2 at `8201647c822896a4dbc8fe00547f94aabb633de9`; [44205741755](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44205741755) completed failure at the same SHA. Different workflow IDs may have different gates: **do not call this a consecutive failure pair without verifying workflow ID and branch**.
- Native encrypted F7 [44180961225](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225): completed success on attempt **2** at public integration SHA `fc6c9e462295ff2fdfae9a481580965d5c408e55`. Pin attempt number; it is not physical flash approval. Previous CRC 9-99 image remains quarantined.
- Public-safe integration [PR 66](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/66) at `4ab720ad23ca20df484e5f5468aa3bdb43f7748e` has passing checks including [44205085626](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44205085626); distinguish public contract checks from private source provenance and native artifact identity.
- Pi suite inventory [PR 103](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/103) at `d943c317284337b6ef0d24e923825de26c2f21ee` has passing checks [44206442543](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44206442543), [44206442542](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44206442542).

## Mandatory fail-closed routing

1. Group completed failures by exact repository, workflow ID and branch, including attempt numbers. Count only consecutive failures; a completed success resets that workflow+branch streak.
2. On two consecutive completed failures or repeated pre-provision failure, use only the approved public-safe integration fallback. Send **references and sanitized metadata only**, never firmware source, firmware binary, tokens, secrets, raw private logs, or personal diagnostics.
3. If private Actions:read or workflow dispatch is unavailable (including HTTP 403), mark **BLOCKED** and request permission correction. A green public fallback contract check is not proof of automatic dispatch. Preserve failing and fallback run IDs and job-level cause classification; do not guess billing.
4. No indefinite reruns, relaxed gates, production merges or device changes.

## Unified release holds

| Candidate | Current hold | Required promotion evidence |
| --- | --- | --- |
| Android test APK | HOLD | Passing exact-head combined build, version/package identity, installed-vs-candidate signing certificate match or explicitly approved side-by-side distinct package, no data loss, AI1 parity |
| Momentum F7 native updater .tgz | HOLD | Exact private source SHA, real firmware.dfu suffix CRC and framing, updater SHA-256 manifest, encrypted-only artifact provenance, qFlipper recovery plan, physical owner acceptance |
| BLE AI1 | HOLD | Firmware/Android contract revision, command/response/notification parity, reconnect and consent fail-closed tests, real paired device handshake |
| Pi/ESP32/radio | OPTIONAL | Independently passing source/CI plus safe integration acceptance |

Reference owner-approved private release blocker matrix [Momentum PR 23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and public-safe fallback coverage [Integration PR 23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23). Integration-testing owns the combined release ledger. No promotion, flash, install or merge is authorized by this document.
