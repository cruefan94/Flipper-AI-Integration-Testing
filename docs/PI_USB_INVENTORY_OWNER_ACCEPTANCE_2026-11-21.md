# Raspberry Pi 4B USB inventory: owner acceptance (read-only)

Scope: first-generation Pironman Pi workstation only. This is a **manual acceptance procedure**, not proof of physical hardware validation. Do not modify cooling, OLED, RGB, services, USB permissions or firmware.

## Preconditions
- Owner is present and explicitly opts in to this individual check.
- Pi is operating normally with cooling unchanged.
- Use a normal unprivileged terminal, not sudo. No installation or device access is needed.
- From a trusted checkout of the reviewed source, confirm `raspberry_pi/usb_vidpid_inventory.py` matches the approved commit. Do not pipe remote scripts into a shell.

## Steps (owner device only)
1. Run `python3 raspberry_pi/usb_vidpid_inventory.py` **without** consent. Expected JSON: `status=not_authorized`, empty `devices`, `device_identity=unknown`. No sysfs inventory should be attempted.
2. If and only if the owner agrees, run `python3 raspberry_pi/usb_vidpid_inventory.py --consent`. Expected JSON status `read_only_inventory` with zero or more VID/PID pairs, or `sysfs_unavailable` if inaccessible. These pairs are not proof of a connected Flipper.
3. Inspect output locally. Do not upload unredacted host logs or identifying USB metadata. If sharing results, report only status, count of entries, and whether the two commands exited successfully.
4. Stop. Do not open USB device nodes, change udev rules, start qFlipper, perform backup/recovery, or flash anything as part of this acceptance.

## Pass / fail
- PASS: no-consent output is denied; opt-in output is well-formed and bounded to VID/PID; no device access or service disruption is observed.
- INCONCLUSIVE: sysfs unavailable or device identity cannot be established. No inference about qFlipper connectivity.
- FAIL: unexpected output, error, or any service disruption. Stop and retain private local notes; do not retry indefinitely.

## Recovery and release gate
This procedure makes no configuration changes; rollback is simply closing the terminal. If cooling or services behave abnormally, stop the check and follow the owner's existing Pironman recovery procedure; do not attempt a repair automatically.

Successful offline CI is necessary but insufficient for Pi acceptance. Physical owner evidence and separate qFlipper USB, backup and recovery validation are required. Keep this optional Pi component out of Android APK and F7 Momentum updater candidates until cross-component contracts and acceptance are independently verified.

Related: draft source PR #264, regression PR #267; exact-head regression run 44859660664 and smoke run 44859660541 (both previously successful). Private Actions-read 403 is a blocked monitoring route, not proof of a code failure. Preserve two-consecutive-failure PUBLIC-SAFE fallback and never disclose private firmware or credentials.
