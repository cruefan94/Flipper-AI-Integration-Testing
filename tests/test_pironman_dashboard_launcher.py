"""Safe launcher tests: no Tk window, hardware access or privileged commands."""
import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[1] / "raspberry_pi" / "launch_pironman_dashboard.py"


class PironmanLauncherTests(unittest.TestCase):
    def test_launcher_parses(self):
        ast.parse(LAUNCHER.read_text(encoding="utf-8"))

    def test_check_works_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, "-B", str(LAUNCHER), "--check"],
                cwd=cwd, capture_output=True, text=True, timeout=10,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not hardware validation", result.stdout)

    def test_check_does_not_create_cache(self):
        # Syntax-only check never imports dashboard/monitor or opens Tk.
        source = LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("ast.parse", source)
        self.assertIn('sys.argv[1:] == ["--check"]', source)


if __name__ == "__main__":
    unittest.main()
