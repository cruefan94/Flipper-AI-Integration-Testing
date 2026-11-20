import unittest
from tools.check_android_signing_metadata import validate

class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.old = {"package":"com.example.satellite","versionCode":10,"signerSha256":"a"*64}
        self.new = {**self.old,"versionCode":11}
    def test_valid(self): self.assertTrue(validate(self.old,self.new))
    def test_signer(self):
        with self.assertRaises(ValueError): validate(self.old,{**self.new,"signerSha256":"b"*64})
    def test_version(self):
        with self.assertRaises(ValueError): validate(self.old,self.old)
    def test_package(self):
        with self.assertRaises(ValueError): validate(self.old,{**self.new,"package":"com.example.other"})
    def test_malformed(self):
        with self.assertRaises(ValueError): validate(self.old,{**self.new,"signerSha256":"unknown"})
    def test_boolean_version(self):
        with self.assertRaises(ValueError): validate(self.old,{**self.new,"versionCode":True})

if __name__ == "__main__": unittest.main()
