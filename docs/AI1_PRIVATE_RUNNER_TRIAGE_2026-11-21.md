# AI1 F7 workflow provisioning triage — 2026-11-21 20:00 ET

PUBLIC-SAFE metadata-only handoff. This file contains no private firmware source, logs, credentials, binaries, or personal diagnostics. No production release is authorized.

## Newly observed exact-head private candidate

- Repository: private `cruefan94/Flipper-AI-Momentum-`
- Branch: `candidate/stock-momentum-rpc-ai1-fap-20261121`
- Commit: `de2472686dc0d8b8bbde870e98f76e7c013e807a`
- Completed failures, all distinct workflows on that branch (not two consecutive attempts of the same workflow):
  - [F7 candidate gate #44959750614](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959750614): private quick source checks failed; compile and draft release skipped.
  - [AI1 C/Java interoperability #44959750600](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959750600): failed.
  - [Satellite BLE bridge #44959750300](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959750300): failed.
  - [Standalone FAP #44959750275](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959750275): failed.
  - [AI native protocol #44959750236](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959750236): failed.
  - [Stock Momentum RPC FAP #44959726337](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44959726337): first job failed; FAP compilation skipped.
- GitHub job metadata for #44959750614 and #44959726337 showed failed jobs with **empty steps arrays**. This is consistent with a pre-step/provisioning failure, but **not proof** of its cause. No billing diagnosis or code regression can be concluded from this metadata. Inspect private Actions job annotations, runner allocation and workflow permissions before classifying.
- Public failover monitor [#44966354883](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44966354883) succeeded on `main` at `f1cac80854f26259534c032b2855dd609dd6c58e`; monitor success is NOT proof that an eligible private fallback was dispatched. Fallback dispatch ID/result: **not established**. If repeated pre-provision failure is confirmed, invoke the approved public-safe route once; if private Actions:read is 403, mark **BLOCKED** and request scoped permission. Never upload private firmware or job logs to public.

## Separate confirmed green evidence (not release admission)

- Android combined APK [#44963560905](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44963560905) passed at `97e2131da4f406f3fba4b80a8a0a4ab67b2c6e82` on `test/android-apk-identity-preflight-20261121`. Installed-app signing SHA-256, versionCode upgrade compatibility, package identity and physical BLE AI1 remain unverified; do not install or replace the existing app.
- Public integration radio metadata [#44966321660](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44966321660) and Pi meminfo [#44965724162](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44965724162) passed their offline scopes, not cross-device acceptance.
- Historical native encrypted F7 [#43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) passed its jobs, but was built from a different source revision than current [CRC gate PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) head `32f631c846db67d5f581887c00bbd06599b665c6`. Genuine current updater `firmware.dfu` suffix CRC, archive hashes and encrypted-only artifact provenance have **not** been attested here. The CRC 9-99 image is forbidden.

## Next evidence gate

1. Inspect private job failure annotations and permissions without copying private logs into public; classify runner/provisioning versus source.
2. Group completed attempts by **exact repository + workflow + branch**, never by number of failed workflows in one push. Two consecutive failed attempts or repeated pre-provisioning failures trigger one approved public-safe fallback. Record both failure run IDs and actual fallback dispatch/run ID, or explicit BLOCKED reason.
3. Compare BLE AI1 wire format, UUIDs, authentication and framing between exact Android and FAP source SHAs in private; run public synthetic contract fixtures only.
4. Require real F7 updater CRC, internal hashes, pinned source SHA, recovery manifest, and explicit owner flash approval. Require installed APK signer/package/version evidence before any upgrade. Neither candidate is promoted.
5. Integration-testing workstream alone owns unified candidate ledger; do not mutate shared candidate branch. Refer to private firmware [release blocker PR #23](https://github.com/cruefan94/Flipper-AI-Momentum-/pull/23) and public-safe [fallback PR #23](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/23).
