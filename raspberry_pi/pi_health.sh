#!/usr/bin/env bash
# Raspberry Pi 4B: read-only health audit. Never overclock/flash/reboot/erase.
set -Eeuo pipefail
echo "=== FLIPPER AI: RASPBERRY PI 4B HEALTH ==="
printf 'OS: '
if [ -r /etc/os-release ]; then
  (. /etc/os-release; printf '%s\n' "$PRETTY_NAME")
else uname -s; fi
printf 'CPU architecture: '; uname -m
printf 'Uptime: '; uptime -p 2>/dev/null || uptime
echo "--- RAM ---"
if command -v free >/dev/null 2>&1; then free -h; else echo "Memory utility unavailable"; fi
echo "--- Storage ---"
df -h "$HOME" | head -n 2
echo "--- CPU temperature and throttling ---"
if command -v vcgencmd >/dev/null 2>&1; then
  vcgencmd measure_temp || true
  vcgencmd get_throttled || true
elif [ -r /sys/class/thermal/thermal_zone0/temp ]; then
  awk '{printf "CPU temperature: %.1f C\n",$1/1000}' /sys/class/thermal/thermal_zone0/temp
else echo "CPU temperature unavailable"; fi
echo "--- Wi-Fi ---"
if command -v iwgetid >/dev/null 2>&1; then
  if iwgetid -r >/dev/null 2>&1; then echo "Wi-Fi connected"; else echo "Wi-Fi not associated/unknown"; fi
elif command -v nmcli >/dev/null 2>&1; then
  nmcli -t -f WIFI general status 2>/dev/null | head -n 1 || true
else echo "Wi-Fi status utility unavailable"; fi
echo "--- Bluetooth ---"
if command -v bluetoothctl >/dev/null 2>&1; then
  bluetoothctl show 2>/dev/null | grep -E '^[[:space:]]*Powered:' | head -n 1 || echo "Bluetooth controller unavailable/disabled"
else echo "Bluetooth tools unavailable"; fi
echo "--- USB (serial port names only) ---"
found=0
for port in /dev/ttyACM* /dev/ttyUSB*; do
  [ -e "$port" ] || continue
  found=1
  basename "$port"
done
if [ "$found" -eq 0 ]; then
  echo "No USB serial ports detected. Flipper requires a Pi-to-Flipper DATA cable for qFlipper."
else echo "A serial port is not necessarily a Flipper; check qFlipper's window."; fi
echo "--- qFlipper ---"
if command -v qFlipper >/dev/null 2>&1 || command -v qflipper >/dev/null 2>&1; then
  echo "qFlipper executable present in PATH"
elif [ -x "$HOME/Applications/qFlipper.AppImage" ] || [ -x "$HOME/Applications/qflipper.AppImage" ]; then
  echo "qFlipper AppImage detected (architecture compatibility not verified)"
else echo "qFlipper executable not found in standard locations"; fi
echo "=== CHECK COMPLETE. NO CHANGES TO THE FLIPPER OR ITS FIRMWARE ==="
