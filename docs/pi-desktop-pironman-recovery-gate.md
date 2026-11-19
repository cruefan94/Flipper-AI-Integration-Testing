# Pi 4B / first-generation Pironman: desktop and app recovery gate

Status: planning and owner-run read-only inventory only. **Do not execute on the Pi automatically.**

## Safety stop
Earlier device photos showed repeated EXT4 directory I/O errors on sda2. Before package installs, cleanup, updates, fsck, service restarts or UI changes, confirm backups and storage health. Never run fsck on a mounted root filesystem. If reads fail or the filesystem becomes read-only, stop and prioritize data recovery. Keep existing fan/OLED/RGB services running.

## Owner-approved, read-only inventory (run only if storage is stable enough)
Run commands individually and inspect output locally before sharing; redact usernames, serials, network identifiers, credentials and file paths as needed.

```sh
findmnt /
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL
vcgencmd get_throttled
systemctl --no-pager --type=service --state=failed
dpkg-query -W -f='${binary:Package} ${Status}\n' | grep 'install ok installed' | cut -d' ' -f1
find /usr/share/applications ~/.local/share/applications -maxdepth 1 -name '*.desktop' -type f -printf '%f\n' 2>/dev/null
command -v qFlipper || command -v qflipper || true
```

These are inventory checks, not a repair script. Avoid sending the full package list publicly; review it privately. If filesystem reads cause errors, stop immediately.

## Recovery phases
1. **Storage**: identify boot drive, preserve files with backup and confirm stability before changes.
2. **App audit**: map each installed app to launcher, package/source, executable, service dependency, symptoms and owner priority; do not mass-remove packages.
3. **Pironman**: identify first-generation controller software and pin assignments; read service status and config without touching working fan curves or GPIO. Only later propose reversible UI settings with explicit approval.
4. **qFlipper**: read-only USB enumeration and logs first; recovery/backup procedures must require owner action and prohibit firmware flashing.
5. **Desktop**: review session failures, browser memory pressure and startup apps. Propose reversible changes individually after backups.
6. **Pi-local AI and gateways**: opt-in remote connections, no open ports by default, no secrets in logs. Gate on storage and service stability.

## Acceptance evidence
- Storage stable and owner confirms backup.
- Inventory distinguishes installed, runnable, broken and unverified apps.
- No disruption of Pironman cooling or current services.
- Reversible change log and rollback steps for each eventual repair.
- Hardware checks performed by owner, with evidence, before claiming the desktop is fixed.

## Cross-workstream
This is an optional Pi-side workstation track. Do not integrate into Android APK or F7 updater without tested compatibility and explicit release-ledger handoff. Preserve two-consecutive-failure CI fallback and private-safe public testing boundaries.
