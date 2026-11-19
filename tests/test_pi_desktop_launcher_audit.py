import tempfile
import unittest
from pathlib import Path
from raspberry_pi.desktop_launcher_audit import audit_file, scan

class LauncherAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def entry(self, body):
        p = self.root / "sample.desktop"
        p.write_text("[Desktop Entry]\nType=Application\nName=Example\n" + body, encoding="utf-8")
        return p

    def test_existing_executable(self):
        self.assertEqual(audit_file(self.entry("Exec=/bin/sh\n"))["status"], "executable_found")

    def test_missing_executable(self):
        self.assertEqual(audit_file(self.entry("Exec=definitely_not_a_real_pi_command_xyz\n"))["status"], "missing_executable")

    def test_missing_exec(self):
        self.assertEqual(audit_file(self.entry(""))["status"], "missing_exec")

    def test_hidden(self):
        self.assertEqual(audit_file(self.entry("Hidden=true\nExec=/bin/sh\n"))["status"], "hidden")

    def test_env_wrapper(self):
        self.assertEqual(audit_file(self.entry("Exec=env FOO=bar /bin/sh\n"))["status"], "review_wrapper")

    def test_bad_quote(self):
        self.assertEqual(audit_file(self.entry('Exec="unclosed\n'))["status"], "invalid_exec")

    def test_non_application(self):
        self.assertEqual(audit_file(self.entry("Type=Link\nExec=/bin/sh\n"))["status"], "not_application")

    def test_tryexec_missing(self):
        self.assertEqual(audit_file(self.entry("TryExec=definitely_not_a_real_pi_command_xyz\nExec=/bin/sh\n"))["status"], "missing_tryexec")

    def test_tryexec_existing(self):
        self.assertEqual(audit_file(self.entry("TryExec=/bin/sh\nExec=/bin/sh\n"))["status"], "executable_found")

    def test_tryexec_wrapper_needs_review(self):
        self.assertEqual(audit_file(self.entry("TryExec=env FOO=bar\nExec=/bin/sh\n"))["status"], "review_tryexec")

    def test_scan(self):
        self.entry("Exec=/bin/sh\n")
        self.assertEqual(len(scan([self.root])), 1)

if __name__ == "__main__":
    unittest.main()
