"""Offline tests for conservative backup-evidence evaluation."""
import unittest
from raspberry_pi.qflipper_backup_evidence import assess_backup_evidence


class BackupEvidenceTests(unittest.TestCase):
    def test_empty_evidence_is_not_complete(self):
        report = assess_backup_evidence({})
        self.assertFalse(report["evidence_complete"])
        self.assertFalse(report["safe_to_flash"])

    def test_strings_and_port_inventory_do_not_count(self):
        report = assess_backup_evidence({
            "owner_confirmed_backup_exists": "true",
            "owner_confirmed_backup_hash_matches": 1,
            "usb_serial_candidates": 1,
            "safe_to_flash": True,
        })
        self.assertFalse(report["evidence_complete"])
        self.assertFalse(report["hardware_verified"])
        self.assertFalse(report["safe_to_flash"])

    def test_complete_owner_checklist_is_still_not_hardware_validation(self):
        report = assess_backup_evidence({
            "owner_confirmed_backup_exists": True,
            "owner_confirmed_backup_hash_matches": True,
            "owner_confirmed_backup_stored_separately": True,
            "owner_confirmed_restore_procedure_reviewed": True,
        })
        self.assertTrue(report["evidence_complete"])
        self.assertFalse(report["backup_restored_on_device"])
        self.assertFalse(report["hardware_verified"])
        self.assertFalse(report["safe_to_flash"])


if __name__ == "__main__":
    unittest.main()
