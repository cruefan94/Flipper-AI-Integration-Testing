"""GPL flasher MD5 patch must reject short reads and failed verification."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from patch_esp_flasher_verify import patch_text,PatchMismatch

SOURCE="""// upstream unmodified GPL source fragment fixture
static esp_loader_error_t _flash_file(EspFlasherApp* app, char* filepath, uint32_t addr) {
    uint64_t size = storage_file_size(bin_file);
    loader_port_debug_print("Start programming\\n");
    while(size>0) {
        size_t to_read = 1024;
        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);
        esp_loader_flash_write(payload, num_bytes);
        size -= num_bytes;
    }
    // TODO verify
    return ESP_LOADER_SUCCESS;
}
"""

class VerifyPatchTests(unittest.TestCase):
    def test_md5_verification_is_required_before_success(self):
        patched=patch_text(SOURCE)
        self.assertIn("err = esp_loader_flash_verify();",patched)
        self.assertIn("FLASH VERIFICATION FAILED",patched)
        self.assertIn("Flash MD5 verification PASSED.",patched)
        self.assertIn("#if MD5_ENABLED",patched)
        self.assertIn("#else",patched)
        self.assertIn("return ESP_LOADER_ERROR_FAIL;",patched)
        self.assertLess(patched.index("err = esp_loader_flash_verify();"),
                        patched.index("return ESP_LOADER_SUCCESS;"))

    def test_sd_read_failure_and_empty_images_fail_closed(self):
        patched=patch_text(SOURCE)
        self.assertIn("if(size == 0 || size > 0xFFFFFFFFu)",patched)
        self.assertIn("if(num_bytes != to_read)",patched)
        self.assertIn("Firmware SD read failed",patched)
        self.assertIn("storage_file_close(bin_file)",patched)
        self.assertIn("storage_file_free(bin_file)",patched)

    def test_no_unreviewed_or_duplicate_patch(self):
        with self.assertRaises(PatchMismatch):
            patch_text(SOURCE.replace("// TODO verify","// changed upstream"))
        with self.assertRaises(PatchMismatch):
            patch_text(SOURCE+"\n    // TODO verify")
        with self.assertRaises(PatchMismatch):
            patch_text(patch_text(SOURCE))

    def test_no_blind_success_without_md5(self):
        modified=patch_text(SOURCE)
        self.assertIn('Flash MD5 verification unavailable: refusing success.',modified)
        self.assertIn('if(err != ESP_LOADER_SUCCESS)',modified)

if __name__=="__main__":unittest.main()
