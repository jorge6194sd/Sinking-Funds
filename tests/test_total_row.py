"""
Validate that simulation writes a '__TOTAL__' snapshot row and that
latest_balances() ignores it.
"""

from pathlib import Path
from sinking_funds.persistence import latest_balances, load_snapshots
from sinking_funds.simulation import sinking_funds_simulation


def test_total_row_written_and_ignored(tmp_path: Path):
    snap = tmp_path / "snap.jsonl"

    cats = [{"name": "Jar", "balance": 100.0, "monthly_contribution": 0.0, "apr": 0}]
    sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=1,
        num_months=1,
        resume=False,
        snapshot_path=snap,
        verbose=False,
    )

    # snapshot file should contain one real row + 1 total row
    rows = load_snapshots(snap)
    assert any(r.category == "__TOTAL__" for r in rows)
    assert any(r.category == "Jar" for r in rows)

    # latest_balances should NOT include __TOTAL__
    lbs = latest_balances(snap)
    assert "Jar" in lbs
    assert "__TOTAL__" not in lbs
