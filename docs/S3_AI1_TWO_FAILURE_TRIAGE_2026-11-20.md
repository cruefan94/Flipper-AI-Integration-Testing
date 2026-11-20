# ESP32-S3 AI1 exact-head host CI: two-failure triage (2026-11-20)

Public-safe evidence only. No private firmware source, binaries, credentials, raw logs, or personal diagnostics.

## Trigger / exact provenance

- Private firmware PR #75: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/75
- Branch: `test/s3-ai1-exact-host-ci-20261120-0938`
- Exact head: `a37868b100dfdac4b575b3ff194b8e69155e9061`
- Same workflow `ESP32-S3 AI1 exact-head host regression` completed failure twice:
  - https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755541063
  - https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44755560160
- Both have a completed failing `host-regression` job. The public-safe job metadata returned no step records. **Failure category unknown**; do not infer a compiler error, billing issue, or runner outage.
- This satisfies the owner-mandated two-consecutive-completed-failures fallback threshold **for this exact workflow and branch**, independent of other branches.

## Required fallback and privacy gate

Use only the existing approved PUBLIC-SAFE integration-testing private-firmware failover route, with no private source/binary/logs in public artifacts or job summaries. The previous private Actions:read HTTP 403 means monitoring/dispatch coverage is **BLOCKED until authenticated permission is reverified**. A green diagnostic-only fallback (with native firmware compilation skipped) is not a successful firmware build. Do not rerun failing private jobs indefinitely. Preserve failing IDs and record any actual fallback dispatch ID, sanitized outcome, and authorization result in the private canonical tracker.

## Next permitted actions

1. Authorized maintainer verifies the private Actions:read scope for the existing fallback monitor without exposing a token.
2. Inspect private job diagnostics inside the private repository and classify as runner provisioning, permission, dependency, test assertion, or build failure; retain only sanitized classification in public.
3. If approved fallback dispatch succeeds, record its real run ID, exact source SHA, executed jobs, and whether native compilation was actually run.
4. If still blocked, hold promotion. Keep Android APK signing/versionCode continuity and native F7 genuine DFU CRC, updater SHA-256, C2 boundary, and qFlipper recovery gates separate.
5. Never retry the known failed F7 DFU CRC 9-99 artifact, flash hardware, install APKs, or merge protected branches without approval.

## Cross-project acceptance

Android PR #98 worker CI is distinct from Android BLE AI1 acceptance. Android PR #96 build success is not installed-app signer compatibility or physical BLE pairing. Historical native F7 run #43828499328 passed on an older pinned source; it does not validate current firmware. This document changes no source or release candidate.
