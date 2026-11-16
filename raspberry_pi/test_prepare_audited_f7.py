"""Synthetic tests: pinned download, passphrase-gated verification, no flash."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

FILE = Path(__file__).resolve().parent / "prepare_audited_f7.py"
spec = importlib.util.spec_from_file_location("prepare_audited_f7", FILE)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class TTY(io.StringIO):
    def isatty(self):
        return True


class PrepareAuditedF7Tests(unittest.TestCase):
    def test_pins_audited_artifact(self):
        self.assertEqual(p.RUN_ID, 43782149547)
        self.assertEqual(p.ARTIFACT_ID, 14189530383)
        self.assertEqual(p.SOURCE_REVISION, "642e267612f1c555c60eb0db2ec167f5d2ab036f")
        self.assertIn("099e36509814ed975d17b108124f1a0c36a907b7", p.VALIDATOR_URL)

    def run_simulated(self, wrong_source=False, expired=False):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            baseline = home / "flipper-z-f7-update-mntm-012.tgz"
            baseline.write_bytes(b"RECOVERY: NEVER OVERWRITE")
            fake_validator = '''
from pathlib import Path

def decrypt_and_verify_artifact(encrypted, decrypted, visible=False):
    assert encrypted.exists()
    assert not visible
    return ("flipper-z-f7-update-mntm-012.tgz", b"FAKE-TEST-CANDIDATE", ''' + (
                '"wrong"' if wrong_source else repr(p.SOURCE_REVISION)) + ''')

def sha256(data):
    import hashlib
    return hashlib.sha256(data).hexdigest()

def save_candidate(dst, name, data, private=True):
    import hashlib
    dst.mkdir(parents=True, exist_ok=True)
    path = dst / name
    if path.exists() and path.read_bytes() != data:
        path = dst / (name[:-4] + "-" + hashlib.sha256(data).hexdigest()[:12] + ".tgz")
    with path.open("xb") as f:
        f.write(data)
    return path
'''
            def fake_download(dest):
                dest.write_text(fake_validator)
            def fake_command(argv, **kwargs):
                if argv[:2] == ["gh", "run"]:
                    assert "--dir" in argv
                    work = Path(argv[argv.index("--dir") + 1])
                    (work / p.ENCRYPTED_NAME).write_bytes(b"MOCK-ENCRYPTED")
                    return ""
                if "artifacts" in argv[-1]:
                    return json.dumps({"artifacts": [{
                        "id": p.ARTIFACT_ID, "name": p.ARTIFACT_NAME,
                        "expired": expired
                    }]})
                return json.dumps({"conclusion": "success", "status": "completed"})
            with patch.object(p.sys, "stdin", TTY()), \
                 patch.object(p.Path, "home", return_value=home), \
                 patch.object(p, "download_validator", side_effect=fake_download), \
                 patch.object(p, "command", side_effect=fake_command), \
                 patch.dict(p.sys.modules, {}, clear=False):
                # Import from the newly staged directory each run.
                p.sys.modules.pop("firmware_to_phone", None)
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    if wrong_source or expired:
                        with self.assertRaises(RuntimeError):
                            p.main()
                    else:
                        self.assertEqual(p.main(), 0)
                self.assertEqual(baseline.read_bytes(), b"RECOVERY: NEVER OVERWRITE")
                out = home / "FlipperAI_ReadyToFlash"
                if wrong_source or expired:
                    self.assertFalse(out.exists())
                else:
                    self.assertEqual(len(list(out.glob("*.tgz"))), 1)
                    self.assertEqual(next(out.glob("*.tgz")).read_bytes(),
                                     b"FAKE-TEST-CANDIDATE")
                    self.assertIn("NO FLASH", output.getvalue())
                p.sys.modules.pop("firmware_to_phone", None)

    def test_verified_download_keeps_recovery_copy(self):
        self.run_simulated()

    def test_wrong_source_never_writes_candidate(self):
        self.run_simulated(wrong_source=True)

    def test_expired_artifact_never_requests_passphrase(self):
        self.run_simulated(expired=True)


if __name__ == "__main__":
    unittest.main()
