# Android AI1 PR #60 exact-head regression and candidate hold — 2026-11-17 03:04 ET

Public-safe integration triage. No private firmware, device identifiers, signing material, or diagnostic payloads.

## Reproducible provenance

- Android PR: https://github.com/cruefan94/Flipper-AI-Android-Satellite/pull/60
- Exact head: `458f6f10d543c7676a26951bb81e22be7509579d`
- Branch: `fix/ai1-revocation-epoch-20261117-0248`
- Completed failing Actions run: https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44041523364
- Provisioned job `133896990332`: `One-time Android source, JVM and security regressions` failed; APK build and artifact provenance steps skipped. **No release APK from this run.**
- Previous PR #59 run https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44026721567 failed on *another branch*; do not count as consecutive same-branch failure.
- Public runner log text available at inspection did not establish the precise new assertion/compile cause. Do not assume PR #60 reproduces PR #59's original assertion without the test report.

## Required Android owner acceptance

1. Inspect the failure diagnostics artifact privately/safely; identify failing test names and stack traces without posting personal data.
2. Verify policy epoch invalidation for offline and cloud in-flight requests, before dispatch and before GATT reply; confirm no stale response after consent/policy revocation.
3. Test reconnect/link-epoch cancellation, consent off, AI engine readiness and process/service lifecycle.
4. Rerun targeted JVM tests and full APK CI on the *same exact updated head*. Preserve the two-consecutive-completed-failure fallback rule scoped by workflow and branch; repeated pre-runner failures also qualify.
5. Keep existing installed APK untouched until actual signing certificate/package/versionCode compatibility is established. A separate debug test APK is opt-in only.

## Firmware and unified release holds

- Native F7 build https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497 compiled but failed real DFU header-size validation. Do not package or flash.
- Earlier encrypted native build https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328 had a successful build job, **not** exact-image DFU CRC/native TGZ hash proof.
- Synthetic DFU tests at https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22 are not hardware proof.
- The CRC 9-99 updater is quarantined permanently.
- Firmware/Android AI1 protocol version, GATT registration, HELLO/ASK semantics, cancellation, and matched exact-head tests must be documented before candidate promotion.
- No protected merges, firmware flash, APK installation, or cloud deployment authorized.

## Cross-workstream relay

Integration-testing owns the combined release ledger; Android and firmware owners retain their feature branches. Request Android PR #60 exact-head failure diagnosis and passing rerun; request private native F7 validator framing fix and CRC/hash proof. No claim of a completed integrated candidate.
