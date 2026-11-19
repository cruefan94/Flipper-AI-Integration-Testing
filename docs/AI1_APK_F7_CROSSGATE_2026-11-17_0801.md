# Cross-project AI1 / Android APK / F7 candidate handoff — 2026-11-17 08:01 ET

Public-safe coordination document only. No private firmware source, logs, binary, secrets, user device identifiers, or internal artifacts.

## Exact evidence reviewed

- Android [PR #61](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/61), reported exact SHA `d9421962`: [combined CI run 44059283296](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44059283296) passed. This does not establish installed-app signer compatibility.
- Android [PR #62](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/62) adds fail-closed host-only APK signing/manifest evidence tests; its own exact-head CI and actual APK certificate fingerprint must be recorded before promotion.
- Firmware [PR #41](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/41) and review-only [PR #42](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/42) are not release approvals. PR #42 identifies possible lost disconnect/CCCD events under nonblocking lock contention; require firmware owner to review and test state reconciliation.
- Public [F7 CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) tests synthetic DFU corruption. The actual AI1 [native build run 44023046497](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497) failed a real DFU header-size gate; **do not promote**.
- [Integration evidence PR #77](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/77) exact-head smoke [44069721369](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44069721369) passed; [PR #79](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/79) exact-head CI [44079479065](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44079479065) passed. These are release-gate tests/documentation, not hardware proof.

## Required single compatibility record before promotion

For **each** candidate, record: repository, immutable full commit SHA, branch, workflow name and run URL, job outcome, artifact name, artifact SHA-256, package/build version, AI1 protocol revision, dependency commits, and device-test status. Never infer artifact provenance from a green workflow alone.

### Android test APK gate

1. Verify built APK SHA-256, `apksigner verify --verbose --print-certs`, `aapt dump badging` package/version/label and exact workflow source SHA.
2. Compare signing certificate with *installed* app before any in-place upgrade. A mismatch means HOLD. Side-by-side test package is optional **only after explicit owner approval** and must not overwrite or uninstall the existing app.
3. Run host regressions for consent revocation during ASK, CCCD disable/re-enable, disconnect/reconnect, HELLO freshness, duplicate response suppression, and cloud opt-in. Confirm background service lifecycle on a real Android device before claiming acceptance.

### Native F7 updater gate

1. Record native updater TGZ SHA-256 and exact embedded `firmware.dfu` SHA-256; validate DfuSe framing, declared target/element sizes, suffix signature and CRC against **the same extracted image**.
2. Compare artifact manifest to exact private firmware commit through an authorized private-only route. Public CI may receive only sanitized pass/fail evidence; never source, binary, secrets, raw private logs or personal diagnostics.
3. Preserve Momentum functionality, recovery/backup steps and qFlipper procedure. The known CRC 9-99 updater is quarantined and must **never** be retried. No physical flash without explicit approval.

### Two-failure routing and provenance

Maintain a per-(repository, workflow ID, branch) consecutive-completed-failure counter, with exact run IDs and job-provisioning status. On two failures, or repeated pre-job failure, invoke only the approved PUBLIC-SAFE private-firmware fallback. If Actions:read/dispatch is 403 or unavailable, record **BLOCKED**, not SUCCESS; do not infer billing. Previously recorded qualifying Momentum pairs:
- workflow `420935082`: runs `44024430141`, `44024439067`
- workflow `414157517`: runs `44024410032`, `44024430149`

No newly authorized fallback dispatch is asserted here. Preserve failed-run links, fallback run ID if one exists, classification, and corrective step in the **private** [MAIN tracker #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).

## Integration disposition

Android candidate: HOLD (signer/device/AI1 paired acceptance). F7 candidate: HOLD (real header/CRC/hash/provenance). Pi/ESP32/radio/voice: optional until individually validated. This document changes no candidate branch or product code. No merge, flash, install or deployment.
