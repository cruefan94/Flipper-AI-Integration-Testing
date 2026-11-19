# Cross-workstream exact-head acceptance delta — 2026-11-19 11:00 ET

Public-safe, read-only evidence handoff. This document is **not** the combined release candidate ledger; the integration-testing workstream remains its sole owner. No private firmware source, artifacts, credentials or personal diagnostics are included.

## Newly established evidence

- **Pi dashboard exact suite recovered:** PR [#181](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/181), head `74e414bde06ce139ba8193d3e5e2b3ba513f8baf`. The dedicated [exact-suite run 44551764387](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44551764387) completed successfully, including its "Run exact dashboard and launcher tests with zero skips" step. [Run 44551736155](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44551736155) also succeeded at the same head. The workflow's minimum-test-count assertion must be reviewed before claiming a specific count; no Pi device testing was performed. This supersedes the earlier **CI discovery failure** hold, but **not** Pi hardware acceptance.
- **Android latest host build:** PR [#85](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/85), head `12fd30bfa320b9a7e690e823031077a8bd5c9e65`. [Run 44559371207](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44559371207) passed source/JVM/security regressions, debug APK build, integrity/provenance generation and upload. This is **not** evidence of installed-app signing continuity, safe in-place upgrade, or device BLE reliability. Earlier run 44559341877 was **cancelled**, not a completed failure for the two-failure policy.
- **Firmware current draft:** PR [#70](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/70), head `067e5a23e8e6d668a2f0d64bcd29cc9e63927bd5`, adds fail-closed regular-file validation to synthetic C2 image-size auditing. It does **not** verify the authoritative physical C2 boundary, linker sections, or safe native F7 updater. The private Actions run listing still shows the three failed combined-build runs 44481566067, 44481581444, 44481593032 on the same branch; avoid infinite retries or assuming a billing cause.
- **Historical native CRC candidate:** [run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) passed the older encrypted private firmware job. Historical success is not exact-head CRC/flash proof. [CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains draft. Never retry the updater that failed on device with DFU CRC 9-99.

## Release candidate handoff (no promotion)

| Gate | Evidence still required |
| --- | --- |
| F7 Momentum .tgz | Exact private source SHA; authoritative C2/linker layout and flash-safety acceptance; actual embedded firmware.dfu suffix CRC; internal updater SHA-256; encrypted-only identity; qFlipper recovery instructions |
| Android test APK | Exact artifact hash, package ID, signer certificate fingerprint comparison against installed app, monotonically increasing versionCode, user-approved side-by-side alternative if signer differs |
| BLE AI1 | Versioned characteristic UUID/role, framing, auth, reconnect and error contract parity on exact paired commits, then owner-led hardware handshake |
| Pi gateway | Dedicated exact suite passing (now supported at PR #181), followed separately by safe read-only on-device acceptance |
| ESP32 / radio / voice / Termux | Independent provenance, security, compatibility and opt-in gates; never imply inclusion based on standalone CI |

## Two-failure fallback and privacy

After two **consecutive completed failures on the same workflow and branch**, or repeated pre-run provisioning failures, use only the approved encrypted public-safe private-firmware route. Record exact failed run IDs, fallback run ID, outcome and remediation. If Actions:read or dispatch permissions return 403, label the specific coverage **BLOCKED**; never publish private source, binary, logs, secrets or personal diagnostics. The previously recorded encrypted fallback [run 44491711278](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44491711278) succeeded for the earlier firmware sequence, but is not proof that every future fallback can be dispatched.

No production merge, hardware flash, APK install, production deployment or unified candidate promotion is authorized by this document.
