# Raspberry Pi 4B / first-generation Pironman: read-only monitor acceptance (draft)

Scope: standalone Pi-side work only. Reference monitor: draft PR #335, numeric guard draft PR #340. These PRs are not merged into this branch. This document is a test plan, not evidence of physical validation.

## Prerequisites and safety
- Obtain explicit owner approval before any device-side trial.
- Keep existing Pironman fan, RGB, OLED, system services and cooling settings unchanged.
- No sudo, package installation, firmware flashing, GPIO writes, hardware control, remote access enablement, credential capture or log publication.
- Do not run unreviewed scripts on the Pi. Prefer local synthetic fixtures and manually supplied redacted observations.
- Do not confuse offline timestamp status evaluation with live device polling.
- Do not retry the known F7 updater that failed DFU CRC 9-99. Do not replace the installed Android APK because of signing incompatibility.

## Offline acceptance gates
1. Pin exact source SHA for the monitor and numeric guard and review their diff and dependencies.
2. Verify targeted GitHub Actions at the exact SHA, not only a generic smoke test. Record run and job URLs, conclusion and test counts.
3. Exercise supplied timestamps for all four fixed sources (Pi, Pironman OLED, Flipper, ESP32): fresh, stale, missing, invalid, negative, huge integers, booleans and non-finite floats. Expect stable OK/STALE/MISSING/INVALID classifications and no exceptions.
4. Verify no hardware access, network access, privileged commands, service writes or secret output in the code path.
5. For any two consecutive completed failures on one workflow and branch, or repeated pre-runner failure, follow the approved PUBLIC-SAFE fallback. If private Actions:read returns 403, label BLOCKED; never publish private source/logs or assume billing is responsible.

## Owner-approved device acceptance (future; not executed)
- Observe the current working cooling and OLED behavior before and after, without changing them.
- Use only reviewed read-only observation commands, with the owner operating the Pi; redact hostnames, device addresses, paths and serials before sharing.
- Collect timestamp samples every 10 seconds only after a separate read-only adapter has passed offline tests and privacy review. The current module does not collect data.
- Verify unplugged/disconnected Flipper and ESP32 produce MISSING/STALE, never false OK; verify OLED is not presumed observable without a supported read-only interface.
- Stop on abnormal fan behavior, temperature rise, service instability, permission prompts or unexpected writes. Do not attempt repair automatically.

## Separate Pi workstream gates
| Workstream | Next safe acceptance gate |
|---|---|
| Pironman control center | Identify installed first-gen controller/API; simulate reversible settings; no live fan/RGB/OLED writes |
| 10-second monitor | Offline status tests, then owner-approved read-only adapter |
| Pi OS health / low-memory browser | Synthetic memory tests; no automatic process kills or cleanup |
| qFlipper diagnostics / recovery | USB enumeration and backup inventory read-only; no firmware updater retry |
| Pi-local AI | Inspect existing installed runtime; opt-in inference with resource limits |
| Phone-to-Pi remote access | Threat model and explicit opt-in; no exposed listener by default |
| BLE/Wi-Fi/USB gateways | Protocol fixtures and permission boundaries before device connection |

## Release handoff
Pi is an optional peripheral until hardware and compatibility are demonstrated. Integration-testing owns the unified release ledger. Do not promote to Android test APK or Momentum F7 .tgz without exact commit, passing CI, protocol compatibility, restore path and owner authorization. Private Phase 1 blockers: Momentum PR #23; public-safe fallback coverage: Integration-Testing PR #23. Canonical tracker: private Momentum issue #5.
