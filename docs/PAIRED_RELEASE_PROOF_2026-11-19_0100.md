# Paired release proof — 2026-11-19 01:00 ET (public-safe)

Status: **HOLD**. This file is a read-only evidence handoff, not a release manifest or permission to install.

## Pinned observations

| Component | Exact observed ref | CI evidence | Acceptance |
| --- | --- | --- | --- |
| Android AI1 status regression | `08e1715b1be39c39bd2ee390e82cb557b3463c8f` | [Android run 44468213679](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44468213679): completed success | Build CI green; installed signer, versionCode and paired AI1 handshake **not verified** |
| Momentum stock SD starter | `60f18fc4791148a9c2e8f316caf2704af142973e` | [private firmware run 44459428313](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44459428313): completed failure | Combined native updater **not accepted** |
| Momentum AI1 TX scope | `dc97ec774867b3e580ad2bfd4db448f1df713cfd` | [private F7 run 44422497544](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44422497544): workflow success but native compile and TGZ jobs skipped | **Not a successful updater build** |
| Historical encrypted native F7 | public harness `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | [run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328): custom-firmware job success | Historical pinned proof only; not evidence for current candidate or physical device |
| Public F7 CRC gate | PR [#22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22), head `32f631c846db67d5f581887c00bbd06599b665c6` | open draft gate | Synthetic CRC fixtures alone cannot validate a real DFU image |

## Release acceptance (all required)

1. **Source provenance:** exact private firmware source SHA and upstream Momentum SHA, exact Android source SHA, BLE AI1 UUID/characteristic/authentication and frame contract version, dependencies, CI job identities. Do not publish private source or private build metadata beyond approved sanitized fields.
2. **Native F7:** actual compile and updater packaging jobs **executed and succeeded**, not skipped; verify `firmware.dfu` suffix and CRC on the actual native bytes, F7/C2 compatibility, TGZ member manifest and SHA-256 on the exact encrypted-only candidate via approved private-safe route. Historical DFU CRC 9-99 artifact is prohibited from retry.
3. **Android:** inspect built APK package ID, signer certificate digest, versionCode and artifact SHA-256 against the *installed* app's trusted owner-provided metadata in a private channel; no replace/uninstall. If mismatch, only opt-in isolated side-by-side test package with explicit approval.
4. **Paired BLE AI1:** verify matching GATT UUIDs, properties, authentication, CCCD lifecycle, reconnect/session epoch, request cancellation, and stock Momentum RPC separation against exact pinned revisions. Host tests do not establish physical handshake.
5. **Fallback:** two consecutive completed failing attempts in the *same repo + workflow + branch* or repeated pre-provision failure triggers approved public-safe private-firmware fallback; preserve run IDs and distinguish code failure from runner failure. Private Actions:read 403 = **BLOCKED**, not successful automatic fallback. No public private-source, binary, token, logs or personal diagnostics.
6. **Recovery:** maintain documented official qFlipper/DFU recovery steps and backup before any owner-authorized hardware attempt. Never auto-flash, auto-install, merge protected branches or deploy.

## Immediate owners / next actions

- Firmware owner: triage private integrated-update job in 44459428313; provide sanitized failure class, exact native-job and CRC/hash evidence for a new candidate only.
- Android owner: hand off APK artifact SHA-256, package/versionCode and **private** signer comparison; prove same-version safe upgrade or separate test package.
- Integration-testing owner: pin a compatible firmware/Android pair and run public-safe AI1 contract checks; update sole release ledger only on verified evidence.
- Pi/ESP32/radio/voice: remain optional until independent tested compatibility; do not fold prototypes into APK/F7 deliverables.

No physical Flipper test, release promotion, production merge, or actual fallback dispatch is claimed by this document.
