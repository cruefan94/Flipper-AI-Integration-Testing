# Latest F7 exact-job evidence — 2026-11-18 02:03 America/Toronto

This is **public-safe metadata only**, not a firmware artifact or release approval.

## Fresh cross-repository evidence
- Private Momentum `test/ai1-pinned-gatt-api-contract-20261118` at `ce8b22585a31a30b03d543140f958dd244f547f0`: [F7 workflow 44252265247](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44252265247) reports success, but **only** quick source checks ran. Native compile job 134625535908 and private TGZ publisher job 134625536084 were **skipped**. No artifacts listed. Do **not** promote this head as a compiled F7 candidate.
- Same private head: [full inventory 44252253684](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44252253684) failed. Integrated Momentum updater and ESP32-S2 merged-image jobs failed; worker, syntax, WROOM reference, standalone FAP and WROOM SD bundle passed. The final bundle job skipped. This is one completed failure for that workflow/branch; do not conflate with another branch or F7 workflow.
- Earlier private Momentum head `1e7a412003af01653ff89dc03fee743a1e37a624`: [native compile 44238360282](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238360282) had executed build/publisher jobs, but exact private artifact SHA-256, extracted real `firmware.dfu` CRC and device acceptance still require authorized private verification.
- Public integration native encrypted [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) custom-firmware job passed. [CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) remains draft; passing job status is not a substitute for source SHA and exact native artifact evidence.
- Android [combined build 44214146838](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44214146838) passed at `9da29c4fce8e82c981823c9aee0296671abfb335`, with one 24,496,527-byte DEBUG-UNTESTED artifact. Installed signer and versionCode upgrade compatibility remain unverified. Do not replace/uninstall the installed app.
- Prior Android same-branch failures [44181012277](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44181012277) and [44204936456](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44204936456) met the two-completed-failure trigger; **no Android-compatible fallback run ID verified**. The subsequent green build does not retroactively establish fallback dispatch.

## Release gates and owner handoff
1. Exact-head F7 native compile must **execute** (not skip), pass real DFU suffix CRC and native updater checks, produce private encrypted-only TGZ, and record private SHA-256/source provenance. Never retry the CRC 9-99 updater.
2. Android candidate needs passing exact-head build, signer fingerprint match or explicitly side-by-side test identity, versionCode check, and owner opt-in before any install.
3. AI1 BLE version, GATT UUID/characteristics, frame limits, request/reply and reconnect behavior require matched Android/firmware contract tests and then physical acceptance.
4. For two consecutive failures on the **same workflow and branch**, use only an approved component-compatible public-safe fallback; if Actions:read/dispatch is unavailable, label **BLOCKED**, record IDs, and request authorized configuration. Do not leak source, binaries, logs, credentials or personal diagnostics.
5. Integration-testing workstream alone owns combined candidate ledger. Pi, ESP32, Arduino, voice and receive-only radio stay optional until proven. qFlipper recovery and Termux diagnostics must remain private/read-only until separately accepted.

No production merges, physical flashing, APK installs or artifact promotion authorized. See [private release matrix PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and [failover coverage PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23).
