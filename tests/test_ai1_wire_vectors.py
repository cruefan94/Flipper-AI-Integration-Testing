"""Public-safe AI1 protocol compatibility vectors derived from source inspection."""
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/"contracts/ai_satellite_v1.json").read_text())

def encode(kind, request_id, payload):
    if not re.fullmatch(r"[A-Z_]{1,16}",kind):
        raise ValueError("type")
    if not isinstance(request_id,int) or isinstance(request_id,bool) or not 0<=request_id<=4294967295:
        raise ValueError("id")
    if not isinstance(payload,str) or any(ch in payload for ch in ("|","\r","\n","\x00")):
        raise ValueError("payload")
    data=f"AI1|{kind}|{request_id}|{payload}\n".encode("utf-8")
    if len(data)>180:
        raise ValueError("oversize")
    return data

def decode(data):
    if not isinstance(data,bytes) or len(data)<8 or len(data)>180 or not data.endswith(b"\n"):
        raise ValueError("frame")
    if b"\x00" in data or b"\r" in data:
        raise ValueError("control")
    try:
        s=data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError("utf8") from e
    fields=s[:-1].split("|")
    if len(fields)!=4 or fields[0]!="AI1" or not re.fullmatch(r"[A-Z_]{1,16}",fields[1]):
        raise ValueError("header")
    if not re.fullmatch(r"[0-9]{1,10}",fields[2]) or int(fields[2])>4294967295:
        raise ValueError("id")
    if "\n" in fields[3] or "\r" in fields[3]:
        raise ValueError("payload")
    return fields[1],int(fields[2]),fields[3]

class WireCompatibilityVectors(unittest.TestCase):
    def test_contract_framing(self):
        self.assertEqual(CONTRACT["wire_format"],r"AI1|TYPE|request_id|payload\n")
        self.assertEqual(CONTRACT["max_frame_bytes"],180)

    def test_valid_round_trips(self):
        for kind,ident,payload in [
            ("PING",0,""),("STATUS",4294967295,"ready"),("AI_REQUEST",27,"hello"),
            ("ANSWER",123,"UTF-8 café"),("A",1,"x")]:
            self.assertEqual(decode(encode(kind,ident,payload)),(kind,ident,payload))

    def test_rejects_bad_headers_and_framing(self):
        bad=[b"AI2|PING|1|hi\n",b"AI1|bad|1|hi\n",b"AI1|PING|-1|hi\n",
             b"AI1|PING|4294967296|hi\n",b"AI1|PING|1|a|b\n",
             b"AI1|PING|1|hi\r\n",b"AI1|PING|1|hi",b"AI1|PING|1|hi\nmore\n",
             b"AI1|PING|1|hi\x00\n"]
        for value in bad:
            with self.subTest(value=value),self.assertRaises(ValueError):
                decode(value)

    def test_byte_length_limit_not_character_limit(self):
        with self.assertRaises(ValueError):
            encode("ANSWER",1,"é"*90)
        self.assertEqual(len(encode("ANSWER",1,"x"*166)),180)

    def test_bad_outgoing_payloads(self):
        for value in ["a|b","a\nb","a\rb","a\x00b"]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                encode("ASK",1,value)

if __name__=="__main__":
    unittest.main()
