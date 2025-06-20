import json
from pathlib import Path

from sinking_funds.persistence import Snapshot, save_snapshot
from sinking_funds.simulation import sinking_funds_simulation


def test_auto_resume(tmp_path: Path):
    """
    Given last month's snapshot, balances should carry forward when
    user passes zero or missing balance.
    """
    snap = tmp_path / "snap.jsonl"

    # Last month's closing balances
    rows = [
        Snapshot(year=2026, month=6, category="Tools",   balance=20.0),
        Snapshot(year=2026, month=6, category="Clothes", balance=20.0),
    ]
    save_snapshot(rows, snap)

    # User provides only metadata & zero balances
    cats = [
        {"name": "Tools",   "balance": 0.0, "monthly_contribution": 20, "apr": 0},
        {"name": "Clothes", "balance": 0.0, "monthly_contribution": 20, "apr": 0},
    ]

    out = sinking_funds_simulation(
        categories=cats,
        start_year=2026,
        start_month=7,
        num_months=1,
        resume=True,
        snapshot_path=snap,
        verbose=False,
    )[0]["categories"]

    # Check that opening 20 + deposit 20 = 40 closing
    for cat in out:
        assert cat["balance"] == 40.0
