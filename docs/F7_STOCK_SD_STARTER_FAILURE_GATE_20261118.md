# F7 stock-SD starter: fail-closed build triage (2026-11-18 23:56 ET)

## Pinned observations (not release approval)
- Private firmware branch `feature/official-momentum-sd-starter-20261118`, SHA `60f18fc4791148a9c2e8f316caf2704af142973e`.
- [Actions run 44459428313](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44459428313): **completed failure**. Job `Momentum mntm-012 integrated update + existing apps` failed; final `Bundle only verified compilations into one Android download` was **skipped**. Source syntax, worker/packaging checks, standalone FAP, ESP32-S2 and WROOM/SD starter jobs reported success. Those successful jobs **do not** imply a native F7 updater or release bundle is ready.
- Prior [firmware run 44422497544](https://github.com/cruefan94/Flipper-AI-Momentum-/actions/runs/44422497544) reported workflow success at a **different branch/SHA** but native compilation and TGZ jobs were skipped (per MAIN handoff). It cannot be used to promote the current candidate.
- [Android run 44454412841](https://github.com/cruefan94/Flipper-AI-Android-Satellite/actions/runs/44454412841) passed at `05c1149b7c7dace508f8f77d90200170ae2e293a`, but installed-app signing certificate, versionCode and AI1 paired interoperability remain unverified.
- [Public-safe upgrade gate 44455293897](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/44455293897) passed at `3574523721fe54870a3692a01c885207783afa3e`. This verifies **synthetic policy tests**, not a real device upgrade.
- Historical [encrypted native run 43828499328](https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328) completed successfully on `4cbdf863f5d7062ff34271bbd0687b843a6fbfc8`, while [PR #22](https://github.com/cruefan94/Flipper-AI-Integration-Testing/pull/22) currently points to `32f631c846db67d5f581887c00bbd06599b665c6`. These are **different commits**; no current-head CRC or artifact integrity is inferred.

## Triage handoff (private owner)
1. Read only the failing integrated Momentum job log via authorized private Actions:read. Classify source/compile/packaging error versus runner/provisioning issue; never assume billing. Keep private logs and firmware material private.
2. Compare the failing workflow's **same branch** completed attempts. A single failure is not a two-failure trigger. On two consecutive completed failures for the same workflow and branch, or repeated pre-provisioning failure, invoke the approved **public-safe private-firmware fallback**. Record both failing IDs, fallback ID, results, and corrective action. If private Actions:read or dispatch permission returns 403, mark **BLOCKED** and request correct permissions; never claim fallback succeeded.
3. Native F7 promotion requires a **non-skipped** successful compile, actual `firmware.dfu` suffix CRC verification, native updater `.tgz` contents and SHA-256 manifest, encrypted-only artifact identity, pinned private source SHA, and tested recovery instructions. Never reuse the historical failed DFU CRC 9-99 updater.
4. Android promotion requires signed APK hash, signing certificate match to installed application, monotonic versionCode, package identity, safe data-preserving upgrade, and paired AI1 BLE spec/contract checks. Signing mismatch means **HOLD**, not uninstall/replace.
5. Pi, ESP32, SD starter and standalone FAP outputs remain separately gated optional components; their success cannot substitute for a unified native F7 TGZ. qFlipper DFU recovery instructions must be reviewed before any owner-approved flash.

## Release matrix snapshot
| Candidate | Exact evidence | Gate |
|---|---|---|
| Native F7 TGZ | 44459428313 failed integrated job; bundle skipped | HOLD |
| Android test APK | 44454412841 build passed; signing/upgrade unverified | HOLD |
| BLE AI1 paired | No exact-pair hardware handshake evidence | HOLD |
| ESP32/Pi/SD starter | Individual CI jobs only | NOT PROMOTED |

This document contains only public-safe run IDs, refs, job conclusions, and acceptance criteria. It contains no private source, binaries, credentials, personal diagnostics, or job logs. No protected merge, flashing, installation, or production deployment is authorized.
