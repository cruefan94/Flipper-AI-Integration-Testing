"""Pure, bounded text view for offline Pi monitor snapshots.

No device I/O, hardware polling, terminal escape codes, or user-controlled labels.
"""
from pi_lab.monitor_dashboard import render_rows

def format_snapshot(observations: dict[str, tuple[str, int]]) -> str:
    """Render fixed four-line ASCII display; stale data never looks live."""
    rows = render_rows(observations)
    return "\n".join(
        f"{row.label}: {row.state if row.freshness == 'FRESH' else 'STALE'}"
        for row in rows
    )
