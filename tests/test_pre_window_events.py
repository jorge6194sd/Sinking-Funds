"""
If we skipped a month run, events between the last snapshot and window start
should adjust the opening balance.
"""

from datetime import date
from pathlib import Path

from sinking_funds.events import Event, EventType, add_event
from sinking_funds.persistence import Snapshot, save_snapshot
from sinking_funds.simulation import sinking_funds_simulation


def test_pre_window_event_applied(tmp_path: Path):
    snap = tmp_path / "snap.jsonl"
    evs = tmp_path / "events.jsonl"

    # April snapshot: 100
    save_snapshot([Snapshot(2025, 4, "Jar", 100.0)], snap)

    # Withdrawal dated May 10 (we will simulate starting June)
    add_event(
        Event(date=date(2025, 5, 10), category="Jar", amount=-20.0, type=EventType.WITHDRAW),
        evs,
    )

    cats = [{"name": "Jar", "balance": 0.0, "monthly_contribution": 0.0, "apr": 0}]

    june = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=6,
        num_months=1,
        resume=True,
        use_events=True,
        snapshot_path=snap,
        event_path=evs,
        verbose=False,
    )[0]["categories"][0]["balance"]

    # Opening should be 80 (100 – 20), no deposits
    assert june == 80.0
