# Android AI1 PR61 passing CI: candidate handoff gate (2026-11-17 05:00 EST)

Public-safe integration evidence only; no firmware source, artifacts, credentials, or device diagnostics.

## Exact observed evidence
- Android PR #61: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/61
- Head: `d9421962de77c37f49b8ee60bd249909a9e4154b`
- Branch: `fix/ai1-policy-transition-test-20261117-0449`
- Workflow 420703090 run https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44059283296 completed **success** at inspection.
- Earlier PR #60 workflow run 44041523364 failed on **different branch** `fix/ai1-revocation-epoch-20261117-0248`; PR #59 run 44026721567 failed on another branch. Do **not** combine these as consecutive same-branch failures.

## Integration gates still required
1. Review actual PR #61 test assertions and job steps: success does not prove Android-device behavior or combined feature inclusion.
2. Pin a compatible firmware AI1 revision and compare HELLO/ASK/ANSWER payloads, CCCD, policy revocation, timeouts, replay and reconnect behavior using contract tests.
3. Capture actual APK package name, versionCode, signing certificate fingerprint and SHA-256 privately; prove upgrade compatibility against installed signer, or use isolated opt-in test package. Never uninstall/replace the owner's app.
4. Firmware PR #41 at `1c51c08f384d5538f60580600c7c42bf1680ca1e` has failing workflows 420935082 and 414157517; retain approved same-workflow two-failure fallback and classify job-level failure before any repeat.
5. Native F7 trial 44023046497 failed actual DFU header-size integrity; the older 43828499328 successful build job is not proof of native image CRC. Require actual `firmware.dfu` header/suffix CRC, native updater TGZ SHA-256, exact private SHA, encrypted-only provenance and qFlipper recovery instructions before promotion.
6. Keep CRC 9-99 updater quarantined. No flash, install, protected merge or production release.

## Handoff
Integration-testing workstream owns combined release ledger; feature owners should submit exact head, passing workflow, tested artifact identity, contract version and blockers. This document is a non-production evidence handoff, not candidate promotion.
