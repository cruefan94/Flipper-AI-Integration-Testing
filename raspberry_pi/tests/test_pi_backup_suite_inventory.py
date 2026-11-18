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
        self.assertEqual(result["privacy_contract"], True)
        self.assertFalse(result["manifest_verifier"])
        self.assertFalse(result["readiness_contract"])
        self.assertNotIn(str(root), repr(result))


if __name__ == "__main__":
    unittest.main()
