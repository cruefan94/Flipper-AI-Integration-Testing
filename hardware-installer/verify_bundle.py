#!/usr/bin/env python3
"""Flipper AI hardware firmware selection/staging preflight (NO FLASHING).

Checks conservative board/chip compatibility, checksums, offsets and sizes.
SHA256 checks integrity against a manifest, not publisher authenticity.
Requires a separately approved ESP Flasher or USB-host backend for writing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
from board_profiles import match

_SAFE_NAME=re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,79}$")
_SHA256=re.compile(r"^[0-9a-fA-F]{64}$")

class BundleError(ValueError):
    pass

def _hex_valid(blob):
    """Validate Intel HEX records and checksums for Uno R3; no upload."""
    try: lines=blob.decode("ascii").splitlines()
    except UnicodeDecodeError: return False
    if not lines or len(lines)>65536: return False
    eof=False
    saw_data=False
    high=0
    for i,line in enumerate(lines):
        if not line.startswith(":") or len(line)<11 or len(line)%2!=1: return False
        try:rec=bytes.fromhex(line[1:])
        except ValueError:return False
        if len(rec)<5 or rec[0]!=len(rec)-5 or sum(rec)%256:return False
        length,hi,lo,typ=rec[:4]
        address=hi*256+lo
        if typ==0:
            if length>0:saw_data=True
            if high+address+length>32768:return False
        elif typ==1:
            if length!=0 or i!=len(lines)-1:return False
            eof=True
        elif typ==4:
            if length!=2:return False
            high=int.from_bytes(rec[4:6],"big")*65536
            if high!=0:return False
        elif typ==2:
            # A 20-bit segment outside the 328P's 32KB flash is unsafe.
            if length!=2:return False
            high=int.from_bytes(rec[4:6],"big")*16
            if high>32768:return False
        else:return False
    return eof and saw_data

def inspect(manifest:Path,selected_board:str):
    manifest=Path(manifest)
    if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>32768:
        raise BundleError("Missing, symlinked or oversized bundle manifest")
    try: doc=json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:raise BundleError("Invalid bundle JSON") from exc
    if not isinstance(doc,dict) or doc.get("schema")!=1:
        raise BundleError("Unsupported bundle schema")
    if doc.get("board_id")!=selected_board:
        raise BundleError("Selected board differs from manifest target")
    try: board=match(selected_board,doc.get("chip"))
    except ValueError as exc:raise BundleError(str(exc)) from exc
    version=doc.get("version")
    if not isinstance(version,str) or not _SAFE_NAME.fullmatch(version):
        raise BundleError("Invalid firmware version")
    images=doc.get("images")
    if not isinstance(images,list) or not 1<=len(images)<=6:
        raise BundleError("One to six named images are required")
    cap=doc.get("flash_size_bytes")
    if board.chip.startswith("esp32"):
        if type(cap) is not int or cap not in (4194304,8388608,16777216):
            raise BundleError("Confirm exact ESP32 flash size (4, 8 or 16 MiB)")
    else:
        if cap!=32768:raise BundleError("Uno R3 must use 32768-byte flash capacity")
        if len(images)!=1:raise BundleError("Uno R3 requires one Intel HEX file")
    verified=[]
    seen=set()
    ranges=[]
    for item in images:
        if not isinstance(item,dict):raise BundleError("Invalid image record")
        filename=item.get("file")
        if not isinstance(filename,str) or not _SAFE_NAME.fullmatch(filename) or filename in (".","..") or filename in seen:
            raise BundleError("Duplicate or unsafe filename")
        seen.add(filename)
        target=manifest.parent / filename
        if target.is_symlink() or not target.is_file():
            raise BundleError("Missing or linked image")
        if not 1<=target.stat().st_size<=8388608:
            raise BundleError("Image size outside safety limit")
        blob=target.read_bytes()
        sha=item.get("sha256")
        if not isinstance(sha,str) or not _SHA256.fullmatch(sha) or hashlib.sha256(blob).hexdigest()!=sha.lower():
            raise BundleError("Image checksum does not match bundle manifest")
        if board.chip.startswith("esp32"):
            value=item.get("offset")
            if not isinstance(value,str) or not re.fullmatch(r"0x[0-9a-fA-F]+",value):
                raise BundleError("ESP32 image needs an explicit hexadecimal offset")
            offset=int(value,16)
            if offset%4096 or offset+len(blob)>cap:
                raise BundleError("ESP32 image offset/size outside verified flash range")
            if not filename.endswith(".bin"):raise BundleError("ESP32 images must be .bin")
            ranges.append((offset,offset+len(blob)))
        else:
            if "offset" in item or not filename.endswith(".hex") or not _hex_valid(blob):
                raise BundleError("Uno R3 needs a valid offset-free Intel HEX image")
            offset=None
        verified.append((filename,offset,sha.lower()))
    ranges.sort()
    if any(a[1]>b[0] for a,b in zip(ranges,ranges[1:])):
        raise BundleError("Overlapping ESP32 flash regions")
    return board,version,verified

def stage(manifest:Path,selected_board:str,destination:Path,approve:bool=False):
    board,version,images=inspect(manifest,selected_board)
    if not approve:raise BundleError("Explicit staging approval is required")
    if not board.flipper_flash:raise BundleError("No Flipper firmware staging backend for this board")
    destination=Path(destination)
    if destination.is_symlink() or not destination.is_dir():
        raise BundleError("Destination must be an existing non-symlink directory")
    if any((destination/name).exists() or (destination/name).is_symlink() for name,_,_ in images):
        raise BundleError("Destination has existing file; overwriting forbidden")
    # Validate all images and targets before staging. Never trigger a flash.
    written=[]
    try:
        for name,_,_ in images:
            source=Path(manifest).parent/name
            target=destination/name
            with source.open("rb") as src, target.open("xb") as dst:
                shutil.copyfileobj(src,dst)
            written.append(target)
        return written
    except OSError:
        for entry in written:entry.unlink(missing_ok=True)
        raise

def main():
    parser=argparse.ArgumentParser(description="Review and stage hardware firmware only. NEVER flashes.")
    parser.add_argument("manifest",type=Path)
    parser.add_argument("--board",required=True,help="Owner-confirmed board ID, not an automatic guess")
    parser.add_argument("--stage-to",type=Path)
    parser.add_argument("--approve-stage",action="store_true",help="Explicit approval to copy checked images, never flash")
    args=parser.parse_args()
    try:
        board,version,images=inspect(args.manifest,args.board)
        print("BOARD:",board.description,"CHIP:",board.chip,"VERSION:",version)
        for name,offset,digest in images:
            print("FILE",name,"OFFSET",hex(offset) if offset is not None else "N/A","SHA256",digest)
        print("WARNING:",board.warning)
        print("Manifest hashes verify integrity only; independently verify firmware origin,")
        print("board pinout, UART voltage, flash size, image offsets and recovery.")
        if args.stage_to:
            for path in stage(args.manifest,args.board,args.stage_to,args.approve_stage):
                print("STAGED:",path)
            print("NO FLASH PERFORMED. Select images and confirm write in ESP Flasher.")
    except (BundleError,OSError,KeyError) as exc:
        parser.exit(2,"REFUSED: "+str(exc)+"\n")

if __name__=="__main__": main()
