"""Virtual transport tests: synthetic AI1 frames only."""
import unittest
from virtual_ai1_session import VirtualAi1Session

class VirtualSessionTests(unittest.TestCase):
    def test_roundtrip(self):
        s=VirtualAi1Session(); s.connect(True)
        self.assertEqual(s.request(9,"battery"),b"AI1|ASK|9|battery\n")
        self.assertEqual(s.response(b"AI1|ANSWER|9|normal\n",s.generation),"normal")
        self.assertIsNone(s.pending)

    def test_reject_untrusted(self):
        s=VirtualAi1Session(); s.connect(False)
        with self.assertRaises(PermissionError): s.request(1,"test")

    def test_disconnect_invalidates_response(self):
        s=VirtualAi1Session(); s.connect(True)
        s.request(7,"test"); epoch=s.generation
        s.disconnect(); s.connect(True)
        with self.assertRaises(PermissionError):
            s.response(b"AI1|ANSWER|7|old\n",epoch)

    def test_replay_and_mismatch(self):
        s=VirtualAi1Session(); s.connect(True); s.request(5,"test")
        with self.assertRaises(ValueError): s.response(b"AI1|ANSWER|6|wrong\n",s.generation)
        s.response(b"AI1|ANSWER|5|ok\n",s.generation)
        with self.assertRaises(ValueError): s.response(b"AI1|ANSWER|5|replay\n",s.generation)

    def test_busy(self):
        s=VirtualAi1Session(); s.connect(True); s.request(1,"one")
        with self.assertRaises(RuntimeError): s.request(2,"two")

    def test_malformed_frames(self):
        s=VirtualAi1Session(); s.connect(True); s.request(1,"x")
        for frame in [b"AI1|ANSWER|1|bad",b"AI1|ANSWER|1|bad\nline\n",b"AI1|ANSWER|01x|bad\n",b"AI1|ANSWER|1|"+b"x"*180+b"\n",b"AI1|ANSWER|1|\xff\n"]:
            with self.subTest(frame=frame):
                with self.assertRaises(ValueError): s.response(frame,s.generation)
        self.assertEqual(s.pending,1)

if __name__=="__main__": unittest.main()
