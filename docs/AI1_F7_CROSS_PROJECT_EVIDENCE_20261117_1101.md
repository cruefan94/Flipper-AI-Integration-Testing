# AI1/F7 cross-project evidence checkpoint — 2026-11-17 11:01 EST

Public-safe references only. This file contains no private source, firmware binary, token, device identifier, or diagnostic log. It is a proposed checkpoint, not an approved release ledger update.

## Exact evidence
| Component | Ref | Evidence | Release implication |
|---|---|---|---|
| Android AI1 offline consent | cruefan94/Flipper-AI-Android-Satellite PR #63, c512617233043df297a9da1062989664f74ea242 | Actions 44106822997: completed/success | Host tests only; not a signed upgrade or BLE device acceptance |
| Android signing-source contract | Android PR #62, 3919ce339e95bf9ca4ac300058c0fad9ac2855a4 | Actions 44087115570: completed/success | Installed signer comparison still missing |
| F7 notification lock contract | private Momentum PR #43, bede033029d43e5d0fc51e6acf5e9b035bb90b49 | Actions 44116871005: completed/failure; worker packaging and Python syntax jobs failed; build jobs skipped | No firmware candidate promotion; job failure details need authorized diagnosis |
| CI fallback classification | Integration PR #85, 0f633946ab9f25dd20524e597e25d3edaf7092d2 | Actions 44109665144: completed/success, public smoke and offline fallback regression | Does not prove private Actions read permission or live dispatch |
| Earlier encrypted native trial | Integration Actions 43828499328, public workflow SHA 4cbdf863f5d7062ff34271bbd0687b843a6fbfc8 | custom-firmware job completed/success, encrypted-only uploads | No proof of successful physical flash or that later AI1 DFU header regression was repaired |
| Later native AI1 trial | Integration Actions 44023046497 | Reported actual firmware.dfu header-size mismatch | Native F7 candidate HOLD |

## Two-failure policy and new run triage
Prior same-workflow/same-branch Momentum failures: workflow 420935082 runs 44024430141 and 44024439067; workflow 414157517 runs 44024410032 and 44024430149. The new PR #43 failure 44116871005 is on a DIFFERENT branch and is **not** the next consecutive failure on the prior branch. Do not conflate branches or workflows. Classify jobs using authorized logs, distinguish code errors from runner failures, and do not attribute failures to billing without evidence.

The approved public-safe fallback must be attempted when its policy triggers, but live private Actions:read/dispatch authority remains **BLOCKED / unverified**. A green offline classifier test is not evidence of automatic dispatch. Do not publish private firmware source, binary, credentials or private logs to this repository.

## Coordinated release gates
1. Android: exact integrated source SHA; reproducible APK build; SHA-256; package ID, versionCode and versionName; APK signer certificate digest matching the currently installed app for an in-place upgrade, otherwise owner-approved isolated test app only; cloud-consent regression; actual BLE AI1 lifecycle and background reconnection.
2. F7: exact private source SHA and pinned Momentum base; actual generated firmware.dfu DfuSe header/targets/elements and suffix CRC verified on the SAME artifact; .tgz contents and SHA-256; encrypted-only artifact provenance; qFlipper restore instructions and explicit physical-flash approval. The historical CRC 9-99 artifact is permanently quarantined.
3. Cross-project: AI1 characteristic UUIDs, authorization, HELLO/ASK/reply framing, disconnect/CCCD behavior, cancellation and consent rules, version compatibility, and physical handshake must match before promotion.
4. Pi/ESP32/Arduino/radio/voice remain optional until their separate evidence and safety gates pass.

Next: obtain authorized PR #43 job-level failure details; confirm whether PR #85 changes are integrated into the active fallback workflow; produce a new real native F7 DFU integrity pass before considering any flash; compare Android installed signer safely without uninstalling.
