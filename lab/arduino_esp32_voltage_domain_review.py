"""Offline, fail-closed voltage-domain review for proposed Arduino/ESP32 GPIO links.

This module does not access GPIO, USB, serial ports, or hardware.
All voltages are explicitly supplied from verified component documentation.
"""
from dataclasses import dataclass
from math import isfinite
import unittest


@dataclass(frozen=True)
class Link:
    source: str
    sink: str
    source_high_max_v: float | None
    sink_absolute_max_v: float | None
    source_ground_verified: bool
    level_shifter_verified: bool = False
    shifter_output_max_v: float | None = None


def review(link: Link) -> tuple[bool, str]:
    """Return review eligibility only, never permission to connect or power hardware."""
    if not link.source or not link.sink or link.source == link.sink:
        return False, "invalid_endpoint"
    if not link.source_ground_verified:
        return False, "ground_unverified"
    for value in (link.source_high_max_v, link.sink_absolute_max_v):
        if value is None or not isinstance(value, (float, int)) or isinstance(value, bool) or not isfinite(value) or value <= 0:
            return False, "ratings_unverified"
    effective = link.source_high_max_v
    if link.level_shifter_verified:
        v = link.shifter_output_max_v
        if v is None or not isinstance(v, (float, int)) or isinstance(v, bool) or not isfinite(v) or v <= 0:
            return False, "shifter_rating_unverified"
        effective = v
    elif link.shifter_output_max_v is not None:
        return False, "shifter_not_verified"
    if effective > link.sink_absolute_max_v:
        return False, "overvoltage_risk"
    return True, "offline_review_only"


class VoltageDomainTests(unittest.TestCase):
    def test_5v_uno_to_3v3_esp32_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", 5.0, 3.3, True))[1], "overvoltage_risk")

    def test_verified_shifter_with_safe_output(self):
        self.assertEqual(review(Link("uno", "esp32", 5.0, 3.3, True, True, 3.3)), (True, "offline_review_only"))

    def test_shifter_claim_without_rating_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", 5.0, 3.3, True, True))[1], "shifter_rating_unverified")

    def test_unverified_shifter_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", 5.0, 3.3, True, False, 3.3))[1], "shifter_not_verified")

    def test_no_common_ground_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", 3.3, 3.3, False))[1], "ground_unverified")

    def test_missing_rating_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", None, 3.3, True))[1], "ratings_unverified")

    def test_nan_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", float("nan"), 3.3, True))[1], "ratings_unverified")

    def test_bool_rating_rejected(self):
        self.assertEqual(review(Link("uno", "esp32", True, 3.3, True))[1], "ratings_unverified")

    def test_same_endpoint_rejected(self):
        self.assertEqual(review(Link("uno", "uno", 3.3, 3.3, True))[1], "invalid_endpoint")

    def test_equal_voltage_is_review_only(self):
        self.assertEqual(review(Link("esp32", "sensor", 3.3, 3.3, True)), (True, "offline_review_only"))


if __name__ == "__main__":
    unittest.main()
