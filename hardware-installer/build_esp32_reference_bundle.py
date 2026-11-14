#!/usr/bin/env python3
"""Generate a reproducible *reference* ESP32 firmware bundle from PlatformIO.

Never runs a flasher or claims the owner's actual flash size, chip, partition
layout, USB-to-UART isolation, or hardware compatibility have been verified.
A manifest SHA256 is an integrity check, not a publisher signature.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from verify_bundle import inspect, BundleError

# Pinned build profile. These offsets are the classic esp32dev Arduino defaults
# used by the current reference build, NOT discovered from the user's chip.
BOARD="esp32_wroom32_devkit"
CHIP="esp32"
PIO_ENV="esp32dev"
REFERENCE_FLASH_SIZE=4*1024*1024
OFFSETS={"bootloader.bin":"0x1000","partitions.bin":"0x8000","firmware.bin":"0x10000"}
VERSION_PATTERN=re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}$")

NOTICE="""FLIPPER AI ESP32 REFERENCE BUNDLE - NOT VERIFIED FOR ANY REAL BOARD

This is a precompiled *reference* classic ESP32 / ESP-WROOM-32 build.
Target board named esp32_wroom32_devkit is the user's 38-pin development
board family, NOT verified pin continuity, flash size or ROM chip identity.

The declared 4 MiB capacity and 0x1000 / 0x8000 / 0x10000 offsets come
from the current default ESP32 Arduino PlatformIO reference build. Confirm
them against the installed chip, toolchain and full partition layout.

Before programming: use a trusted source build, inspect all binaries and
SHA256 checksums; confirm chip model, actual flash capacity, 3.3V UART,
BOOT/EN behavior, shared ground, USB-UART driver isolation and recovery.
Flipper uses UART0 pins 13/14 for ESP Flasher; close Flipper AI and Manager.
Never use an ESP32-S2 image or Arduino Uno firmware with this ESP32.

The generator DOES NOT FLASH OR ERASE anything. SD staging is a separate
opt-in action; final board programming MUST be confirmed on the Flipper.
Compiled source and host tests are NOT actual-device verification.
"""

def package(build:Path,out:Path,version:str,source_revision:str="unknown")->Path:
    if not VERSION_PATTERN.fullmatch(version):
        raise BundleError("Invalid reference firmware version")
    if not source_revision or len(source_revision)>96 or not re.fullmatch(r"[A-Za-z0-9_.-]+",source_revision):
        raise BundleError("Invalid source revision label")
    build=Path(build)
    out=Path(out)
    if out.exists() or out.is_symlink():
        raise BundleError("Refusing to overwrite existing bundle path")
    if not build.is_dir() or build.is_symlink():
        raise BundleError("Expected a local, real PlatformIO esp32dev build directory")
    for name in OFFSETS:
        src=build/name
        if src.is_symlink() or not src.is_file() or not 1<=src.stat().st_size<REFERENCE_FLASH_SIZE:
            raise BundleError("Reference image missing, linked or outside size limit: "+name)
        # ESP32 bootloader and app images start with Espressif binary magic 0xE9.
        if name!="partitions.bin":
            with src.open("rb") as fp:
                if fp.read(1)!=b"\xE9":
                    raise BundleError("Invalid ESP32 binary magic for "+name)
    out.mkdir(parents=True,exist_ok=False)
    try:
        imgs=[]
        for name,offset in OFFSETS.items():
            shutil.copyfile(build/name,out/name)
            digest=hashlib.sha256((out/name).read_bytes()).hexdigest()
            imgs.append({"file":name,"offset":offset,"sha256":digest})
        manifest={
            "schema":1,
            "board_id":BOARD,
            "chip":CHIP,
            "version":version,
            "flash_size_bytes":REFERENCE_FLASH_SIZE,
            "hardware_confirmation_required":True,
            "build_profile":PIO_ENV,
            "source_revision":source_revision,
            "images":imgs,
        }
        (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        (out/"READ_ME_BEFORE_FLASHING.txt").write_text(NOTICE,encoding="utf-8")
        # Verify actual artifact bytes as if consumed by the separate SD stager.
        inspected_board,_,validated=inspect(out/"manifest.json",BOARD)
        if inspected_board.chip!=CHIP or len(validated)!=len(OFFSETS):
            raise BundleError("Generated bundle failed chip/manifest validation")
        return out/"manifest.json"
    except Exception:
        shutil.rmtree(out)
        raise

def main():
    p=argparse.ArgumentParser(description="Generate untested ESP32 reference image bundle; no flash")
    p.add_argument("--build",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--version",default="0.1.0-dev")
    p.add_argument("--source-revision",default="unknown")
    args=p.parse_args()
    print(package(args.build,args.out,args.version,args.source_revision))
    print("REFERENCE ONLY: confirmed exact chip/flash size and owner approval REQUIRED.")

if __name__=="__main__":
    main()
