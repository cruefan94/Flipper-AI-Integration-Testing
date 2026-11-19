# Pi exact-suite CI incident — 2026-11-19 07:56 EST

Public-safe cross-workstream triage only. No private source, device logs, credentials, firmware, or user identifiers.

## Evidence
- Repository: cruefan94/Flipper-AI-Integration-Testing
- Branch: `test/pi-dashboard-exact-suite-ci-20261119`
- Three completed failed exact-suite runs: [44521022652](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521022652), [44521042473](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521042473), [44521062532](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521062532).
- Latest failed head: `8879739def60295114fe0c2125ac0bb455c33a34`.
- [Smoke run 44521062601](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44521062601) passed on that head; it is **not** proof that the dedicated Pi suite passed.
- Job `dashboard-contract` (135549464782) completed setup, checkout, Python setup, Tkinter prerequisite, and source parsing. Its exact-suite step failed with `ImportError: Start directory is not importable: '.../tests'` at `unittest.TestLoader().discover('tests', pattern=..., top_level_dir='.')`. This is a test-discovery/packaging problem, not evidence of an unavailable runner, a hardware fault, or a billing issue.

## Mandatory routing
The same workflow and branch have more than two consecutive completed failures: **escalate to the established public-safe integration-testing fallback policy**. These failures are already in the public integration-testing workspace, so do not mislabel another ordinary smoke run as a successful fallback. No approved independent fallback dispatch or fallback run ID is evidenced here. If no authorized dispatch exists, mark execution BLOCKED and hand off to the Pi test owner; do not rerun indefinitely.

## Recommended correction for the Pi test owner (not applied here)
Make test discovery importable by ensuring the checked-out `tests` package layout is valid (for example, an `__init__.py` when required) or use explicit module/file loading rather than fragile `discover(..., top_level_dir='.')` behavior. Verify all three exact test files, >=11 executed tests, zero skips, and successful assertions on a **new head**; keep Tkinter requirement and the failure-on-skip gate intact. Never weaken tests merely to obtain green CI.

## Release gates unchanged
No promotion of Pi dashboard, Android APK, or F7 updater. F7 requires native flash-layout safety, genuine DFU CRC and updater hashes. Android requires signing-certificate continuity and versionCode checks. BLE AI1 requires paired contract acceptance. No physical install, flash, merge or secret publication.
