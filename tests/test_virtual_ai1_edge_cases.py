"""Additional AI1 virtual-session regression tests.

Host-only checks; these do not emulate Bluetooth radio or Flipper hardware.
"""
import unittest
from virtual_ai1_session import VirtualAi1Session


class VirtualSessionEdgeCases(unittest.TestCase):
    def test_reconnect_clears_pending_request(self):
        session = VirtualAi1Session()
        session.connect(True)
        session.request(42, "battery")
        old_generation = session.generation
        session.disconnect()
        session.connect(True)
        self.assertIsNone(session.pending)
        with self.assertRaises(PermissionError):
            session.response(b"AI1|ANSWER|42|stale\n", old_generation)
        self.assertEqual(session.request(43, "status"), b"AI1|ASK|43|status\n")

    def test_rejected_response_does_not_consume_pending_request(self):
        session = VirtualAi1Session()
        session.connect(True)
        session.request(7, "status")
        for frame in (
            b"AI1|ANSWER|8|wrong\n",
            b"AI1|ANSWER|7|line\rbreak\n",
            b"AI1|ANSWER|7|nul\x00byte\n",
            b"AI1|ANSWER|7|del\x7fbyte\n",
            b"AI1|ANSWER|7|bad\nnewline\n",
            b"AI1|ANSWER|4294967296|overflow\n",
            b"AI1|ANSWER|+7|sign\n",
            b"AI1|ANSWER|-7|negative\n",
        ):
            with self.subTest(frame=frame):
                with self.assertRaises(ValueError):
                    session.response(frame, session.generation)
                self.assertEqual(session.pending, 7)
        self.assertEqual(session.response(b"AI1|ANSWER|7|ok\n", session.generation), "ok")

    def test_disconnected_session_cannot_accept_response(self):
        session = VirtualAi1Session()
        session.connect(True)
        session.request(3, "status")
        generation = session.generation
        session.disconnect()
        with self.assertRaises(PermissionError):
            session.response(b"AI1|ANSWER|3|ok\n", generation)

    def test_untrusted_reconnection_blocks_requests(self):
        session = VirtualAi1Session()
        session.connect(True)
        session.request(4, "status")
        session.disconnect()
        session.connect(False)
        with self.assertRaises(PermissionError):
            session.request(5, "status")

    def test_maximum_valid_request_id_roundtrip(self):
        session = VirtualAi1Session()
        session.connect(True)
        session.request(0xffffffff, "status")
        self.assertEqual(
            session.response(b"AI1|ANSWER|4294967295|ok\n", session.generation),
            "ok",
        )


if __name__ == "__main__":
    unittest.main()
