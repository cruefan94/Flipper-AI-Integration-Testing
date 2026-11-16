#!/usr/bin/env bash
# Flipper AI Raspberry Pi 4B setup. Safe, repeatable: no firmware writes.
set -Eeuo pipefail
umask 077

REPO="https://github.com/cruefan94/Flipper-AI-Integration-Testing.git"
BRANCH="feature/raspberry-pi4b-one-command-setup-20261115"
DEST="$HOME/flipper-ai-pi-companion"
LAUNCHER="$HOME/flipper-ai"
MODE="install"

for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE="dry-run" ;;
    --help|-h)
      echo "Usage: bash setup_pi4b.sh [--dry-run]"
      echo "Install Flipper AI diagnostics on a Raspberry Pi; no auto-flashing or OS tuning."
      exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

heading() { printf '\n=== %s ===\n' "$1"; }
note() { printf '%s\n' "$1"; }
fail() { echo "STOP: $1" >&2; exit 1; }

if [ "$(id -u)" -eq 0 ]; then
  fail "Run as your normal Pi desktop user, not root or with sudo. The script invokes sudo only for approved apt packages."
fi
if [ ! -f /etc/os-release ]; then
  fail "Unsupported operating system: no /etc/os-release."
fi
. /etc/os-release
case "$ID" in
  raspbian|debian|ubuntu) ;;
  *) 
    if ! command -v apt-get >/dev/null 2>&1; then
      fail "This setup supports Raspberry Pi OS/Debian/Ubuntu with apt, not an unknown OS."
    fi ;;
esac

heading "Flipper AI Raspberry Pi 4B setup — $PRETTY_NAME"
note "Safe scope: tools, Python source, read-only hardware checks."
note "Won't flash, erase, upgrade the OS, overclock, change passwords, or enable SSH."
if [ "$MODE" = "dry-run" ]; then
  note "DRY RUN: would install Git, curl, Python, Bluetooth utilities and GitHub CLI."
  note "DRY RUN: would check out $BRANCH into $DEST (preserving any existing work)."
  note "DRY RUN: would create $LAUNCHER and print next steps."
  exit 0
fi
command -v sudo >/dev/null 2>&1 || fail "sudo not available; cannot safely install packages."
command -v apt-get >/dev/null 2>&1 || fail "apt-get is required."
if [ ! -d "$HOME" ] || [ ! -w "$HOME" ]; then fail "Home directory is not writable."; fi
free_mb="$(df -Pm "$HOME" | awk 'NR==2{print $4}')"
if [ -n "$free_mb" ] && [ "$free_mb" -lt 550 ]; then
  fail "Less than 550 MB free on home drive. Free space before installing packages."
fi

heading "Installing only required utilities"
sudo -v || fail "Administrator password check failed."
sudo apt-get update
sudo apt-get install -y --no-install-recommends git curl ca-certificates python3 bluetooth bluez
# Optional GUI/file transfer and private GitHub queue tools: tolerate missing
# distro packages rather than breaking the core read-only companion install.
for pkg in gh blueman bluez-obexd; do
  if apt-cache show "$pkg" >/dev/null 2>&1; then
    if ! sudo apt-get install -y --no-install-recommends "$pkg"; then
      note "Optional $pkg installation failed; you can still use local diagnostics."
    fi
  else
    note "Optional $pkg unavailable in current apt sources; skipping."
  fi
done

heading "Preparing checked-out project (without overwriting changes)"
if [ -e "$DEST" ] && [ ! -d "$DEST/.git" ]; then
  fail "$DEST already exists but is not this Git checkout; not overwriting it."
fi
if [ -d "$DEST/.git" ]; then
  actual="$(git -C "$DEST" remote get-url origin)"
  case "$actual" in
    "$REPO"|"git@github.com:cruefan94/Flipper-AI-Integration-Testing.git"|"https://github.com/cruefan94/Flipper-AI-Integration-Testing") ;;
    *) fail "Existing checkout has a different origin; not changing it." ;;
  esac
  if [ -n "$(git -C "$DEST" status --porcelain)" ]; then
    fail "Existing Pi companion checkout has local changes. Not overwriting your work."
  fi
  git -C "$DEST" fetch --depth 1 origin "$BRANCH"
  git -C "$DEST" checkout -B "$BRANCH" FETCH_HEAD
else
  git clone --quiet --depth 1 --single-branch --branch "$BRANCH" "$REPO" "$DEST"
fi

python3 -m py_compile "$DEST/raspberry_pi/pi_bridge.py"
python3 -m py_compile "$DEST/raspberry_pi/test_pi_bridge.py"

heading "Installing one simple local launcher"
if [ -e "$LAUNCHER" ] || [ -L "$LAUNCHER" ]; then
  if [ ! -f "$LAUNCHER" ] || ! grep -q "^# Flipper AI Pi helper launcher v1$" "$LAUNCHER"; then
    fail "$LAUNCHER already exists and is not our launcher. No file overwritten."
  fi
fi
# The launcher is never run with sudo and does not remotely flash hardware.
cat > "$LAUNCHER" <<'LAUNCHER_SCRIPT'
#!/usr/bin/env bash
# Flipper AI Pi helper launcher v1
set -Eeuo pipefail
DIR="$HOME/flipper-ai-pi-companion"
case "$1" in
  health)
    exec bash "$DIR/raspberry_pi/pi_health.sh" ;;
  status)
    exec python3 "$DIR/raspberry_pi/pi_bridge.py" status ;;
  usb)
    exec python3 "$DIR/raspberry_pi/pi_bridge.py" usb ;;
  firmware)
    exec python3 "$DIR/raspberry_pi/pi_bridge.py" firmware ;;
  connect)
    command -v gh >/dev/null 2>&1 || { echo "GitHub CLI is not installed; use local health and status only."; exit 2; }
    gh auth status >/dev/null 2>&1 || gh auth login --hostname github.com --git-protocol https --web
    echo "Starting Pi bridge; keep this Terminal open. Ctrl+C stops it."
    exec python3 "$DIR/raspberry_pi/pi_bridge.py" watch ;;
  *)
    echo "Commands: ~/flipper-ai health | status | usb | firmware | connect"
    echo "No commands automatically flash, erase, reboot, or modify Flipper firmware."
    exit 2 ;;
esac
LAUNCHER_SCRIPT
chmod 700 "$LAUNCHER"

heading "Read-only Raspberry Pi health report"
bash "$DEST/raspberry_pi/pi_health.sh"
heading "Flipper AI bridge status"
python3 "$DEST/raspberry_pi/pi_bridge.py" status
heading "READY: safe Raspberry Pi project tools installed"
note "To see Pi health:       ~/flipper-ai health"
note "To see USB status:      ~/flipper-ai usb"
note "To link to this chat via private GitHub:  ~/flipper-ai connect"
note "The last command may open GitHub browser authentication ON THE PI."
note "It does NOT flash firmware, and your Samsung phone needs no USB cable."
