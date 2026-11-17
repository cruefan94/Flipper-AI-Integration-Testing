# Native F7 evidence: workflow attempt status drift (2026-11-17 18:57 ET)

## Why this gate matters
A workflow run ID is not immutable evidence of a completed passing *latest attempt*. On re-run, the same run ID may temporarily show `in_progress` with `conclusion: null`. A prior success claim must not be reused as current acceptance evidence without checking the latest attempt number, jobs, source SHA and artifacts.

## Observed (GitHub API, 2026-11-17 18:57 ET)
- Integration native F7 run: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44180961225
- Run head SHA: `fc6c9e462295ff2fdfae9a481580965d5c408e55`.
- **Latest read: `status=in_progress`, `conclusion=null`, updated 2026-11-17T23:56:36Z.** Earlier reports of a completed successful attempt do not establish the outcome of this ongoing attempt.
- Integration smoke at `e4e0370644cf6a111f646c2b68fb0f2311e91b65`: https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44195396047 — completed success, not native F7 evidence.
- Android combined build: https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277 — completed failure at `1471d5898ecfad6303d397cbb7501311d2ebce4c`.

## Fail-closed release evidence gate
1. Record workflow ID, run ID, **run_attempt**, completed status/conclusion, head SHA, workflow path and all relevant job conclusions.
2. Inspect actual native `firmware.dfu` framing and suffix CRC, updater archive structure, manifest and SHA-256 on authorized private route. Synthetic fixtures are not substitute evidence.
3. Match private source SHA to the encrypted artifact identity without publishing private binaries, source, logs, keys, or credentials.
4. For Android, require successful exact-head build, package/version compatibility and installed-vs-candidate signing certificate proof before an upgrade recommendation.
5. Require explicit physical owner approval before any APK install or F7 flash; keep CRC 9-99 artifact quarantined.
6. Track failures by **workflow + branch + consecutive completed attempts**, distinguish code from infrastructure, and after two failures use only approved public-safe fallback; record both failure and fallback run IDs. If Actions:read/dispatch is denied (403), mark BLOCKED; do not guess billing.
7. Do not promote Pi, ESP32, Arduino or radio modules without passing interface, safety and dependency gates.

This document is public-safe reference-only evidence; it contains no private source or build output.