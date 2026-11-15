#!/usr/bin/env python3
"""Package a separately built GPL ESP Flasher FAP for encrypted private delivery.

Does NOT install firmware, write a Flipper SD card or program an ESP32.
Requires exact pinned, reviewed upstream and GPL patch revisions.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile

FORMAT="flipper-ai-esp32-programmer-v1"
UPSTREAM="1f6f801c3ebecbc4afbf6500564bf99748710e24"
FAP_NAME="esp_flasher.fap"
MANIFEST="SHA256-manifest.json"
NOTICE="READ_ME_BEFORE_INSTALL.txt"
LICENSE_NAME="LICENSE_GPL-3.0.txt"
SOURCE_INFO="SOURCE_PROVENANCE.txt"
ARCHIVE_NAME="esp32-programmer-UNTESTED.tar.gz"
MAX_FAP_BYTES=8*1024*1024
MAX_LICENSE_BYTES=256*1024
MAX_TEXT_BYTES=8*1024
NAMES={FAP_NAME,MANIFEST,NOTICE,LICENSE_NAME,SOURCE_INFO}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _read(path,limit):
    path=Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Missing or linked delivery input")
    if not 0<path.stat().st_size<=limit:
        raise ValueError("Empty or oversized delivery input")
    return path.read_bytes()


def _validate_fap(blob):
    if not 128<=len(blob)<=MAX_FAP_BYTES or not blob.startswith(b"\x7fELF"):
        raise ValueError("Missing or invalid compiled ESP Flasher ELF/FAP")


def _read_package(path):
    with tarfile.open(path,"r:gz") as tar:
        members=tar.getmembers()
        if len(members)!=len(NAMES):
            raise ValueError("Wrong ESP programmer delivery member count")
        if any(not m.isfile() or m.name not in NAMES or m.size > MAX_FAP_BYTES
               for m in members):
            raise ValueError("Archive contains an unsafe member")
        if {m.name for m in members}!=NAMES:
            raise ValueError("Missing, unexpected or duplicate delivery member")
        contents={}
        for m in members:
            fh=tar.extractfile(m)
            if fh is None: raise ValueError("Unreadable archive member")
            contents[m.name]=fh.read(MAX_FAP_BYTES+1)
    return contents


def verify(path):
    content=_read_package(path)
    _validate_fap(content[FAP_NAME])
    if b"GNU GENERAL PUBLIC LICENSE" not in content[LICENSE_NAME].upper():
        raise ValueError("Missing GPL-3.0 license notice")
    if len(content[LICENSE_NAME])>MAX_LICENSE_BYTES:
        raise ValueError("GPL license document too large")
    if len(content[NOTICE])>MAX_TEXT_BYTES or len(content[SOURCE_INFO])>MAX_TEXT_BYTES:
        raise ValueError("Description or provenance too large")
    try:
        manifest=json.loads(content[MANIFEST])
    except (ValueError,UnicodeError) as exc:
        raise ValueError("Invalid programmer manifest") from exc
    if manifest.get("format")!=FORMAT or manifest.get("app")!=FAP_NAME:
        raise ValueError("Unsupported programmer package")
    if manifest.get("upstream_revision")!=UPSTREAM or not manifest.get("hardware_unverified") is True:
        raise ValueError("Programmer provenance or safety status incorrect")
    patch=manifest.get("patch_revision")
    if not isinstance(patch,str) or len(patch)!=40 or any(c not in "0123456789abcdef" for c in patch):
        raise ValueError("Patch revision must be an exact pinned SHA")
    firmware_source=manifest.get("firmware_source_revision")
    if not isinstance(firmware_source,str) or len(firmware_source)!=40 or any(x not in "0123456789abcdef" for x in firmware_source):
        raise ValueError("Private firmware source revision must be an exact pinned SHA")
    target=manifest.get("target")
    if target!="Flipper Zero F7, custom pinned Momentum SDK":
        raise ValueError("Programmer target mismatch")
    for name in (FAP_NAME,LICENSE_NAME,NOTICE,SOURCE_INFO):
        info=manifest.get("files",{}).get(name,{})
        if info.get("sha256")!=digest(content[name]) or info.get("size")!=len(content[name]):
            raise ValueError("Programmer package content hash/size mismatch: "+name)
    if set(manifest["files"])!={FAP_NAME,LICENSE_NAME,NOTICE,SOURCE_INFO}:
        raise ValueError("Unexpected manifest file inventory")
    if (UPSTREAM.encode() not in content[SOURCE_INFO]
            or patch.encode() not in content[SOURCE_INFO]
            or firmware_source.encode() not in content[SOURCE_INFO]):
        raise ValueError("Source provenance does not match manifest")
    if b"NOT HARDWARE TESTED" not in content[NOTICE]:
        raise ValueError("Missing explicit hardware warning")
    if b"confirmation" not in content[NOTICE].lower():
        raise ValueError("Missing erase/write confirmation warning")
    return manifest


def pack(fap,license_path,output,patch_revision,momentum_revision,firmware_source_revision):
    blob=_read(fap,MAX_FAP_BYTES)
    _validate_fap(blob)
    license_text=_read(license_path,MAX_LICENSE_BYTES)
    if b"GNU GENERAL PUBLIC LICENSE" not in license_text.upper():
        raise ValueError("Expected complete GPL license")
    if not isinstance(patch_revision,str) or len(patch_revision)!=40 or any(x not in "0123456789abcdef" for x in patch_revision):
        raise ValueError("Expected immutable patch commit SHA")
    if not isinstance(momentum_revision,str) or len(momentum_revision)!=40 or any(x not in "0123456789abcdef" for x in momentum_revision):
        raise ValueError("Expected immutable custom Momentum commit SHA")
    if (not isinstance(firmware_source_revision,str) or len(firmware_source_revision)!=40
            or any(x not in "0123456789abcdef" for x in firmware_source_revision)):
        raise ValueError("Expected immutable private firmware source commit SHA")
    notice=("ESP32 PROGRAMMER — DEVELOPMENT ONLY — NOT HARDWARE TESTED\n"
            "Install esp_flasher.fap separately through an approved Flipper SD app method.\n"
            "This archive is NOT a Momentum .tgz and MUST NOT be flashed as firmware.\n"
            "The FAP needs the EXACT SDK used for the custom Momentum firmware build.\n"
            "Only use with the actual ESP-WROOM-32 chip confirmed and safe 3.3V UART wiring.\n"
            "Firmware erasure/programming needs separate on-device confirmation.\n"
            "Verify actual board model, ROM chip ID, flash capacity and .bin offsets.\n"
            "Check USB-to-UART contention and maintain BOOT/EN and qFlipper recovery.\n"
            "Never connect an Uno R3 5V UART directly to Flipper GPIO.\n"
            "Keep the current Flipper firmware unchanged until physical validation.\n").encode()
    provenance=(f"GPL-3.0 source: https://github.com/0xchocolate/flipperzero-esp-flasher\n"
                f"Pinned upstream commit: {UPSTREAM}\n"
                f"Published patch source: https://github.com/cruefan94/Flipper-AI-Integration-Testing/blob/{patch_revision}/hardware-installer/patch_esp_flasher_verify.py\n"
                f"Exact public patch commit: {patch_revision}\n"
                f"Custom Momentum pin: {momentum_revision}\n"
                f"Paired private firmware source commit: {firmware_source_revision}\n"
                "Any redistribution must comply with GPL-3.0 and provide corresponding source.\n").encode()
    files={FAP_NAME:blob,LICENSE_NAME:license_text,NOTICE:notice,SOURCE_INFO:provenance}
    manifest={
       "format":FORMAT, "target":"Flipper Zero F7, custom pinned Momentum SDK",
       "app":FAP_NAME,"upstream_revision":UPSTREAM,"patch_revision":patch_revision,
       "momentum_revision":momentum_revision,
       "firmware_source_revision":firmware_source_revision,
       "hardware_unverified":True,
       "files":{name:{"sha256":digest(data),"size":len(data)} for name,data in files.items()},
    }
    payload=dict(files)
    payload[MANIFEST]=(json.dumps(manifest,indent=2,sort_keys=True)+"\n").encode()
    output=Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("Refusing to overwrite programmer delivery")
    output.parent.mkdir(parents=True,exist_ok=True)
    with tarfile.open(output,"x:gz") as tar:
        for name,data in sorted(payload.items()):
            member=tarfile.TarInfo(name)
            member.mode=0o600
            member.size=len(data)
            tar.addfile(member,io.BytesIO(data))
    try:
        verify(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("pack")
    p.add_argument("--fap",type=Path,required=True)
    p.add_argument("--license",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--patch-revision",required=True)
    p.add_argument("--momentum-revision",required=True)
    p.add_argument("--firmware-source-revision",required=True)
    v=sub.add_parser("verify")
    v.add_argument("--archive",type=Path,required=True)
    args=parser.parse_args()
    if args.command=="pack":
        out=pack(args.fap,args.license,args.out,args.patch_revision,
                 args.momentum_revision,args.firmware_source_revision)
        print("Verified GPL ESP Flasher delivery (ENCRYPT before upload):",out)
    else:
        info=verify(args.archive)
        print("Verified untested programmer package",info["app"],info["momentum_revision"])


if __name__=="__main__":
    main()
