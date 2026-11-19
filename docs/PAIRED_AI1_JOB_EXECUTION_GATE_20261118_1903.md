# Paired AI1 release gate — 2026-11-18 19:03 America/Toronto

Public-safe evidence handoff. This file contains no private firmware source, artifacts, credentials or device logs. No release approval.

## Exact heads and job execution

| Component | PR / head | Workflow | Observed execution |
|---|---|---|---|
| Firmware | private PR #63 / `dc97ec774867b3e580ad2bfd4db448f1df713cfd` | [44422497544](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44422497544) | Quick source checks **success**; native F7 compile **skipped**; private TGZ release **skipped** |
| Android | public PR #77 / `6d43670ce38cfe5712904b6fc88f71f77b5fbd23` | [44424057383](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44424057383) | Combined APK build job **success**, not device verification |
| Integration classifier | public PR #146 / `5468a5208fd516eee5c40a06d9cff826f4eaf631` | [44417114232](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44417114232) | Offline failure-pair regression **success** |
| Historical encrypted F7 | prior pinned revision (not current candidate) | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) | custom-firmware job **success**, cannot be promoted to current head |

## Fail-closed release assertions

1. A green *workflow* with a skipped native compile is not native firmware proof. Require a completed **success** native compile job, matching commit SHA, nonempty updater archive, private artifact manifest and matching SHA-256.
2. Verify the **actual** `firmware.dfu` UFD suffix and whole-file CRC, not merely synthetic fixture tests. Retain C2 overlap/size safety checks and encrypted-only identity; never retry the known CRC 9-99 artifact.
3. Require Android package name, signer certificate digest and monotonically safe `versionCode` comparison against the installed application before proposing an in-place upgrade. Existing signer mismatch remains a hold. No uninstall, replacement or device installation.
4. Pin both exact heads and compare BLE AI1 service/characteristic UUIDs, ATT framing, authentication/CCCD policy, session-epoch invalidation, HELLO/ACK and stock Momentum RPC isolation. Host tests are not a physical handshake.
5. Pair failures by repository + workflow identity + branch; only two **consecutive completed failing** attempts or repeated pre-provision failure qualify. Exclude skipped/cancelled/queued jobs; check Actions:read access before claiming private fallback. A 403 is **BLOCKED**, not evidence of billing or success.
6. Private-firmware fallback must run only through the approved public-safe route. Do not upload private source, binary, credentials, logs or personal diagnostics to public artifacts.
7. qFlipper recovery and sanitized Termux diagnostics require owner-approved controlled physical testing, not inference from CI. Pi/ESP32/radio/voice remain optional until dependencies and compatibility are proven.

## Next actions / owners

- Firmware owner: resolve PR #63 regression and produce a non-skipped native F7 job at a pinned head with private CRC/hash/C2 evidence.
- Android owner: provide APK artifact digest, package/versionCode/signer evidence and paired AI1 contract fixture for PR #77.
- Integration owner: run exact-pair contract checks after both source heads pass; update sole canonical release ledger and keep both deliverables on HOLD pending device-owner approval.
- Tracker: [private MAIN issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5).

No hardware flash, install, protected merge or release promotion authorized.
