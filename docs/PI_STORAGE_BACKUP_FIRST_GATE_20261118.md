# Raspberry Pi 4B / first-generation Pironman — storage safety gate (2026-11-18)

Scope: standalone Pi workstation only. This is a human-operated checklist, **not** an automated repair or a Flipper/Android release acceptance.

## Observed evidence
Owner-supplied Pi terminal photos show repeated `EXT4-fs warning (device sda2)`, `dx_probe`, `htree_dirblock_to_tree`, and `error -5 reading directory block`. These establish read failures, **not** whether the cause is SSD media, USB bridge/cable, power, or filesystem damage. No live hardware validation has occurred.

## Safe gate before installing Pi components
1. Suspend updates, cleanup, indexing, downloads, benchmarks and other avoidable disk writes. Preserve Pironman fan/cooling and running services.
2. Identify whether `/dev/sda2` is the boot/root volume using owner-run read-only `lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL` and `findmnt /`. Check `vcgencmd get_throttled` as advisory only; historical flags do not prove current undervoltage.
3. Owner should prioritize backup of irreplaceable files to separate reliable storage. If repeated I/O errors persist, avoid repeated scans; consider an offline image-first recovery with suitable hardware and professional assistance for valuable data.
4. Do **not** run `fsck` against a mounted filesystem, run write-mode SMART tests, format, flash, disconnect a live boot SSD, or automatically repair.
5. Do not upload raw `journalctl`, device identifiers, file listings or private project content into a public CI repository. Use sanitized synthetic fixtures only.
6. Resume Pi software installation only after owner confirms backup, storage identification, and a stable storage/power path. Record evidence and owner approval in the private tracker.

## Project integration gates
- Pi EXT4 classifier: offline unit tests on exact commit, exact-head CI job evidence, bounded input, no privileged calls, no hardware access.
- Pironman control center: default read-only, reversible explicit opt-in RGB/OLED/fan changes, preserve safe fan defaults.
- Ten-second monitor: read-only snapshots; no continuous high-I/O polling on a suspect disk.
- qFlipper workstation: read-only USB detection first; verified backup and restore before any firmware operation.
- Pi-local AI and phone gateway: existing runtime, authenticated opt-in access, least privilege; no public listener by default.
- Browser/cleanup: **blocked** while storage is unstable; never auto-delete.
- BLE/Wi-Fi/USB gateways: optional Pi-only until interface compatibility and device safety are demonstrated.

## Coordinated release handoff
No Android APK or native F7 updater is produced or promoted by this Pi documentation. Public integration-testing workstream alone owns combined release ledger. Momentum PR #23 and integration-testing PR #23 are the Phase 1 safety references. Failed DFU CRC 9-99 updater must not be retried; Android signing mismatch forbids replacing existing app. The two-consecutive-failed-attempt private-safe fallback remains mandatory, but missing private Actions:read/HTTP 403 means BLOCKED, not success. No secrets, private source or binaries in public CI.

## Evidence status
This document is a source-only safety milestone. No Pi device tests, SSD recovery, GitHub Actions success for this new commit, or end-to-end release acceptance is implied.
