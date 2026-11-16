"""Public-safe, host-only Raspberry Pi bridge regressions. No device or tokens needed."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "flipper_ai_pi_bridge", ROOT / "raspberry_pi" / "pi_bridge.py")
pi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pi)


def issue(operation="diagnostics", *, owner="cruefan94", device="raspberrypi4b",
          title="[Pi] Check Raspberry Pi", args=None):
    return {
        "number": 123,
        "state": "open",
        "title": title,
        "user": {"login": owner},
        "body": json.dumps({
            "schema": 1, "device": device,
            "operation": operation, "args": {} if args is None else args,
        }),
    }


def make_f7(folder: Path, *, target="7", extra=None):
    path = folder / "flipper-z-f7-update-fixture.tgz"
    members = {
        "f7-update-test/update.fuf": (
            "Filetype: Flipper firmware upgrade configuration\n"
            "Target: " + target + "\nLoader: updater.bin\n"
            "Firmware: firmware.dfu\n").encode(),
        "f7-update-test/updater.bin": b"SYNTHETIC NOT FLASHABLE",
        "f7-update-test/firmware.dfu": b"SYNTHETIC NOT FLASHABLE",
    }
    if extra:
        members.update(extra)
    with tarfile.open(path, "w:gz") as archive:
        for name, data in members.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
    return path


class RaspberryPiBridgeTest(unittest.TestCase):
    def test_accept_only_owner_and_exact_device(self):
        self.assertEqual(pi.parse_issue(issue())["operation"], "diagnostics")
        self.assertIsNone(pi.parse_issue(issue(owner="someone_else")))
        self.assertIsNone(pi.parse_issue(issue(device="phone")))
        self.assertIsNone(pi.parse_issue(issue(title="[Termux] Try")))
        self.assertIsNone(pi.parse_issue(issue(operation="shell")))
        self.assertIsNone(pi.parse_issue(issue(operation="flash_firmware")))
        self.assertIsNone(pi.parse_issue(issue(args={"command": "rm -rf"})))
        self.assertIsNone(pi.parse_issue(issue(operation="workflow_runs", args={"repo": "testing", "cmd": "x"})))
        pulled = issue()
        pulled["pull_request"] = {"url": "https://example.invalid"}
        self.assertIsNone(pi.parse_issue(pulled))

    def test_valid_native_f7_is_inspected_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            f = make_f7(Path(d))
            report = pi.check_native_f7(f)
            self.assertEqual(report["f7_native_structure"], "validated")
            self.assertEqual(len(report["sha256"]), 64)
            self.assertFalse(report["hardware_tested"])
            self.assertIn("not independently", report["firmware_source_revision"])
            self.assertTrue(f.exists())

    def test_wrong_f7_target_refused(self):
        with tempfile.TemporaryDirectory() as d:
            f = make_f7(Path(d), target="6")
            with self.assertRaisesRegex(pi.BridgeError, "Wrong firmware hardware target"):
                pi.check_native_f7(f)

    def test_archive_path_traversal_refused(self):
        with tempfile.TemporaryDirectory() as d:
            f = make_f7(Path(d), extra={"../other.bin": b"not safe"})
            with self.assertRaisesRegex(pi.BridgeError, "Unsafe member"):
                pi.check_native_f7(f)

    def test_bluetooth_usb_diagnostics_do_not_report_mac_or_serial(self):
        with patch.object(pi, "capture", return_value=(0, "Controller 11:22:33:44:55:66\n Powered: yes")), \
             patch.object(pi, "usb_status", return_value={"ttyACM": [], "ttyUSB": []}), \
             patch.object(pi, "qflipper_executable", return_value=None), \
             patch.object(pi.shutil, "which", return_value=None):
            result = pi.diagnostics()
        self.assertEqual(result["bluetooth_adapter_powered"], "yes")
        self.assertNotIn("11:22:33", json.dumps(result))
        self.assertIs(result["automatic_flashing"], False)

    def test_no_shell_exec_or_flash_operation_exposed(self):
        self.assertNotIn("shell", pi.OPS)
        self.assertNotIn("flash", pi.OPS)
        with self.assertRaisesRegex(pi.BridgeError, "Unrecognized"):
            pi.execute("shell", {"command": "pwd"})
        with self.assertRaisesRegex(pi.BridgeError, "approval-required"):
            pi.execute("launch_qflipper", {})

    def test_private_issue_is_processed_once_and_reported(self):
        with tempfile.TemporaryDirectory() as d, \
             patch.object(pi, "STATE", Path(d)), \
             patch.object(pi, "diagnostics", return_value={"healthy": True}):
            calls = []
            def fake_gh(method, path, payload=None):
                calls.append((method, path, payload))
                if method == "GET":
                    return [issue()] if "page=1" in path else []
                return {}
            with patch.object(pi, "gh", side_effect=fake_gh):
                pi.poll_once()
                pi.poll_once()
            messages = [c for c in calls if c[0] == "POST"]
            self.assertEqual(len(messages), 1)
            self.assertIn('"healthy": true', messages[0][2]["body"].lower())
            self.assertTrue((Path(d) / "123.reported").exists())
            self.assertTrue((Path(d) / "123.claimed").exists())

    def test_qflipper_launch_needs_local_keyboard_approval(self):
        with tempfile.TemporaryDirectory() as d, \
             patch.object(pi, "STATE", Path(d)):
            with patch.object(pi, "gh", return_value=[issue("launch_qflipper")]):
                pi.poll_once()
            self.assertTrue((Path(d) / "123.pending.json").exists())
            with patch.object(pi, "gh", return_value=issue("launch_qflipper")), \
                 patch("builtins.input", return_value="NO"), \
                 patch.object(pi.subprocess, "Popen") as start:
                with self.assertRaisesRegex(pi.BridgeError, "Not approved"):
                    pi.approve(123)
                start.assert_not_called()
            self.assertFalse((Path(d) / "123.launched").exists())

    def test_optional_openai_never_sent_without_explicit_key(self):
        with patch.dict(pi.os.environ, {"FLIPPER_PI_AI_PROVIDER": "openai"}, clear=True):
            with self.assertRaisesRegex(pi.BridgeError, "no key configured"):
                pi.ask("What's my Flipper status?")
        with self.assertRaisesRegex(pi.BridgeError, "2,500"):
            pi.ask("x" * 2501)

    def test_disallowed_workflow_repo_rejected(self):
        with self.assertRaisesRegex(pi.BridgeError, "Unknown repository"):
            pi.workflow_runs("random-user/secret-repo")


if __name__ == "__main__":
    unittest.main()
