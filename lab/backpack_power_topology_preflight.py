"""Offline public-safe backpack wiring preflight. No hardware access."""
import unittest

def inspect(topology):
    issues = []
    devices = topology.get("devices", [])
    if not isinstance(devices, list) or not devices:
        return ["missing_devices"]
    names = [d.get("name") for d in devices if isinstance(d, dict)]
    if len(names) != len(devices) or len(names) != len(set(names)) or any(not n for n in names):
        issues.append("invalid_device_identity")
    for d in devices:
        if not isinstance(d, dict):
            continue
        if d.get("logic_v") not in (3.3, 5.0):
            issues.append("unknown_logic_voltage")
        if d.get("power_source") not in ("isolated_usb", "regulated_battery", "self_powered"):
            issues.append("unreviewed_power_source")
    for link in topology.get("links", []):
        if not isinstance(link, dict) or link.get("from") not in names or link.get("to") not in names:
            issues.append("unknown_link_endpoint")
            continue
        a = next(d for d in devices if isinstance(d, dict) and d.get("name") == link["from"])
        b = next(d for d in devices if isinstance(d, dict) and d.get("name") == link["to"])
        if link.get("kind") == "power":
            issues.append("direct_power_interconnect_requires_review")
        elif link.get("kind") == "signal":
            if not link.get("common_ground_verified"):
                issues.append("ground_not_verified")
            if a.get("logic_v") == 5.0 and b.get("logic_v") == 3.3 and not link.get("level_shift_verified"):
                issues.append("unsafe_5v_to_3v3")
            if link.get("driver") not in ("from", "to", "open_drain"):
                issues.append("signal_driver_unspecified")
        else:
            issues.append("unknown_link_kind")
    return sorted(set(issues))

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.devices = [dict(name="uno", logic_v=5.0, power_source="isolated_usb"),
                        dict(name="esp32", logic_v=3.3, power_source="isolated_usb")]
    def check(self, **kwargs):
        link = dict(kind="signal", **{"from":"uno", "to":"esp32"}, common_ground_verified=True,
                    driver="from", level_shift_verified=True)
        link.update(kwargs)
        return inspect(dict(devices=self.devices, links=[link]))
    def test_reviewed_signal(self): self.assertEqual(self.check(), [])
    def test_unsafe_voltage(self): self.assertIn("unsafe_5v_to_3v3", self.check(level_shift_verified=False))
    def test_missing_ground(self): self.assertIn("ground_not_verified", self.check(common_ground_verified=False))
    def test_power_link(self): self.assertIn("direct_power_interconnect_requires_review", self.check(kind="power"))
    def test_unknown_endpoint(self): self.assertIn("unknown_link_endpoint", self.check(to="unknown"))
    def test_driver_missing(self): self.assertIn("signal_driver_unspecified", self.check(driver=None))
    def test_missing_devices(self): self.assertIn("missing_devices", inspect({}))
    def test_duplicate_devices(self): self.assertIn("invalid_device_identity", inspect({"devices":self.devices*2}))
    def test_unknown_power(self):
        self.devices[0]["power_source"]="gpio"
        self.assertIn("unreviewed_power_source", self.check())
    def test_unknown_logic(self):
        self.devices[0]["logic_v"]=12
        self.assertIn("unknown_logic_voltage", self.check())

if __name__ == "__main__":
    unittest.main()
