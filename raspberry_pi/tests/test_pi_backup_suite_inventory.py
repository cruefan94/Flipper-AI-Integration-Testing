"""Synthetic tests for the read-only backup test-suite inventory."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from raspberry_pi.backup_suite_inventory import REQUIRED_SUITES, inspect_suite_presence


class BackupSuiteInventoryTests(unittest.TestCase):
    def test_empty_tree_reports_all_missing(self):
        with TemporaryDirectory() as directory:
            result = inspect_suite_presence(Path(directory))
        self.assertEqual(set(result), set(REQUIRED_SUITES))
        self.assertFalse(any(result.values()))

    def test_complete_tree_reports_all_present(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for filename in REQUIRED_SUITES.values():
                (root / filename).touch()
            result = inspect_suite_presence(root)
        self.assertTrue(all(result.values()))

    def test_partial_tree_identifies_missing_suite_without_paths(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / REQUIRED_SUITES["privacy_contract"]).touch()
            result = inspect_suite_presence(root)
        self.assertTrue(result["privacy_contract"])
        self.assertFalse(result["manifest_verifier"])
        self.assertFalse(result["readiness_contract"])
        self.assertNotIn(str(root), repr(result))

    def test_symlinked_suite_file_is_not_accepted(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.py"
            target.touch()
            for label, filename in REQUIRED_SUITES.items():
                (root / filename).symlink_to(target)
                self.assertFalse(inspect_suite_presence(root)[label])
                (root / filename).unlink()

    def test_symlinked_root_is_not_accepted(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            actual = root / "actual"
            actual.mkdir()
            for filename in REQUIRED_SUITES.values():
                (actual / filename).touch()
            link = root / "linked"
            link.symlink_to(actual, target_is_directory=True)
            self.assertFalse(any(inspect_suite_presence(link).values()))

    def test_directory_named_like_suite_is_not_accepted(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / REQUIRED_SUITES["manifest_verifier"]).mkdir()
            self.assertFalse(inspect_suite_presence(root)["manifest_verifier"])


if __name__ == "__main__":
    unittest.main()
