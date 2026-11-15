#!/usr/bin/env python3
"""Public fixture-only tests for GPL ESP Flasher encrypted delivery packaging."""
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "esp_delivery",ROOT/"scripts/prepare_esp_flasher_delivery.py")
pkg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pkg)
PATCH="9a3adae719132d862ae9708bfd820c13b7e59abc"
MOMENTUM="d3f89dfe2ef6b01839201598e9be1590cba80322"

class FlasherDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.fap=self.root/"esp_flasher.fap"
        # Synthetic ELF signature; NOT an actual flasher or distributable app.
        self.fap.write_bytes(b"\x7fELF"+b"TEST ONLY"*20)
        self.license=self.root/"LICENSE"
        self.license.write_text("GNU GENERAL PUBLIC LICENSE\nVersion 3, 29 June 2007\nTEST FIXTURE")
        self.output=self.root/"programmer.tar.gz"

    def pack(self):
        return pkg.pack(self.fap,self.license,self.output,PATCH,MOMENTUM)

    def repack(self,mod):
        with tarfile.open(self.output,"r:gz") as tar:
            contents={m.name:tar.extractfile(m).read() for m in tar.getmembers()}
        mod(contents)
        modified=self.root/"tampered.tar.gz"
        with tarfile.open(modified,"w:gz") as tar:
            for name,blob in contents.items():
                member=tarfile.TarInfo(name)
                member.size=len(blob)
                tar.addfile(member,io.BytesIO(blob))
        return modified

    def test_package_verified_and_plaintext_not_published_by_tool(self):
        path=self.pack()
        result=pkg.verify(path)
        self.assertEqual(result["format"],pkg.FORMAT)
        self.assertEqual(result["app"],"esp_flasher.fap")
        self.assertEqual(result["upstream_revision"],pkg.UPSTREAM)
        self.assertEqual(result["patch_revision"],PATCH)
        self.assertEqual(result["momentum_revision"],MOMENTUM)
        self.assertTrue(result["hardware_unverified"])
        with tarfile.open(path) as tar:
            self.assertEqual({m.name for m in tar.getmembers()},pkg.NAMES)
            note=tar.extractfile(pkg.NOTICE).read().decode()
            self.assertIn("NOT HARDWARE TESTED",note)
            self.assertIn("confirmation",note.lower())
            source=tar.extractfile(pkg.SOURCE_INFO).read().decode()
            self.assertIn("GPL-3.0 source",source)
            self.assertIn(PATCH,source)
            self.assertIn(pkg.UPSTREAM,source)

    def test_refuse_non_elf_or_bad_license_before_creating_package(self):
        self.fap.write_bytes(b"not an ELF, not a FAP"*15)
        with self.assertRaisesRegex(ValueError,"ELF"):
            self.pack()
        self.assertFalse(self.output.exists())
        self.fap.write_bytes(b"\x7fELF"+b"TEST"*40)
        self.license.write_text("Non-GPL readme")
        with self.assertRaisesRegex(ValueError,"GPL"):
            self.pack()
        self.assertFalse(self.output.exists())

    def test_refuse_overwrite_and_unpinned_source(self):
        with self.assertRaisesRegex(ValueError,"patch commit"):
            pkg.pack(self.fap,self.license,self.output,"main",MOMENTUM)
        with self.assertRaisesRegex(ValueError,"Momentum commit"):
            pkg.pack(self.fap,self.license,self.output,PATCH,"latest")
        self.pack()
        with self.assertRaisesRegex(ValueError,"overwrite"):
            self.pack()

    def test_tampered_binary_or_provenance_fails(self):
        self.pack()
        wrong_fap=self.repack(lambda x:x.__setitem__(pkg.FAP_NAME,x[pkg.FAP_NAME]+b"wrong"))
        with self.assertRaisesRegex(ValueError,"hash/size"):
            pkg.verify(wrong_fap)
        wrong_revision=self.repack(lambda x:x.__setitem__(pkg.SOURCE_INFO,b"untrusted"))
        with self.assertRaisesRegex(ValueError,"hash/size"):
            pkg.verify(wrong_revision)

    def test_unknown_or_missing_member_and_symlink_rejected(self):
        self.pack()
        extra=self.repack(lambda x:x.__setitem__("unreviewed.bin",b"flash me"))
        with self.assertRaisesRegex(ValueError,"member count"):
            pkg.verify(extra)
        missing=self.repack(lambda x:x.pop(pkg.LICENSE_NAME))
        with self.assertRaisesRegex(ValueError,"member count"):
            pkg.verify(missing)
        altered=self.root/"linked.tar.gz"
        with tarfile.open(self.output,"r:gz") as original:
            entries=[(m.name,original.extractfile(m).read()) for m in original.getmembers()]
        with tarfile.open(altered,"w:gz") as tar:
            for name,blob in entries:
                member=tarfile.TarInfo(name)
                if name==pkg.FAP_NAME:
                    member.type=tarfile.SYMTYPE
                    member.linkname="../../bad"
                    member.size=0
                    tar.addfile(member)
                else:
                    member.size=len(blob)
                    tar.addfile(member,io.BytesIO(blob))
        with self.assertRaisesRegex(ValueError,"unsafe"):
            pkg.verify(altered)

if __name__=="__main__":unittest.main()
