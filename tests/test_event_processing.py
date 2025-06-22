from datetime import date
from pathlib import Path

from sinking_funds.events import Event, EventType, add_event
from sinking_funds.simulation import sinking_funds_simulation
from sinking_funds.persistence import Snapshot, save_snapshot


def test_withdraw_event_affects_balance(tmp_path: Path):
    snap = tmp_path / "snap.jsonl"
    evs = tmp_path / "events.jsonl"

    # Last snapshot (May)
    save_snapshot(
        [Snapshot(year=2026, month=5, category="Clothes", balance=100.0)], snap
    )

    # Mid‑June withdrawal
    add_event(
        Event(date=date(2026, 6, 12), category="Clothes", amount=-30, type=EventType.WITHDRAW, note="Jeans"),
        evs,
    )

    cats = [{"name": "Clothes", "balance": 0.0, "monthly_contribution": 20.0, "apr": 0}]
    june_row = sinking_funds_simulation(
        cats,
        start_year=2026,
        start_month=6,
        num_months=1,
        resume=True,
        use_events=True,
        snapshot_path=snap,
        event_path=evs,
        verbose=False,
    )[0]["categories"][0]

    # 100 opening -30 jeans +20 deposit = 90
    assert june_row["balance"] == 90.0
    assert "WITHDRAW -30.00 on 06-12" in june_row["markers"]
