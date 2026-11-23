# MAIN cross-project gate triage — 2026-11-23 02:02 EST

Public-safe coordination only. No private source, firmware binaries, tokens, signing certificates, or device logs.

## Exact-head findings
- Private Momentum PR #89, head `0cae6e1fb7a81928566306a53a17abb6cac75d96`: full-build workflow **failed twice on the same branch**, runs [45124987882](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124987882) (prior SHA `6a62e9ce9e`) and [45124990592](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45124990592) (current SHA). Second run has failed Worker packaging and Python source-syntax jobs, downstream native compilation **skipped**. Do not classify this as purely pre-runner or firmware compilation failure without private job evidence. **Two-failure fallback triggered**: require approved encrypted/private-safe dispatch and record resulting run ID; no source or artifact to public.
- Momentum PR #89 other workflows [45125155988](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45125155988), [45125155848](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45125155848), [45125155836](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45125155836), [45125155824](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45125155824), [45125155760](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/45125155760) failed separately; do not aggregate different workflows to invent a second attempt.
- Android Worker PR #145 head `0c36b2c070ba44d02edd6bc761ce552f622c6e26`: [45126754731](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45126754731) failed. Parent PR #144 [45113647300](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45113647300) passed at different SHA; not exact-head acceptance and not a same-branch two-failure pair.
- Android M7 PR #143 head `c8a7c88412c2b2e961eb131502f7bba34b44014b`: combined APK [45106703969](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703969), preview [45106703986](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703986), metadata [45106703984](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/45106703984) passed; not installed-signer parity or physical BLE proof.
- Public-safe integration PR #409 head `04154dc7a59a6a7a9423fe9d04e7376d2823b428` smoke [45121832964](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/45121832964) passed.
- Historic native F7 [43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) succeeded on `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`; not proof that a present candidate .tgz has correct real DFU CRC and member hashes.

## Release admission (fail closed)
1. Record exact firmware and Android source SHA, workflow/job IDs, artifact identity and SHA-256; preserve encryption-only private firmware route.
2. Confirm native F7 `firmware.dfu` suffix CRC from **actual candidate bytes**, `.tgz` and each updater member hash, compatible target, and qFlipper official recovery instructions. Never retry CRC 9-99.
3. Confirm APK package ID, versionCode, SHA-256 and signer fingerprint **against the installed application** before upgrade; otherwise only separate opt-in package with owner approval. Do not uninstall existing app.
4. Verify AI1 protocol version, request/response framing, timeout, reconnect and errors in C/Java contract tests; passing host tests do not prove physical BLE.
5. Keep Pi/ESP32/radio/voice separate until exact dependency and hardware gates pass. Do not merge protected main, flash, install or deploy.

## Mandatory fallback handling
After two consecutive completed failures of one workflow/branch, or repeated pre-provision failures, route through existing approved public-safe integration workspace. A green monitor alone is not proof of dispatch. If private Actions:read gives 403 or authorized dispatch cannot be confirmed, record **BLOCKED** with missing permission; do not invent fallback run ID or retry indefinitely. Distinguish runner provisioning from source test failure by inspecting job steps privately.

Next: private owner to inspect full-build job summaries and authorize approved safe fallback dispatch for PR #89; Android owner to triage PR #145. Integration owner alone promotes controlled unified candidates after evidence.
