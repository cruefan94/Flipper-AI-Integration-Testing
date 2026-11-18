# Two-failure inventory gate: 2026-11-18 02:56 America/Toronto

## Verified public-safe evidence

The **same branch** `fix/esp32s2-merged-bin-output-20261118` and **same workflow** `Build Flipper AI - custom Momentum + full executable inventory` failed on two completed runs:

| Run | Source SHA | Integrated Momentum update job | ESP32-S2 merged image job | Bundle job |
|---|---|---|---|---|
| [44260352832](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260352832) | `ea14b03af37bdc96b7144e42acfc2d04c1c5d307` | failed (134651980827) | passed | skipped |
| [44260368327](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44260368327) | `edc4a8fca49407ca5df3990f258a44e06dd61d45` | failed (134652049788) | passed | skipped |

Both runs passed source syntax, worker checks, WROOM reference, standalone FAP and SD-card companion jobs. The ESP32-S2 merge-bin path repair appears to have recovered its job, **but the integrated Momentum updater job is still failing**. Do not infer the failing assertion or blame runner/billing without job logs.

## Mandatory action

This is a **two-completed-failure trigger** on a single workflow+branch even though the source SHA changed. Use only the approved public-safe fallback route, **if it supports this workflow** and has authorized private Actions:read and dispatch permissions. If inaccessible (including HTTP 403), record **BLOCKED**; never transfer private firmware source, binary, credentials or raw diagnostics to public Actions. Record any real fallback run ID; none was verified when this document was authored. Do not loop reruns or weaken gates.

## Candidate gate

- The two failing inventory runs produced **no combined verified bundle** (bundle jobs skipped).
- A passing ESP32-S2 job is not a passing Momentum integrated updater.
- Earlier native F7 run [44238360282](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44238360282) pertains to SHA `1e7a412003af01653ff89dc03fee743a1e37a624`, **not** either failed inventory head.
- Android combined build [44214146838](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44214146838) passed at `9da29c4fce8e82c981823c9aee0296671abfb335`, but installed-signer compatibility and physical acceptance are unverified.
- The old DFU CRC 9-99 artifact is quarantined. Require real firmware.dfu suffix CRC, SHA-256, encrypted artifact identity, qFlipper recovery and owner approval before flashing.
- BLE AI1 version/UUID/message contract, Android consent and physical handshake remain release gates.

This is a documentation-only public-safe triage checkpoint, not a release candidate, build repair, fallback dispatch, or hardware test. See private Momentum draft PR #23 and integration-testing draft PR #23 for the owner-approved policy.
