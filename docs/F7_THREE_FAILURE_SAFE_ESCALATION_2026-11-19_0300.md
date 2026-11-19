# Public-safe F7 repeated-failure and release hold — 2026-11-19 03:00 ET

## Scope and provenance
This is a **sanitized coordination record only**. No private firmware source, binary, credentials, device logs, or artifact is included.

- Private source repository: `cruefan94/Flipper-AI-Momentum-`
- Workflow: `Build Flipper AI - custom Momentum + full executable inventory`
- Same branch: `test/stock-momentum-flash-offset-guard-20261119-0240`
- Three **completed failures**: [44481566067](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481566067) (`e37f9b3bed8b4d908159fc8ce6bed377358332fc`), [44481581444](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481581444) (`b5d33825703bca7ec485d9871838bb038706c82d`), [44481593032](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44481593032) (`604e89a17a3ba485bbf347b68d0bf2326e28426b`). These runs were initiated seconds apart on different SHAs; they do not prove sequential attempts at an unchanged source revision.
- All three show the native integrated updater job failed, while standalone FAP, ESP32 and stock SD starter jobs passed; final combined bundle was skipped. **A green auxiliary job does not make a valid native F7 updater.**
- Private job steps and a limited diagnostic excerpt identify a **native build safety refusal** involving an unsafe flash layout/offset, not a runner-provisioning failure. The build requested explicit unsafe acknowledgment; **do not add the acknowledgment or bypass the safety guard**. Firmware owners must repair layout/partition assumptions, then build on a new reviewed branch.

## Mandatory two-failure routing
The repeated completed failures on the same workflow/branch satisfy the owner's conservative two-failure escalation threshold, even though source SHAs differ. The approved fallback is the existing public-safe integration-testing workflow with private-source handling strictly confined to authorized private routes; never upload private firmware or logs to public.

**Fallback state: BLOCKED / NOT DISPATCHED from this review.** The available GitHub connector has no workflow-dispatch operation, and the prior private Actions-read HTTP 403 is not confirmed resolved. No fallback run ID exists from this review. Do not label the monitor's success as successful private build fallback. A maintainer with Actions write and valid private Actions:read must check the monitor's current coverage, then dispatch only the approved encrypted/private-safe route, recording the fallback run ID and outcome. Do not rerun failed native updater blindly.

## Coordinated release gates
- **F7 .tgz HOLD**: genuine compiled `firmware.dfu` suffix CRC, updater SHA-256, encrypted-only artifact provenance, exact source SHA, native non-skipped job, C2 safety, SD restore and qFlipper recovery required. Never retry the old DFU CRC 9-99 image.
- **Android APK HOLD**: latest Android PR #81 at `2997585863e2bd064b8896811d1971ea01792926` has [CI #44482308174](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44482308174) success; installed signing-certificate match, versionCode monotonicity and data-preserving upgrade remain unverified. No replacement/uninstall.
- **BLE AI1 HOLD**: paired exact protocol/characteristic/frame/status contract and physical handshake are not proven by separate CI successes.
- **Pi/ESP32**: optional separately built peripherals only; no unified promotion until provenance, electrical and transport gates pass.

## Next safe actions
1. Firmware owner: inspect private diagnostics and fix unsafe F7 flash offset/partition layout without disabling protection; record exact fixed SHA and non-skipped native updater run.
2. CI owner: verify private Actions-read permissions and dispatch the approved safe fallback; record its run ID or explicit permission error. Keep public results sanitized.
3. Integration owner: verify actual updater DFU CRC and archive hashes, APK signer/versionCode against installed app, and paired BLE AI1 tests before promoting either candidate.
4. Maintain the canonical private [MAIN issue #5](https://github.com/cruefan94/Flipper-AI-Momentum-/issues/5) and do not merge, flash, install or distribute until approved.
