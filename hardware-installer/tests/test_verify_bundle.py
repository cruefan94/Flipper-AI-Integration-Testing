"""No-flash bundle safety contracts for attached expansion hardware."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verify_bundle import inspect,stage,BundleError

class InstallerPreflight(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.output=self.root/"out"
        self.output.mkdir()

    def make_bundle(self, board="esp32_wroom32_devkit", chip="esp32",
                    payload=b"image-data-for-testing", offset="0x10000",
                    name="firmware.bin", size=4194304):
        (self.root/name).write_bytes(payload)
        obj={"schema":1,"board_id":board,"chip":chip,"version":"dev-1",
             "flash_size_bytes":size,"images":[{"file":name,"offset":offset,
             "sha256":hashlib.sha256(payload).hexdigest()}]}
        if board=="arduino_uno_r3":
            obj["images"][0].pop("offset")
        manifest=self.root/"manifest.json"
        manifest.write_text(json.dumps(obj))
        return manifest,obj

    def test_classic_esp32_staging_requires_approval(self):
        m,doc=self.make_bundle()
        board,version,images=inspect(m,"esp32_wroom32_devkit")
        self.assertEqual(board.chip,"esp32")
        self.assertEqual(version,"dev-1")
        self.assertEqual(images[0][1],0x10000)
        with self.assertRaisesRegex(BundleError,"approval"):
            stage(m,"esp32_wroom32_devkit",self.output)
        self.assertEqual(list(self.output.iterdir()),[])
        copied=stage(m,"esp32_wroom32_devkit",self.output,approve=True)
        self.assertEqual(len(copied),2)
        self.assertEqual(copied[0].read_bytes(),b"image-data-for-testing")
        plan=(self.output/"flipper-ai-esp32-plan.txt").read_text()
        self.assertIn("FZHW1|BOARD=esp32_wroom32_devkit|CHIP=esp32|VER=dev-1|HW_UNVERIFIED=1\\n",plan)
        self.assertIn("IMG|firmware.bin|0x10000|",plan)
        self.assertIn("NOTICE|SD_COPY_ONLY|ESP_FLASHER_APPROVAL_REQUIRED",plan)
        with self.assertRaisesRegex(BundleError,"overwriting"):
            stage(m,"esp32_wroom32_devkit",self.output,approve=True)

    def test_existing_plan_blocks_staging_before_any_image_copy(self):
        m,_=self.make_bundle()
        plan=self.output/"flipper-ai-esp32-plan.txt"
        plan.write_text("Existing hardware plan: leave unchanged")
        with self.assertRaisesRegex(BundleError,"overwriting"):
            stage(m,"esp32_wroom32_devkit",self.output,approve=True)
        self.assertEqual(plan.read_text(),"Existing hardware plan: leave unchanged")
        self.assertFalse((self.output/"firmware.bin").exists())

    def test_cross_flash_chip_and_board_rejected(self):
        m,doc=self.make_bundle()
        with self.assertRaisesRegex(BundleError,"Selected board"):
            inspect(m,"flipper_wifi_devboard_s2")
        doc["chip"]="esp32s2"
        m.write_text(json.dumps(doc))
        with self.assertRaisesRegex(BundleError,"Chip mismatch"):
            inspect(m,"esp32_wroom32_devkit")

    def test_missing_or_wrong_hash_rejected(self):
        m,doc=self.make_bundle()
        (self.root/"firmware.bin").write_bytes(b"changed")
        with self.assertRaisesRegex(BundleError,"checksum"):
            inspect(m,"esp32_wroom32_devkit")

    def test_overlap_and_flash_capacity_rejected(self):
        m,doc=self.make_bundle()
        payload=b"second"
        (self.root/"another.bin").write_bytes(payload)
        doc["images"].append({"file":"another.bin","offset":"0x10000",
                              "sha256":hashlib.sha256(payload).hexdigest()})
        m.write_text(json.dumps(doc))
        with self.assertRaisesRegex(BundleError,"Overlapping"):
            inspect(m,"esp32_wroom32_devkit")
        doc["images"][1]["offset"]="0x400000"
        m.write_text(json.dumps(doc))
        with self.assertRaisesRegex(BundleError,"outside verified"):
            inspect(m,"esp32_wroom32_devkit")

    def test_directory_traversal_and_symbolic_link_rejected(self):
        m,doc=self.make_bundle()
        doc["images"][0]["file"]="../outside.bin"
        m.write_text(json.dumps(doc))
        with self.assertRaisesRegex(BundleError,"unsafe filename"):
            inspect(m,"esp32_wroom32_devkit")
        doc["images"][0]["file"]="firmware.bin"
        m.write_text(json.dumps(doc))
        (self.root/"firmware.bin").unlink()
        (self.root/"firmware.bin").symlink_to(m)
        with self.assertRaisesRegex(BundleError,"linked image"):
            inspect(m,"esp32_wroom32_devkit")

    def test_uno_r3_preflight_not_programmed_from_flipper(self):
        payload=b":0400000001020304F2\n:00000001FF\n"
        m,doc=self.make_bundle(board="arduino_uno_r3",chip="atmega328p",
                  payload=payload,name="blink.hex",size=32768)
        board,_,_=inspect(m,"arduino_uno_r3")
        self.assertFalse(board.flipper_flash)
        with self.assertRaisesRegex(BundleError,"No Flipper"):
            stage(m,"arduino_uno_r3",self.output,approve=True)
        doc["images"][0]["file"]="firmware.bin"
        m.write_text(json.dumps(doc))
        with self.assertRaises(BundleError):
            inspect(m,"arduino_uno_r3")

    def test_uno_r4_refused_until_backend_exists(self):
        payload=b":00000001FF\n"
        m,doc=self.make_bundle(board="arduino_uno_r4",chip="ra4m1",
                               payload=payload,name="firmware.hex",size=32768)
        with self.assertRaisesRegex(BundleError,"no installer backend"):
            inspect(m,"arduino_uno_r4")

    def test_partial_sd_write_rolls_back_incomplete_new_file(self):
        from unittest.mock import patch
        m,_=self.make_bundle()
        def interrupt(source,destination):
            destination.write(b"partial-image")
            raise OSError("simulated SD disconnect")
        with patch("verify_bundle.shutil.copyfileobj",side_effect=interrupt):
            with self.assertRaisesRegex(OSError,"SD disconnect"):
                stage(m,"esp32_wroom32_devkit",self.output,approve=True)
        self.assertEqual(list(self.output.iterdir()),[],
                         "A failed copy must never leave a bootable-looking partial .bin")

    def test_sd_copy_mismatch_is_rejected_and_removed(self):
        from unittest.mock import patch
        m,_=self.make_bundle()
        def corrupt(source,destination):
            destination.write(b"corrupted-output")
        with patch("verify_bundle.shutil.copyfileobj",side_effect=corrupt):
            with self.assertRaisesRegex(BundleError,"post-copy SHA256"):
                stage(m,"esp32_wroom32_devkit",self.output,approve=True)
        self.assertEqual(list(self.output.iterdir()),[],
                         "Corrupted staged files must be removed")

    def test_checksum_not_authentication_claim(self):
        s=(Path(__file__).resolve().parents[1]/"verify_bundle.py").read_text()
        self.assertIn("SHA256 checks integrity",s)
        self.assertNotIn("subprocess",s)
        self.assertNotIn("esptool.main",s)
        self.assertNotIn("avrdude",s)

if __name__=="__main__":unittest.main()
