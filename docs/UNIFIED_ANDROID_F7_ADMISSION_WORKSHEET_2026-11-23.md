# Unified Android APK / Momentum F7 admission worksheet (2026-11-23)

Status: **HOLD**. Public-safe instructions only; no production release authorization.

## Immutable evidence tuple (one row per candidate)
Record privately where needed: component; repository; exact source commit; workflow run and job ID; job conclusion; artifact ID; artifact digest; extracted file SHA-256; build variant/version; contract version; hardware validation; owner approval. A workflow's public head SHA is **not** a private firmware source SHA. A green workflow with skipped component jobs is not a combined integration pass.

## Android signer and data preservation gate
1. Obtain candidate APK via an authorized route; do not replace the installed app.
2. In a private trusted workstation run `apksigner verify --verbose --print-certs candidate.apk` and `sha256sum candidate.apk`. Record certificate SHA-256, package name, versionCode and versionName using `aapt dump badging candidate.apk` or equivalent build tooling.
3. Compare the certificate SHA-256 and package name against the **installed** application's verified signer and package. A different signer with the same package name is **NOT** an in-place update. Also require a monotonically increasing versionCode for an upgrade. Android signing lineage/rotation must be independently verified where used.
4. If compatibility is unproven, retain the existing app and data. A side-by-side build requires a distinct applicationId and owner opt-in; never uninstall or overwrite automatically.
5. Require BLE AI1 UUID, authenticated read/write/notify roles, framing, protocol version, request correlation, timeout, disconnect/reconnect and negative-case parity against the exact F7 source commit. Worker-only tests do not prove APK parity.

## F7 updater integrity and qFlipper recovery gate
1. The previously failed DFU CRC 9-99 updater is permanently quarantined; do not retry it.
2. Preserve encrypted artifact only through the approved access-controlled route; keep ciphertext and any decrypted firmware outside public repositories, CI logs, and public artifacts.
3. After authorized private decryption, record `sha256sum updater.tgz` and per-member SHA-256. Validate archive structure against the pinned Momentum updater format, real `firmware.dfu` suffix CRC, and exact private firmware source SHA. Synthetic fixture CRC passing is not proof of a real updater.
4. Confirm the exact F7 target, firmware version, intact original Momentum features, storage/SD backup and official qFlipper recovery procedure **before** any owner-approved hardware test. A CI pass never authorizes flashing.
5. For recovery preparation, use an official compatible Momentum release and official qFlipper documentation, confirm USB cable/data connection and backup availability, and do not perform recovery or DFU actions without the owner's explicit approval.

## CI fallback / escalation
For two consecutive completed failures on the **same workflow and branch**, or repeated failure before provisioning, preserve both run IDs and exact commit, distinguish source/test from runner/permissions failure, and use only the approved PUBLIC-SAFE private-firmware fallback. Require a real dispatched fallback run ID and its completed job conclusions. A 403 or unavailable dispatch permission means **BLOCKED**, not dispatched; never rerun indefinitely. PR #90 native-protocol failures: 45219142235 and 45219142350 at 92cd48cee0abd3efbbe2d2d5647c556b833e4655. PR #89's native fallback run 45160017502 is not evidence for PR #90.

## Current non-promotable evidence
- PR #89 encrypted artifact 14811097270 from run 45160017502; expires 2026-11-30 11:03:29 UTC. Encrypted ZIP digest is not decrypted updater/member digest. Real firmware CRC and source SHA unverified.
- Android Worker PR #150 is synthetic contract coverage, not an installed, signer-compatible APK or BLE device pass.
- PR #90 fallback: qualifying two failures, dispatch not yet confirmed.
- Pi/ESP32/radio/voice remain optional until exact contract, safety, dependency and build gates pass.

Do not merge protected branches, flash, install, deploy, publish private source/firmware, or promote either candidate without explicit owner approval and the above evidence.
