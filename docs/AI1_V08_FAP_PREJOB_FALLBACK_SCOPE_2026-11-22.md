# AI1 v0.8 FAP pre-job failures and fallback scope — 2026-11-22 04:55 ET

Public-safe evidence only. No firmware source, artifact, credentials, private logs, device identifiers or raw diagnostics.

## Exact source and CI evidence
- Private Momentum PR #86: `fix/flipper-ai-v08-fap-ci-trigger-20261122`, head `5eed030b206e15983624107bd794ae792138d5f2`.
- Same workflow and branch, completed failures: [45008101314](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008101314) and [45008110405](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008110405), both at the exact head. The earlier [45008094375](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45008094375) is on the same branch but at prior source SHA `821e13a0dec41b7ac10626fdf7f3ddb0833d87fd`. Each inspected job has conclusion failure and **zero steps**. Classify as **pre-job/runner provisioning failure suspected, root cause unproven**. Do not call this a compiler regression or assume billing.
- The owner's two-failure threshold is met for the *same workflow and branch*. An approved public-safe fallback should be invoked if not already routed for these exact runs; dispatch/result for these specific IDs is **not verified**. If Actions read/dispatch permissions fail (including 403), mark **BLOCKED** rather than silently treating monitor green as success.
- Earlier public fallback [44998562293](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44998562293) executed private-source protocol interoperability jobs on **different pinned legacy branches**, with no native FAP job. Do not attribute this to PR #86 or the latest Android AI1 source.
- Earlier public fallback [44998563900](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44998563900) ran only describe/diagnostic; firmware, contract, protocol and Android were skipped. Green is not a native updater pass.
- Public fallback scope gate [45005450089](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45005450089) **passed** at `9f814848395c3ec0730a25b2884a55eb3084ec5a`; this is a synthetic fail-closed test, not a firmware build.
- Historical native encrypted F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) succeeded at source `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`. Do not promote without independently verifying genuine `firmware.dfu` suffix CRC, native updater manifest hashes, encrypted-only delivery and provenance. Never retry the known CRC 9-99 artifact.

## Android and cross-project admission
- Android PR #124 at `f1188d21e7ee01219a36698fdb270f69df1c407d`: combined APK [45004495801](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45004495801) and isolated APK metadata [45004495849](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45004495849) passed. These are *branch-specific* and do not attest an integrated release APK, signer match with the installed app, versionCode continuity or physical AI1 RPC.
- Require an exact pair of Android/Flipper commits and a stock Momentum RPC AppStart/AppData AI1 transcript from an authorized physical test before calling end-to-end BLE success. Do not put raw user diagnostics or credentials into public artifacts.
- Side-by-side test APK only with owner opt-in; no replacement or uninstall of existing Android app. Native F7 updater remains HOLD; no device flashing.

## Next safe action
1. Check whether the approved public-safe fallback already dispatched for PR #86 runs 45008101314/45008110405. If not, invoke only the existing approved route, preserving private-source isolation; record fallback run ID, jobs actually executed, and exact SHA.
2. Obtain private Actions annotations/provisioning evidence for these zero-step jobs using authorized access; classify infrastructure versus source only after evidence.
3. Gate both candidate deliverables on exact-artifact checks, recovery guidance, signer continuity and physical approval. No protected merges or shared candidate branch mutation.
