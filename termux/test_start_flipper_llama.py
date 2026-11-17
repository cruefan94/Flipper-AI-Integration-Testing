"""Synthetic tests for the opt-in localhost llama.cpp launcher."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("start_flipper_llama.sh")


def launch(*args, path="/no-programs", home="/no-home", **extra_env):
    env = dict(os.environ, PATH=str(path), HOME=str(home), **extra_env)
    return subprocess.run(["/bin/sh", str(SCRIPT), *map(str, args)],
                          env=env, capture_output=True, text=True, timeout=10)


class TermuxLlamaLauncherTests(unittest.TestCase):
    def test_missing_and_non_gguf_weights_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            self.assertNotEqual(launch("start", base / "missing.gguf", home=base).returncode, 0)
            self.assertNotEqual(launch("start", "relative.gguf", home=base).returncode, 0)
            self.assertNotEqual(launch("start", base / "file.bin", home=base).returncode, 0)

    def test_command_matches_android_and_is_loopback_only(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            model = base / "model with spaces.gguf"
            model.write_text("synthetic data; not a model", encoding="utf-8")
            capture = base / "captured.txt"
            binary = base / "llama-server"
            binary.write_text(
                '#!/bin/sh\nprintf "%s\\n" "$@" > "$CAPTURE_PATH"\n',
                encoding="utf-8"
            )
            binary.chmod(0o700)
            process = launch("start", model, path=base, home=base,
                             CAPTURE_PATH=str(capture))
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(capture.read_text(encoding="utf-8").splitlines(), [
                "--model", str(model), "--host", "127.0.0.1",
                "--port", "9931", "--alias", "flipper-local",
                "--ctx-size", "2048", "--gpu-layers", "0",
                "--no-webui"
            ])

    def test_status_is_only_local_and_never_starts_server(self):
        with tempfile.TemporaryDirectory() as folder:
            process = launch("status", home=folder)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("curl is not installed", process.stderr)


if __name__ == "__main__":
    unittest.main()
