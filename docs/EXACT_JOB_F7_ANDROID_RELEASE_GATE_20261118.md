# Exact-job release gate: F7 and Android (2026-11-18 UTC)

Public-safe evidence only. This note contains no private firmware, keys, diagnostics, or firmware artifacts.

## F7: do not mistake a green workflow for a compiled updater

Private workflow [44238377245](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238377245) at source ref `1e7a412003af01653ff89dc03fee743a1e37a624` has overall SUCCESS, but its job inventory shows only **Private quick source checks** succeeded. **Full F7 AI1 firmware compile and strict update inspection** and **Private DRAFT release with direct native TGZ download** were both SKIPPED; its artifact list was empty. It is NOT release proof and must not be promoted.

Separate [44238360305](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238360305), same source ref, FAILED: Momentum integrated update and ESP32-S2 merged build failed; standalone FAP, WROOM reference and worker checks succeeded. Distinguish unrelated workflow IDs when counting consecutive failures. Do not use a standalone FAP or WROOM reference as an F7 updater substitute.

Gate: require exact source SHA, successful **non-skipped** native F7 compile, real `firmware.dfu` suffix CRC and header checks, manifest and SHA-256 for actual TGZ, encrypted-only delivery if using public fallback, controlled private draft identity, recovery instructions and owner-approved physical acceptance. Quarantine original CRC 9-99 artifact.

## Android: a new host-build recovery, not an approved update

[44214146838](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44214146838) at `9da29c4fce8e` completed the combined APK job successfully and produced an artifact named `FlipperAI-Android_20261118_run44214146838-a1_sha9da29c4f_ALLFEATURES-DEBUG-UNTESTED` (24,496,527 bytes). This supersedes the older two failures as **latest host build evidence on that branch**, but does not retroactively prove an authorized fallback dispatch for [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456).

Gate: compare installed and candidate signing certificates, applicationId, versionCode and upgrade semantics; a DEBUG-UNTESTED artifact is not an in-place upgrade candidate unless signer compatibility is independently established. Do not uninstall/replace the installed app. Explicit opt-in only for a separately identified test package, and no device install without owner approval.

## Contract and integration handoff

BLE AI1 service/characteristic UUIDs, framing, CCCD subscription behavior, consent revocation, disconnect/reconnect state, transport version and physical handshake must be tested against exact paired Android and firmware refs before promotion. Pi, ESP32, Arduino, radio and voice remain optional until proven against the candidate. Integration Testing alone owns the combined candidate ledger; feature branches hand off exact SHA, passing job, artifact identity, hashes, and blockers.

## Mandatory fallback

After two consecutive completed failures for the same workflow AND branch, or repeated pre-provision failure, use only an authorized public-safe fallback route for that component. Classify code vs infrastructure from jobs/logs. If dispatch or private Actions:read is missing, record BLOCKED and **no fallback run ID**. Never count distinct workflows together, never loop retries, and never publish private source, binaries, logs or credentials.

Status: both unified deliverables HOLD. No merge, flash, install, production deployment or physical validation implied.
