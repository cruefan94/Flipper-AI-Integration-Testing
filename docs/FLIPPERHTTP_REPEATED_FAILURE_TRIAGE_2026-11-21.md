# FlipperHTTP exact-branch repeated-failure triage — 2026-11-21

Public-safe metadata only. This is **not** a successful private-firmware fallback or release attestation.

## New two-failure candidate
- Private Momentum PR #76: https://github.com/cruefan94/Flipper-AI-Momentum-/pull/76
- Workflow: `FlipperHTTP read-only probe FAP (no firmware update)`
- Branch: `dev/flipperhttp-safe-adapter-20261120`
- Completed failure 1: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866082379 (head `199473c3287f2175e723aeb9b27dbe2a9f85c415`)
- Completed failure 2: https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44866117174 (head `4d2364f49339b4cb82b4e22ac4ce663c76df3d42`)
- Both runs have failing host regression jobs; native pinned Momentum FAP compile was **skipped**. Run #44866117174 also shows failures for runner/checkout availability checks. Job conclusions alone do not establish root cause or GitHub billing failure.
- Earlier same-branch failures #44865964031, #44865891484 and #44865825058 also exist. Do not restart the same branch indefinitely.

## Mandatory fallback routing and access
Two completed failures on the same workflow and branch meet the owner's public-safe fallback trigger. Use the *approved* private-safe route in this repository only after confirming its exact workflow inputs and secret/permission boundary. Previous private Actions:read HTTP 403 remains **BLOCKED** until a permitted read is demonstrated. **No fallback dispatched in this audit; fallback run ID: none.** Never copy private source, firmware, binary, credentials, personal logs or unsanitized diagnostics into public artifacts. Keep private-native build inside authorized encrypted/private boundaries.

## Separate the causes
1. Inspect sanitized run/job metadata and approved private logs for whether checkout/runner failure occurred before test code.
2. For jobs that started, collect the *first failing step* and sanitized exit classification; do not infer test logic failure from a red workflow alone.
3. On a corrected **new exact commit**, run targeted isolated host tests first; then pinned external FAP compile if host checks pass.
4. Record run ID, exact commit, workflow, branch, job/step classification, fallback ID or explicit BLOCKED reason, and corrective action in private canonical issue #5.
5. Preserve stock Momentum. No FAP install, firmware flash, production merge or promotion.

## Cross-project handoff
- Android PR #109 `test/worker-upstream-credential-isolation-20261121` head `a983820723050adb52e1b959916c5408dfbcd05c`: Worker contract CI #44882163012 passed. Does not establish APK signing compatibility or BLE device acceptance.
- Integration radio PR #278 `lab/radio-feed-admission-ci-20261121-0225` head `38a87ab21c3f82387c041a84a782c3f783d4185f`: offline radio CI #44880218774 and smoke #44880218716 passed. Receive-only admission tests do not establish hardware radio reception.
- Private S3 AI1 failure pair #44755541063/#44755560160 remains independently blocked.
- F7 native updater remains HOLD: no exact genuine `firmware.dfu` CRC, archive hashes, source provenance, C2 boundary and recovery attestation for a current candidate. Never retry the known CRC 9-99 artifact.
- Android test APK remains HOLD: installed-app signing fingerprint and monotonically increasing versionCode not proven; do not replace or uninstall owner's installed app.
- BLE AI1 API/spec parity, Pi/ESP32 integration, and physical acceptance remain unverified.

No unified Android APK or F7 updater candidate promoted. The integration-testing workstream alone owns the combined release ledger; this is a separate triage document, not a concurrent ledger edit.
