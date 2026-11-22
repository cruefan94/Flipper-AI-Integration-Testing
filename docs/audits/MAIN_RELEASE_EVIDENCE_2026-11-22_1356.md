# MAIN integration evidence checkpoint — 2026-11-22 13:56 America/Toronto

Scope: PUBLIC-SAFE status and fail-closed release gate only. No private source, firmware binary, credentials, logs, device identifiers, or personal diagnostics.

## New exact-head evidence
- Android PR #131, head `05010b24c6acd6d9b627a52ab336dcdcda374ae0`: combined APK workflow **45057052798 SUCCESS**; isolated APK metadata workflow **45057052878 SUCCESS**. This is a test-vector correction for Java escaped Unicode/control inputs; not proof of device BLE or signature-compatible upgrade.
- Android PR #130 combined run **45051767233 FAILED** at host regression; isolated metadata **45051767238 SUCCESS**. The follow-up #131 fixes the escaped negative fixtures; do not count #130 as passing.
- Integration PR #374, head `a1b100e78af33aef25bd814df13a2e5221348b44`: smoke workflow **45052189636 SUCCESS**. This validates documentation/smoke only.
- Momentum FAP PR #86 same-workflow failed pair **45008101314**, **45008110405**; public-safe fallback native firmware runs **45039819048**, **45039817534** and protocol run **45039820581** previously reported successful. Fallback firmware compilation is **not** a passing standalone FAP build.
- Historical encrypted native F7 run **43828499328** is historical build evidence, not present candidate CRC/hash verification.

## Promotion conditions — all must be separately proven
1. Android: record APK SHA-256, package name, versionCode, certificate SHA-256 of current installed app and proposed APK; require same package and certificate and increasing versionCode before any in-place update. A separately named test APK needs explicit owner approval; no uninstall.
2. AI1 BLE: pin both source SHAs and spec revision, run cross-language frame/length/timeout/error vectors and real stock Momentum RPC interoperability tests. CI success alone is not hardware proof.
3. Standalone FAP: require successful native external FAP compile for exact pinned Momentum target and ELF/API compatibility, artifact hash and install/recovery procedure. Native *firmware* fallback cannot substitute.
4. F7 TGZ: inspect actual `firmware.dfu` suffix CRC, internal updater checksums, archive SHA-256, source SHA, encrypted-only artifact identity and qFlipper recovery path. **Never reuse CRC 9-99 updater.**
5. Public-safe fallback: on two consecutive completed failures for the same workflow+branch, or repeated pre-job failure, invoke only approved private-safe route; record source run IDs, fallback run IDs, exact job conclusions and skipped jobs. Treat 403/Actions:read as BLOCKED. Do not publish private material.
6. Pi/ESP32/Arduino/radio: optional until separate electrical, protocol, lawful receive-only and device acceptance evidence exists.

## Next integration handoff
- Android owner: supply PR #131 APK artifact hash and signing metadata, with secrets excluded.
- Firmware owner: supply PR #87 native FAP compiler diagnostics via private route and exact-head build proof.
- Integration owner: reconcile the canonical combined release ledger without concurrent branch mutation; keep both deliverables on HOLD.
