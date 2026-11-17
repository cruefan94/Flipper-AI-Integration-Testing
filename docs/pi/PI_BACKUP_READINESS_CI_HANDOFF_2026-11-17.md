# Pi qFlipper backup readiness — isolated CI handoff (2026-11-17)

Scope: Raspberry Pi 4B / first-generation Pironman side-project only. This is a source/CI handoff, not hardware validation, restore authorization, or release promotion.

## Exact verified evidence
- Source branch: `fix/pi-backup-ci-import-root-20261117-1607`
- Tested head: `90011f7ebd325616883f88c8e7ec31877af2e2cc`
- Dedicated backup/readiness run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44176567893 — completed success, both Python 3.11 and 3.12 jobs; their 'Compile isolated Pi backup modules' and 'Discover and execute backup and readiness regression suites' steps completed successfully.
- Public smoke: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44176567867 — completed success.
- Prior failing discovery run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44167236277 — test-discovery/import-root failure, not runner provisioning. The corrected exact-head run passed. No second consecutive completed failure was established for this branch/workflow; no fallback dispatch claimed.
- PR: https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/98 (stacked on #96 and earlier backup-readiness work).

## Integration gates
1. Reconcile stacked PR #80–#98 dependencies and review actual changed files before any promotion. Passing isolated CI does not prove physical restore safety.
2. Integration-testing workstream alone owns unified release ledger and candidate branches. Hand off this exact tested ref and CI links; do not independently edit shared candidates.
3. The backup verifier/readiness interface is Pi-side optional; **not** incorporated into Android test APK or native Momentum F7 updater .tgz.
4. Never retry known failed DFU CRC 9-99 updater; no hardware flash, real backup restore, production merge, or APK replacement.
5. Private Momentum Actions visibility HTTP 403 remains **BLOCKED** until Actions:read permission is configured and verified. Preserve two-failure PUBLIC-SAFE fallback with no private source/artifacts/secrets in public.
6. Device acceptance requires real Pi/qFlipper evidence, read-only backup verification, redaction checks, and explicit owner approval before any restore.

## Other Pi workstreams (tracked; unchanged in this change)
- Pironman RGB/fan/OLED reversible controls; do not disturb cooling services.
- 10-second read-only Pi/Flipper/ESP32 monitor.
- Pi OS health, memory/browser/cleanup tooling.
- qFlipper USB diagnostics and backup/recovery workstation (current focus).
- Pi-local existing-runtime AI.
- Opt-in secure phone-to-Pi remote access.
- Pi BLE/Wi-Fi/USB gateway adapters.

Next: review dependency chain and privacy-contract test discovery; seek exact-head passing CI on a reconciled non-production integration branch before integration-testing owner considers candidate promotion.
