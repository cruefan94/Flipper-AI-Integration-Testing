# Raspberry Pi 4B / first-generation Pironman: read-only desktop acceptance gate

Status: **device acceptance NOT PERFORMED**. This checklist is a manual acceptance protocol, not evidence that the device was tested. Base: Pi dashboard CI import-root correction PR #177.

## Preconditions and protection

- Do not install packages, change systemd services, touch fan curves, OLED, RGB, GPIO, firmware, Bluetooth pairing, or network configuration.
- Back up important user data before any later installation or repair: earlier owner-reported `/dev/sda2` I/O warnings remain unresolved.
- Confirm existing Pironman cooling is running normally by observation. If the fan stops, the Pi overheats, or storage warnings recur, abort the dashboard acceptance and preserve the current configuration.
- Run the desktop dashboard only in a logged-in Pi OS graphical session. Do not use sudo. Keep a second terminal available to close it if necessary.
- Do not publish hostnames, serial numbers, device IDs, private IPs, credentials, personal file paths, or raw device logs in public issues.

## Stage A — source and CI gate (off-device)

1. Confirm exact branch/commit and a completed passing **exact-suite** Actions run that explicitly executes >=11 tests with zero skips. A passing generic smoke run is not sufficient.
2. Confirm the dashboard and monitor import successfully without writing to the Pi, and that launcher source-check mode exits cleanly.
3. Record run ID, commit SHA, and test count. If two completed failures occur on the same workflow/branch, use the approved PUBLIC-SAFE fallback. If Actions:read is denied (403), mark fallback BLOCKED, not passed.

## Stage B — on-device read-only acceptance (owner opt-in only)

1. Open the dashboard normally (no root privileges). Verify no exception dialog appears and no system setting changes.
2. Compare displayed CPU temperature, total/available memory and uptime with native Pi OS read-only observations; record only rounded, non-identifying values.
3. Observe at least three consecutive 10-second refresh cycles. Check the UI stays responsive and reports errors without freezing or showing stale numbers as current.
4. Disconnect no hardware. Where OLED, Flipper or ESP32 adapters have not been validated, require explicit `not_probed` rather than a fabricated connected state.
5. Close and reopen the dashboard from a different working directory / desktop launcher. Confirm clean exit and no background process left behind.
6. Recheck existing fan/cooling behavior and normal Pi services after closing. Stop and report any deviation.

## Acceptance record template (do not prefill)

- Tested exact commit:
- Exact-suite CI run / test count:
- Pi OS version and desktop (general release only):
- Three refresh intervals observed:
- CPU/memory/uptime plausible:
- Missing peripherals show not_probed:
- Launcher works from alternate directory:
- Cooling/services unchanged:
- Storage warnings observed (yes/no; no raw logs):
- Pass / fail / blocked and corrective action:

## Related Pi workstream gates

| Workstream | Gate before enabling |
| --- | --- |
| Pironman RGB/fan/OLED control center | Confirm first-generation vendor interface, save reversible defaults, and obtain explicit device approval before any write |
| Pi OS health, browser, cleanup | Read-only inventory, storage backup, then reversible per-change tests |
| qFlipper USB backup/recovery | Detect USB safely; verify backups/restores without automatic firmware flash |
| Pi-local AI | Verify existing local runtime, RAM pressure and opt-in model selection; no new custom engine |
| Secure phone-to-Pi | Explicit opt-in, authentication, LAN-only default, no exposed public port |
| BLE/Wi-Fi/USB gateways | Contract/version checks, rate limits, disconnect/reconnect handling, no unapproved radio transmission |

Integration: these are **optional Pi-side components**, not part of the Android test APK or F7 Momentum updater unless exact compatibility and device acceptance are proven. The integration-testing workstream owns the combined release ledger. Never retry the known DFU CRC 9-99 updater or replace the installed Android app with a signing-incompatible APK.
