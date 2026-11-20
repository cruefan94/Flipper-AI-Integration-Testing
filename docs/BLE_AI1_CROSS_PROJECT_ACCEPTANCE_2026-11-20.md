# BLE AI1 cross-project acceptance and evidence gate (2026-11-20)

**Public-safe review only. No device identifiers, private source, keys, binaries, logs, or user diagnostics.** This checklist is not evidence that BLE pairing or firmware flashing passed.

## Evidence required before unified candidate promotion

| Gate | Evidence to record privately | Failure / HOLD condition |
|---|---|---|
| Contract | Android and Momentum exact source SHA; AI1 spec version; host-side conformance CI URL for each | Version disagreement, unknown SHA, or untested transport |
| Session identity | Paired device switch, stale GATT callback, reconnect epoch, disconnect and consent revocation regression IDs | Old device can receive or answer after switch |
| Payload boundary | Invalid UTF-8, overlong payload, malformed frame, timeout and fragmented message cases | Accepts malformed input, stale response, or cross-session response |
| Privacy | Cloud opt-in and cancellation tested without sensitive logs | Consent persists after disconnect or user switch |
| Native firmware | Current encrypted F7 artifact SHA-256, genuine firmware.dfu suffix CRC, C2 boundary, updater contents and recovery manifest | Any missing real-artifact proof, or prior CRC 9-99 image |
| Android upgrade | Installed signer SHA-256 vs candidate signer, package ID, monotonic versionCode, separate opt-in test APK | Signer mismatch, downgrade, unapproved installation |
| Physical | Device-owner-approved BLE pairing and disconnect/reconnect test with observable results | No physical verification |

## Two-failure fallback ledger

Count **consecutive completed failures for the same workflow AND branch**, not unrelated workflows. Record two run URLs, job provisioned (yes/no), first failing step, classification (source / runner / permissions / unknown), fallback dispatch URL and outcome. A repeated failure before provisioning also triggers fallback. Use only the approved public-safe private-firmware route. If private Actions:read yields 403, mark **BLOCKED** and request least-privilege permission; never export private source, firmware, artifacts, or logs to public. A green diagnostic-only fallback with native build skipped is **not** firmware acceptance.

Historical examples to investigate privately: F7 runs 44672488421 and 44672970526; S3 runs 44672488333 and 44672970355. Historical native run 43828499328 is not current-image evidence.

## Integration ownership and next actions

The integration-testing workstream alone maintains the combined candidate ledger. Firmware and Android owners hand off exact commit, dependency, passing CI, artifact identity and open blockers; do not modify their feature branches or a shared release branch concurrently. Review private firmware PR #23 and integration fallback PR #23 before any candidate changes. Check PR #75 exact-head host regression, Android PR #96 BLE device-switch regression and PR #97 cloud contract independently; their green checks cannot substitute for physical acceptance. Keep Android test APK and F7 updater on HOLD until all respective gates are evidenced. No production merge, flash, install or deployment.
