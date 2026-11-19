# AI1 consent toggle regression — public-safe triage (2026-11-17 14:01 ET)

This is a reference-only integration handoff. It contains no private source, artifacts, tokens, logs, or device diagnostics. No release promotion or deployment is authorized.

## Exact observations
- Android PR #64, `test/ai1-online-consent-toggle-20261117-1346`, SHA `952242ffa5772102428ee660f646e53a68725d59`: combined APK workflow [44151562584](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44151562584) completed **failure**. Job-level root cause not established; request sanitized failing assertion and job conclusion from Android owner.
- Android PR #63, SHA `c512617233043df297a9da1062989664f74ea242`: [44106822997](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44106822997) completed **success**. Different branch: **not** a consecutive-failure pair.
- Integration PR #91, SHA `52d2362e6df6d76de5f6705e66b67b934f62cd85`: [44143819419](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44143819419) passed public contract smoke; this is not native F7 or device validation.
- Private Momentum PR #45 SHA `03e96b8407fb85d2fa9d4420ac871d02c625d742`: [44149416713](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44149416713) completed failure. PR #44 and #43 failures were on **different branches**, not a same-branch consecutive pair.
- Earlier private Momentum candidate branch `feature/momentum-ai1-next-flash-20261117` has qualifying same-workflow failure pairs: workflow 420935082 runs 44024430141/44024439067 and workflow 414157517 runs 44024410032/44024430149. The approved public-safe fallback remains **BLOCKED** until private Actions:read and dispatch permissions are verified. No fallback run is asserted.
- Native encrypted F7 workflow [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed success, but actual DFU suffix CRC, exact updater SHA-256, and encrypted-only artifact identity have not been established from this metadata. The later native validation failure [44023046497](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44023046497) remains a release hold.

## Required next gates
1. Android owner: classify PR #64 job failure (test assertion vs runner), fix on Android-owned branch, and supply passing exact-head CI; verify online consent toggle rejects stale cloud replies.
2. Integration owner: obtain exact compatible firmware/Android AI1 revision and contract transcript; do not infer parity from independent green checks.
3. Firmware owner: private-only native DFU header/suffix CRC and TGZ hashes, source SHA, encrypted artifact provenance, qFlipper recovery checklist. Never retry CRC 9-99 image.
4. APK owner: compare installed and candidate signing certificate digest, application ID, versionCode and data-preserving update path; separate opt-in test install only after owner approval.
5. Two-failure fallback: authorize reference-only public-safe dispatch after permissions review; never upload private source, binary, secrets or diagnostics.

**Unified Android test APK: HOLD. Native F7 updater: HOLD. No physical hardware verification.**
