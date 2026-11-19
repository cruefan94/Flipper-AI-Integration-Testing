"""Offline, fail-closed backpack wiring proposal reviewer. NO hardware access.

This is a *documentation gate*, not electrical certification. Board header
numbering, current budgets, power source and schematics require manual review.
Run: python3 -m unittest discover -s lab/backpack_wiring -p 'test_*.py'
"""
from __future__ import annotations

ALLOWED = {"flipper_zero", "esp32_wroom", "esp32_s2", "arduino_uno", "raspberry_pi_4b"}
MAX_EDGES = 32


def review(edges):
    """Return sanitized findings; never print user-provided strings or pin labels."""
    if not isinstance(edges, list) or len(edges) > MAX_EDGES:
        return ["INVALID_EDGE_COLLECTION"]
    findings = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            findings.append((index, "INVALID_EDGE"))
            continue
        a, b = edge.get("from_board"), edge.get("to_board")
        if a not in ALLOWED or b not in ALLOWED or a == b:
            findings.append((index, "INVALID_BOARD_PAIR"))
            continue
        if edge.get("signal") not in ("uart", "i2c", "spi", "digital", "ground"):
            findings.append((index, "UNREVIEWED_SIGNAL"))
            continue
        if edge.get("signal") == "ground":
            if edge.get("direction") != "passive":
                findings.append((index, "GROUND_DIRECTION_INVALID"))
            continue
        if edge.get("direction") not in ("a_to_b", "b_to_a"):
            findings.append((index, "DIRECTION_UNVERIFIED"))
        if edge.get("source_voltage") not in (3.3, 5.0):
            findings.append((index, "SOURCE_VOLTAGE_UNVERIFIED"))
        elif edge["source_voltage"] == 5.0:
            # Never infer 5V tolerance from board name, even for Uno.
            findings.append((index, "FIVE_VOLT_SIGNAL_REQUIRES_ENGINEERING_REVIEW"))
        if edge.get("level_shift_verified") is not True:
            findings.append((index, "LEVEL_SHIFT_UNVERIFIED"))
        if edge.get("common_ground_verified") is not True:
            findings.append((index, "COMMON_GROUND_UNVERIFIED"))
        if edge.get("pinout_schematic_verified") is not True:
            findings.append((index, "PINOUT_UNVERIFIED"))
        if edge.get("power_budget_verified") is not True:
            findings.append((index, "POWER_BUDGET_UNVERIFIED"))
        # Deliberately refuse to approve any wiring from automated checks alone.
        findings.append((index, "PHYSICAL_WIRING_REQUIRES_MANUAL_APPROVAL"))
    return findings
