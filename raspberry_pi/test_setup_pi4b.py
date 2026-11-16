"""Tests for safe, repeatable Flipper AI Raspberry Pi setup commands.

No real apt calls, hardware access, firmware install or GitHub auth are performed.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "raspberry_pi" / "setup_pi4b.sh"
HEALTH = ROOT / "raspberry_pi" / "pi_health.sh"


class PiSetupTest(unittest.TestCase):
    def test_bash_syntax(self):
        for source in (SCRIPT, HEALTH):
            subprocess.run(["bash", "-n", str(source)],
                           check=True, capture_output=True, text=True)

    def test_dry_run_has_no_system_changes(self):
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            result = subprocess.run(
                ["bash", str(SCRIPT), "--dry-run"], env=env,
                capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY RUN", result.stdout)
            self.assertFalse((Path(home) / "flipper-ai").exists())
            self.assertFalse((Path(home) / "flipper-ai-pi-companion").exists())

    def test_launcher_requires_local_workflow_and_only_readonly_commands(self):
        content = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("git clone", content)
        self.assertIn("case \"\${1:-help}\" in".replace("\\", ""), content)
        self.assertIn("exec python3", content)
        self.assertIn("pi_bridge.py\" status", content)
        self.assertIn("pi_bridge.py\" usb", content)
        self.assertIn("pi_bridge.py\" firmware", content)
        self.assertIn("gh auth status", content)
        self.assertIn("pi_bridge.py\" watch", content)
        for forbidden in ("rpi-update", "raspi-config nonint do_overclock",
                          "wipefs", "dd if=", "mkfs.", "qflipper --flash",
                          "apt-get dist-upgrade", "apt-get upgrade -y",
                          "systemctl disable", "systemctl stop"):
            self.assertNotIn(forbidden, content)

    def test_existing_files_and_worktrees_cannot_be_overwritten_implicitly(self):
        content = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("git -C \"$DEST\" status --porcelain", content)
        self.assertIn("remote get-url origin", content)
        self.assertIn("not changing it", content)
        self.assertIn("not overwriting", content.lower())

    def test_health_is_read_only(self):
        source = HEALTH.read_text()
        for forbidden in ("apt install", "sudo ", "rm -rf", "mkfs",
                          "shutdown", "reboot", "vcgencmd over_voltage",
                          "config.txt", "raspi-config nonint"):
            self.assertNotIn(forbidden, source)
        self.assertIn("get_throttled", source)
        self.assertIn("df -h", source)
        self.assertIn("bluetoothctl show", source)
        self.assertIn("ttyACM", source)


if __name__ == "__main__":
    unittest.main()
