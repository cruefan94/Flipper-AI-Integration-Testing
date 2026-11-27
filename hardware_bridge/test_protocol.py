"""Offline public contract tests; run: python -m unittest discover -s hardware_bridge -p 'test_*.py'"""
import copy
import json
import unittest

try:
    from hardware_bridge import protocol as p
except ModuleNotFoundError:
    import protocol as p


def sample():
    return {
        "version": 1, "kind": "request", "request_id": "demo-001",
        "source": "android", "target": "pi",
        "action": "device.status", "args": {}
    }


class ProtocolTests(unittest.TestCase):
    def test_roundtrip(self):
        original = sample()
        self.assertEqual(p.decode_stream_frame(p.encode_stream_frame(original)), original)

    def test_unicode_roundtrip(self):
        original = sample()
        original["args"] = {"label": "Température 🌡"}
        self.assertEqual(p.decode_envelope(p.encode_envelope(original)), original)

    def test_response(self):
        response = sample()
        response.update(kind="response", source="pi", target="android",
                        status="ok", args={"online": True})
        self.assertEqual(p.decode_envelope(p.encode_envelope(response)), response)

    def test_missing_required_and_extra_field(self):
        msg = sample()
        del msg["action"]
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)
        msg = sample()
        msg["command"] = "rm"
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)

    def test_forbid_raw_shell_script(self):
        msg = sample()
        msg.update(action="script.request", target="termux")
        for args in ({"command": "pwd"}, {"script_id": "../passwd"},
                     {"script_id": "device_diagnostics", "command": "pwd"}):
            msg["args"] = args
            with self.subTest(args=args), self.assertRaises(p.ProtocolError):
                p.encode_envelope(msg)

    def test_script_by_id_only(self):
        msg = sample()
        msg.update(action="script.request", target="termux",
                   args={"script_id": "device_diagnostics", "params": {}})
        self.assertEqual(p.decode_envelope(p.encode_envelope(msg)), msg)
        msg["target"] = "flipper"
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)

    def test_audio_trigger_by_manifest_id(self):
        msg = sample()
        msg.update(source="flipper", target="p4", action="audio.play",
                   args={"sound_id": "notification_1", "volume": 50})
        self.assertEqual(p.decode_stream_frame(p.encode_stream_frame(msg)), msg)
        for action in ("audio.stop", "audio.status"):
            msg.update(action=action, args={})
            self.assertEqual(p.decode_envelope(p.encode_envelope(msg)), msg)

    def test_audio_rejects_unsafe_inputs(self):
        msg = sample()
        msg.update(target="p4", action="audio.play")
        bad_args = (
            {}, {"path": "/sdcard/private.wav"},
            {"sound_id": "../secret"}, {"sound_id": "bad name"},
            {"sound_id": "beep", "path": "/tmp/beep.wav"},
            {"sound_id": "beep", "audio_base64": "AAA"},
            {"sound_id": "beep", "volume": True},
            {"sound_id": "beep", "volume": 1.5},
            {"sound_id": "beep", "volume": -1},
            {"sound_id": "beep", "volume": 101}
        )
        for args in bad_args:
            msg["args"] = args
            with self.subTest(args=args), self.assertRaises(p.ProtocolError):
                p.encode_envelope(msg)
        msg.update(args={"sound_id": "beep"}, target="android")
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)
        for action in ("audio.stop", "audio.status"):
            msg.update(target="p4", action=action, args={"sound_id": "beep"})
            with self.subTest(action=action), self.assertRaises(p.ProtocolError):
                p.encode_envelope(msg)

    def test_oversized_frame(self):
        msg = sample()
        msg["args"] = {"blob": "x" * 4090}
        with self.assertRaises(p.ProtocolError):
            p.encode_stream_frame(msg)

    def test_truncated_and_extra_stream_bytes(self):
        frame = p.encode_stream_frame(sample())
        for broken in (frame[:-1], frame + b"x", frame[:2], b"\x00\x00x"):
            with self.subTest(broken=broken[:12]), self.assertRaises(p.ProtocolError):
                p.decode_stream_frame(broken)

    def test_duplicate_json_key(self):
        msg = b'{"version":1,"version":1,"kind":"request"}'
        with self.assertRaises(p.ProtocolError):
            p.decode_envelope(msg)

    def test_invalid_utf8_and_non_finite(self):
        with self.assertRaises(p.ProtocolError):
            p.decode_envelope(b"\xff")
        msg = sample()
        msg["args"]["n"] = float("nan")
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)

    def test_invalid_identity_and_version(self):
        for field, value in (("source", "unknown"), ("target", "unknown"),
                             ("request_id", "bad request id"), ("version", 2)):
            msg = sample()
            msg[field] = value
            with self.subTest(field=field), self.assertRaises(p.ProtocolError):
                p.encode_envelope(msg)

    def test_deep_args(self):
        msg = sample()
        nested = {}
        node = nested
        for _ in range(7):
            node["level"] = {}
            node = node["level"]
        msg["args"] = nested
        with self.assertRaises(p.ProtocolError):
            p.encode_envelope(msg)


if __name__ == "__main__":
    unittest.main()
