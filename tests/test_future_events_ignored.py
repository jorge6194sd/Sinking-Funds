"""
Events dated *after* the simulated window must be ignored.
"""

from datetime import date
from pathlib import Path

from sinking_funds.events import Event, EventType, add_event
from sinking_funds.simulation import sinking_funds_simulation


def test_future_event_ignored(tmp_path: Path):
    evs = tmp_path / "events.jsonl"

    # Future‑dated top‑up: Sept 15
    add_event(
        Event(date=date(2025, 9, 15), category="Jar", amount=500, type=EventType.DEPOSIT),
        evs,
    )

    cats = [{"name": "Jar", "balance": 100.0, "monthly_contribution": 0.0, "apr": 0}]

    # Simulate August only
    aug_bal = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=8,
        num_months=1,
        resume=False,
        use_events=True,
        event_path=evs,
        verbose=False,
    )[0]["categories"][0]["balance"]

    # August should not include the Sept 15 deposit
    assert aug_bal == 100.0
