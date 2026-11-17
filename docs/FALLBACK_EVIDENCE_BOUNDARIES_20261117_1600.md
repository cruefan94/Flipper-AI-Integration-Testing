# Public-safe fallback evidence boundaries — 2026-11-17 16:00 ET

This is a **non-release audit**. Do not use this note to authorize an APK installation, native F7 flash, protected merge, or private-source publication.

## Newly observed live fallback

- Public integration-testing workflow run [44163834986](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44163834986) is **completed/success**, triggered by `workflow_dispatch`, at integration SHA `653d7ae4a7abab41742b0c7fb0c4d97f6a414fb1`.
- Its displayed title references private Momentum run `43694568473`. The jobs API reports `describe` success and `firmware / custom-firmware` success; protocol, contract, diagnostic, and Android jobs skipped.
- This is **evidence that one public-safe fallback workflow was dispatched and completed**. It is **not evidence** that the two earlier failing workflow/branch pairs (44024430141/44024439067 and 44024410032/44024430149) were automatically routed, nor evidence that private firmware compiled, passed native DFU CRC, or was tested on hardware.
- Do not infer that private Actions:read permissions were repaired: this observation alone does not establish successful private run-history access. An HTTP 403 remains **BLOCKED** for that specific access until separately proven.
- Required follow-up: inspect the sanitized fallback inputs and monitor decision records to link the exact private workflow ID, branch, consecutive failures, dispatch ID, classification and allowed public-safe payload. Record access result explicitly; do not publish source, binaries, logs, secrets or device diagnostics.

## Other exact-head evidence

- Android [44161971844](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44161971844) passed at `29b0c6c05e46011111a8f2d613926e2831741bc7`. This does not prove installed signer compatibility or hardware AI1 parity.
- Integration [44164138136](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44164138136) passed at `c3f132b49b4aba436727a3579360ee74896e3948`.
- Pi isolated readiness [44167236277](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44167236277) failed at `86e032b2a4fda7c74f28b69519e2b6b16525454d` in **both Python 3.11 and 3.12** during suite discovery/execution; requires job log diagnosis, not an infrastructure/billing assumption. This is one completed failing workflow attempt on this branch, not two.
- Momentum private source-contract [44170326007](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44170326007) failed at `2b933a4c7a1783e6322147c1ff085e520237f705`. Earlier different workflow at `03e96b84` failed; do not combine distinct workflow IDs for the two-failure threshold.
- Native encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) succeeded at `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8` and has encrypted, explicitly UNTESTED artifacts. Do not confuse this run's SHA with PR #22 current head `32f631c846db67d5f581887c00bbd06599b665c6`. Neither constitutes verified native firmware.dfu integrity or physical flash acceptance.

## Release holds (unchanged)

- **Android APK:** signer certificate comparison, versionCode upgrade behavior, consent and physical BLE acceptance pending. Do not uninstall/replace the existing app.
- **Momentum F7 updater:** native image framing, actual DFU suffix CRC, encrypted-only artifact identity, native TGZ/SHA256 manifest, qFlipper restore procedure and device owner approval pending. The CRC 9-99 failed updater is permanently excluded from retry.
- **BLE AI1:** require exact Android/F7 protocol revision, disconnect/CCCD/reentrancy and consent revocation cross-contract tests plus device handshake.
- **Pi, ESP32, Arduino, radio, voice:** optional components only until independently validated and accepted into a controlled candidate.
- **Fallback:** enforce two consecutive completed failures on the **same workflow and branch** or repeated pre-provision failure; preserve run IDs and safe payload boundaries. A green fallback workflow is not a green private firmware build.

Owner of the combined release ledger remains the integration-testing workstream. This branch is documentation only; no production code, secrets, firmware, APK or hardware changed.
