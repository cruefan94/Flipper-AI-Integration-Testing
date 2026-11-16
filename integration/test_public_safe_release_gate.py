import copy
import unittest
from public_safe_release_gate import validate

BASE = dict(schema_version=1,deliverable="f7_encrypted_updater",
            repository="cruefan94/Flipper-AI-Momentum-",source_commit="a"*40,
            workflow_run_url="https://github.com/cruefan94/Flipper-AI-Integration-Testing/actions/runs/43828499328",
            artifact_id=14207847319,artifact_sha256="b"*64,contract_version="AI1-v1",
            build_ci_passed=True,package_verified=False,hardware_verified=False,
            owner_approved=False,status="hold")

class GateTests(unittest.TestCase):
    def test_hold_is_valid_without_claiming_package_verified(self):
        self.assertTrue(validate(BASE))
    def test_reject_private_material(self):
        for field in ("token","private_firmware_source","diagnostic_log","encrypted_binary"):
            with self.subTest(field=field):
                item=copy.deepcopy(BASE);item[field]="not allowed"
                with self.assertRaises(ValueError):validate(item)
    def test_reject_false_promotion(self):
        item={**BASE,"status":"ready_for_owner_review"}
        with self.assertRaises(ValueError):validate(item)
    def test_f7_requires_approval(self):
        item={**BASE,"package_verified":True,"status":"ready_for_owner_review"}
        with self.assertRaises(ValueError):validate(item)
    def test_reject_unapproved_url(self):
        item={**BASE,"workflow_run_url":"https://example.com/actions/runs/1"}
        with self.assertRaises(ValueError):validate(item)
    def test_reject_bad_sha_and_non_boolean(self):
        for item in ({**BASE,"artifact_sha256":"bad"},{**BASE,"hardware_verified":"false"}):
            with self.assertRaises(ValueError):validate(item)
    def test_reject_cross_deliverable_source_mismatch(self):
        for item in (
            {**BASE, "repository": "cruefan94/Flipper-AI-Android-Satellite"},
            {**BASE, "deliverable": "android_test_apk"},
        ):
            with self.subTest(deliverable=item["deliverable"], repository=item["repository"]):
                with self.assertRaisesRegex(ValueError, "mismatch"):
                    validate(item)
    def test_android_test_only(self):
        item={**BASE,"deliverable":"android_test_apk",
              "repository":"cruefan94/Flipper-AI-Android-Satellite","status":"test_only"}
        self.assertTrue(validate(item))

if __name__=="__main__":unittest.main()
