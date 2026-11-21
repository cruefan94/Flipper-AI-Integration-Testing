# Android active-GATT regression: exact-head integration handoff (2026-11-20 23:04 ET)

This is PUBLIC-SAFE metadata only. No firmware source, binaries, credentials, device logs or installed-app identifiers.

## Evidence
- Android PR #104 (head `581b423bc2c9e82ac64307c174cff56983963c40`) guards against delayed BLE recovery replacing an active GATT connection. Its workflow #44863047645 failed in host regressions; the PR #105 description identifies two stale static assertions. This is a **test failure on #104**, not evidence of hardware failure or runner billing.
- Android PR #105 (head `084a7221aa7d429ac26d53c71569e32769c252af`) changes regression assertions to require the stronger active-GATT guard. Exact-head combined APK workflow #44863378694 completed **success**. PR #105 targets PR #104, not production main; both remain draft/unmerged.
- Integration PR #266 (head `a64747558da07c45f1fb0899884ad5f9e211b278`) public smoke workflow #44859200807 completed **success**. This verifies documentation CI only, not an updater.
- Private Momentum PR #75 (head `a37868b100dfdac4b575b3ff194b8e69155e9061`) failed same-workflow runs #44755541063 and #44755560160. Preserve the mandatory two-failure route. Earlier public-safe fallback #44782519310 performed diagnostics only; it did not compile native S3 firmware. Private Actions:read HTTP 403 means automated private-history coverage is **BLOCKED**, not successful.

## Promotion dependencies
1. Integration-testing ledger owner must pin both Android PR #104 and child PR #105 and confirm combined tests against the intended merge tree. A passing child PR does not prove the parent branch itself passes or that production main contains the fix.
2. Compare APK package ID, installed-app certificate SHA-256, candidate certificate SHA-256, versionCode and data-preserving update eligibility **privately** before offering any update. Do not uninstall or overwrite the existing app. Side-by-side test APK requires owner opt-in.
3. Compare Android BLE AI1 characteristic/service identifiers, protocol framing, authentication, error states, reconnection epoch and readiness semantics with exact firmware/S3 refs; stock Momentum RPC is not AI1 readiness. Hardware pairing and background-reconnect tests remain pending.
4. Native F7 encrypted build #44782522608 passed compilation/upload only. Before any release: privately prove exact source SHA, real extracted `firmware.dfu` suffix CRC, updater and inner-file SHA-256, C2 boundaries, archive identity, recovery instructions and physical owner consent. Never retry CRC 9-99 artifact.
5. No production merge, hardware flash, install or release promotion on the strength of these host checks.

## Two-failure policy
For each exact workflow+branch, count consecutive completed failed attempts; reset on success, do not count queued/pending. After two failures (or repeated pre-job provisioning failure), use only the approved PUBLIC-SAFE private-firmware fallback. If private Actions:read is inaccessible, report **BLOCKED** with failing IDs and required permission repair. Do not disclose private artifacts or classify billing without evidence.
