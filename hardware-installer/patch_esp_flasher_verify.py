#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reviewable patch for upstream GPL-3.0 ESP Flasher, pinned at 1f6f801c.
Compile upstream+patch, never pretend a successful write proves flash integrity.

Upstream: https://github.com/0xchocolate/flipperzero-esp-flasher
Library: Espressif esp-serial-flasher MD5_ENABLED esp_loader_flash_verify().
Does not flash, run a serial programmer or alter hardware by itself.
"""
from pathlib import Path
import argparse
import sys

UPSTREAM_SHA="1f6f801c3ebecbc4afbf6500564bf99748710e24"

class PatchMismatch(RuntimeError):
    pass

def once(source,from_text,to_text):
    if source.count(from_text)!=1:raise PatchMismatch(
        "Upstream ESP Flasher changed; refusing unreviewed blind patch")
    return source.replace(from_text,to_text,1)

def patch_text(source):
    if "Flipper AI: checked flash MD5" in source:
        raise PatchMismatch("Already patched")
    source=once(source,
      "    uint64_t size = storage_file_size(bin_file);",
      """    uint64_t size = storage_file_size(bin_file);
    if(size == 0 || size > 0xFFFFFFFFu) {
        loader_port_debug_print("Refusing an empty or too-large flash image.\\n");
        storage_file_close(bin_file);
        storage_file_free(bin_file);
        return ESP_LOADER_ERROR_FAIL;
    }""")
    source=once(source,
      "        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);",
      """        uint16_t num_bytes = storage_file_read(bin_file, payload, to_read);
        /* A short/empty SD read must never be mistaken for a completed write.
         * The original loop could retry an empty read indefinitely. */
        if(num_bytes != to_read) {
            loader_port_debug_print("Firmware SD read failed or was incomplete.\\n");
            storage_file_close(bin_file);
            storage_file_free(bin_file);
            return ESP_LOADER_ERROR_FAIL;
        }""")
    source=once(source,
      "    // TODO verify",
      """    /* Flipper AI: checked flash MD5 against the bytes sent to the chip.
     * This is not a cryptographic publisher signature or a hardware test.
     * Fail closed if a target does not implement flash MD5 verification. */
#if MD5_ENABLED
    loader_port_debug_print("Verifying programmed flash MD5...\\n");
    err = esp_loader_flash_verify();
    if(err != ESP_LOADER_SUCCESS) {
        snprintf(user_msg, sizeof(user_msg),
                 "FLASH VERIFICATION FAILED: %d\\n", err);
        loader_port_debug_print(user_msg);
        storage_file_close(bin_file);
        storage_file_free(bin_file);
        return err;
    }
    loader_port_debug_print("Flash MD5 verification PASSED.\\n");
#else
    loader_port_debug_print("Flash MD5 verification unavailable: refusing success.\\n");
    storage_file_close(bin_file);
    storage_file_free(bin_file);
    return ESP_LOADER_ERROR_FAIL;
#endif""")
    return source

def main():
    parser=argparse.ArgumentParser(description="GPL ESP Flasher MD5 verification patch only")
    parser.add_argument("checkout",type=Path)
    args=parser.parse_args()
    root=args.checkout.resolve()
    if not (root/"LICENSE").is_file() or not (root/"application.fam").is_file():
        parser.exit(2,"Refusing unknown ESP Flasher checkout\n")
    import subprocess
    sha=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                 text=True).strip()
    if sha!=UPSTREAM_SHA:
        parser.exit(2,"Unexpected upstream revision: refusing patch\n")
    path=root/"esp_flasher_worker.c"
    if path.is_symlink() or not path.is_file():
        parser.exit(2,"Flasher worker source missing or symlinked\n")
    try:patched=patch_text(path.read_text())
    except PatchMismatch as exc:parser.exit(2,str(exc)+"\n")
    path.write_text(patched)
    print("Applied GPL-licensed Flipper AI flash MD5 verification patch at",sha)

if __name__=="__main__":main()
