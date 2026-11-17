# Native F7 encrypted runner: verified job success, device release still held (2026-11-17 17:02 ET)

## Evidence observed via GitHub Actions API
- Integration PR #66 public head: `fc6c9e462295ff2fdfae9a481580965d5c408e55`.
- Native private-source encrypted compile: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225 — completed **success**. Job `custom-firmware` completed its private-source pin, GATT checks, native Momentum compile, actual F7 DFU framing/CRC gate, updater archive verification, encrypted-only artifact upload steps successfully.
- Exact-SHA source-only contract: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180975302 — completed **success** on same public commit.
- Earlier real DFU failure: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497. Do not reuse previously failed CRC 9-99 updater.
- Android combined build https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277 failed at source/JVM/security regression; APK build and artifact upload skipped. This is on `feature/ai1-background-service-dispatch-20261116`, distinct from green Android PR #65 `29b0c6c0` run 44161971844.

## Fail-closed release boundaries
1. Native job step success is meaningful host evidence **not physical Flipper success**. Before candidate promotion, privately verify exact pinned private firmware commit SHA against the run's attestation, original updater .tgz member hashes, full SHA-256 and encryption recipient identity. Keep all private values, binaries, and logs in approved private-only records. Do not publish encrypted firmware artifacts or decryption secrets in this public repository.
2. No flash until explicit owner approval, qFlipper recovery backup and device-specific validation. Do not retry the known CRC 9-99 artifact.
3. Android remains HOLD: failed latest combined workflow, missing proven installed-versus-candidate signing certificate match and safe upgrade path. No uninstall, replacement, or auto-install.
4. BLE AI1 GATT/API parity and real authenticated BLE phone↔Flipper handshake remain unverified. No end-to-end claim.
5. Two consecutive failures on **same workflow and branch**, or repeated pre-run provisioning failure, trigger approved public-safe fallback. Record source run IDs, fallback IDs and classification; never infer billing from a failure. A successful manual fallback does not prove automatic routing or private Actions:read permission.
6. Pi/ESP32/radio remain optional pending exact tested commits and compatibility acceptance. Release candidate ledger ownership stays with integration-testing; do not modify another task's shared candidate branch.

## Next action
Review the successful native job's private attestation and encrypted artifact manifest in the authorized private route; compare exact source SHA and SHA-256, then pass only safe evidence references to canonical private tracker #5. Diagnose Android 44181012277 host regression without changing its owner branch. Keep both coordinated deliverables on HOLD.
