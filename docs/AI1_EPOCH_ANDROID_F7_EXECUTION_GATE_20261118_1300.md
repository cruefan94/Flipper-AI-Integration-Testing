# AI1 reconnect epoch / native F7 execution evidence — 2026-11-18 13:00 ET

Public-safe integration handoff only. No private firmware code, binaries, keys, device identifiers or personal diagnostics.

## Exact observed heads and executed jobs

| Component | Source PR / SHA | Completed workflow | Executed evidence | Promotion |
|---|---|---|---|---|
| Android AI Satellite | [PR 75](https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/75) / `f4c60535788bd18b74b6888facae001d9eb3676a` | [44361989778](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44361989778) SUCCESS | Host regressions, debug APK build, integrity/provenance generation, artifact upload all succeeded | HOLD: debug APK is not a safe installed-app upgrade; signer/versionCode/device acceptance missing |
| Momentum AI1 | [PR 60](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/60) / `08b144215890d7a6c4d61b79182debb8f0ac7fab` | [44349821320](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44349821320) SUCCESS | Host reconnect/RX-frame contract only | HOLD: no paired device handshake |
| Momentum F7 candidate | same PR 60 / same SHA | [44349821257](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44349821257) SUCCESS (workflow aggregate) | Private quick checks passed; **Full F7 firmware compile and strict update inspection SKIPPED**; **TGZ draft publishing SKIPPED** | HOLD: no current native F7 TGZ evidence |
| Integration smoke | [PR 136](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/136) / `bb7da95f504bc11187dca16ab9d7a1372ec89675` | [44354380858](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44354380858) SUCCESS | Public smoke and offline fallback tests; explicit no-firmware-build step | Not native evidence |
| Historical encrypted F7 | integration source `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` | [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) SUCCESS | Historical run only | NOT the current firmware candidate |

## Paired AI1 acceptance matrix (not yet proven)

1. Pin **both** source SHAs and a declared AI1 API/spec version. Compare GATT UUIDs, characteristic properties, CCCD authentication order, frame format/length limits, session epoch invalidation, reconnect replay prevention and error/status semantics. A host test in one repository is not proof of parity.
2. Capture a public-safe, sanitized cross-component test result tied to both SHAs. Never publish private Momentum source, raw firmware artifacts, BLE addresses or user logs.
3. Confirm native F7 compile and TGZ inspection steps actually executed (not skipped); check C2 memory boundary, real firmware.dfu suffix CRC, encrypted-only artifact identity, per-file SHA-256, and recovery manifest in private CI. The old CRC 9-99 updater is permanently quarantined.
4. Compare candidate APK package ID, signer certificate digest and versionCode against the installed app via owner-authorized **read-only** preflight. No uninstall, replacement, install or device data changes. Debug signing alone is not upgrade proof.
5. qFlipper recovery remains a written/bench-validated gate, not permission to flash. Pi/ESP32/radio remain separately gated until exact source, safety and compatibility evidence exists.

## Two-failure fallback and attribution

For two consecutive **completed failing attempts on the same workflow and branch**, or repeated pre-runner failures, use only the approved public-safe private-firmware fallback. Log triggering run IDs, workflow/branch/head, dispatch ID, actually executed job results and permission status. Distinguish compilation failure, skipped jobs and runner infrastructure failures. Historical [44288673073](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44288673073) ran a firmware fallback job, but exact trigger attribution is still unverified. On private Actions:read HTTP 403, label BLOCKED; never imply fallback was executed.

## Handoff and next action

Firmware owner: deliver a non-skipped C2-safe native F7 updater build and private real-artifact CRC/hash attestation at exact SHA. Android owner: deliver read-only installed/candidate signer+versionCode evidence and paired AI1 epoch/GATT contract. Integration-testing owner: reconcile both exact SHAs and job outcomes in the single candidate ledger, with no shared release branch mutations until acceptance. No protected merges, device flashing, APK installs or production deployments.
