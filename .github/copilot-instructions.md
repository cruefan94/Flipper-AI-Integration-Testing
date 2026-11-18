# GitHub Copilot instructions — public Flipper AI integration testing

## Scope and publication security
- Public CI/test harness for private Flipper AI Momentum firmware and public Android AI Satellite. Respect the boundary: `cruefan94/Flipper-AI-Momentum-` is PRIVATE; `cruefan94/Flipper-AI-Android-Satellite` is public. This repo may run private-source builds **only** in an isolated, correctly authorized workflow that publishes ENCRYPTED firmware and public-safe summaries. Never expose private code, plaintext binaries, private diffs, decryption passwords, GitHub secrets, device identifiers, personal prompts, or raw private logs.
- The default branch may lag the active feature branch; inspect current PRs and workflow revisions. A public-success badge is NOT evidence that the target private firmware booted on a real Flipper.

## Highest-priority review checks
1. Exact private source revision: pin all 40 hex SHA characters; verify the checked-out private HEAD equals the requested SHA; fail closed on changed branch/ref, unexpected dependency revisions, or nonmatching provenance.
2. F7 firmware packaging: compile the intended Momentum target, inspect real native `firmware.dfu` structure and CRC, validate embedded `update.fuf`, `updater.bin`, native F7 `.tgz` contents and per-file SHA-256. Synthetic-test success alone is insufficient.
3. Encryption: require approved GitHub Actions secrets, use the exact OpenSSL AES-256-CBC / PBKDF2 / 250000-iteration parameters where specified, verify decrypt roundtrip and package manifest before removing plaintext, and upload only the encrypted delivery plus safe checksums. Keep secrets out of PR text, job summaries, `set -x`, command arguments, and artifacts. **Never automatically weaken/remove encryption or publish plaintext private firmware.**
4. Cross-repository AI1 contract: compare custom GATT UUIDs, authenticated read/write/notification roles, MTU/payload limit, single-frame `AI1|TYPE|request_id|payload\n` parser, replays and connection-generation handling. Do not claim real C2/GATT or phone operation without hardware tests.
5. Regression/failure paths: source pin mismatch, checksum tampering, wrong DFU framing, corrupt archives, missing secrets, stale responses, failed GitHub Actions jobs, artifact expiry, and incorrect firmware-vs-ESP32 updater.

## Workflow and delivery
- Inspect `.github/workflows/private-momentum-ai-build.yml`, `.github/workflows/ci-fallback-verify.yml`, `scripts/prepare_momentum_flash_package.py`, and `tests/` on the active branch.
- Run appropriate `python3 -m unittest discover -s tests -p 'test_*.py' -v` and Actions contract CI; show exact commit and run/attempt in reports.
- Generate unique, recognizable **encrypted outer** firmware/artifact names with UTC date, GitHub run ID, attempt and short source SHA. Keep the NATIVE `flipper-z-f7-update-*.tgz` internal filename/structure unchanged.
- Clearly label results: **CONTRACT TESTED**, **CI COMPILED**, **DFU VERIFIED**, **ENCRYPTED DELIVERY VERIFIED**, **DEVICE TESTED**, or **FLASH APPROVED**. Never approve a phone flash based only on checksum, packaging, encryption, unit tests, or qFlipper installation instructions.
- Before physical installation require the owner's manual device/SD backups, recovery image, trusted decryption and SHA validation, and recovery readiness. Do not automatically flash, merge, create public releases, or deploy.
- The owner prefers direct, copy-friendly instructions; for Termux, visible/pasteable password prompts must keep secrets out of shell history and shared screenshots.
