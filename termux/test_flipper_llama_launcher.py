"""Offline shell tests: the optional llama.cpp launcher must stay loopback-only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).with_name("start_flipper_llama.sh")


class LocalLlamaLauncherTests(unittest.TestCase):
    def test_posix_shell_syntax(self):
        run=subprocess.run(["sh","-n",str(SCRIPT)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_requires_an_existing_absolute_gguf(self):
        run=subprocess.run(["sh",str(SCRIPT),"start","relative.gguf"],
            capture_output=True,text=True)
        self.assertNotEqual(run.returncode,0)
        self.assertIn("absolute path",run.stderr)

    def test_verified_model_starts_only_stub_loopback_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            fake_bin=base/"bin"
            fake_bin.mkdir()
            server=fake_bin/"llama-server"
            server.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\"\n",encoding="utf-8")
            server.chmod(0o755)
            model=base/"dummy.gguf"
            model.write_bytes(b"fake - no weights or inference")
            env=dict(os.environ)
            env["PATH"]=str(fake_bin)+os.pathsep+env.get("PATH","")
            run=subprocess.run(["sh",str(SCRIPT),"start",str(model)],
                env=env,capture_output=True,text=True,timeout=5)
            self.assertEqual(run.returncode,0,run.stderr)
            words=run.stdout.splitlines()
            for flag,expected in (("--host","127.0.0.1"),
                                  ("--port","9931"),
                                  ("--alias","flipper-local"),
                                  ("--gpu-layers","0")):
                self.assertIn(flag,words)
                self.assertEqual(words[words.index(flag)+1],expected)
            self.assertIn("--no-webui",words)
            self.assertNotIn("0.0.0.0",words)


if __name__=="__main__":
    unittest.main()
