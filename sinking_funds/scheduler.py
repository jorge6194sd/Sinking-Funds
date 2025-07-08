"""
sinking_funds/scheduler.py
────────────────────────────────────────────────────────────────────────────
Nightly task that reads `data/recurring.yaml`, appends due deposit Events,
then bumps each rule’s `next_due` forward.

Cadence strings supported:
• "14d"      → every 14 days
• "monthly"  → same calendar day next month
"""

from __future__ import annotations

import yaml
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

import pendulum

from .events import Event, EventType, add_event

# ── File locations ----------------------------------------------------------
LEDGER_ROOT = Path("data")
RULES_FILE = LEDGER_ROOT / "recurring.yaml"
DEFAULT_NOTE = "Auto‑scheduled"


# ── Helpers -----------------------------------------------------------------
def _parse(d: str) -> date:
    return date.fromisoformat(d)


def _next_due(current: date, cadence: str) -> date:
    """Return the next due date *after* `current`."""
    if cadence.endswith("d"):
        return current + timedelta(days=int(cadence[:-1]))
    if cadence == "monthly":
        return pendulum.instance(current).add(months=1).date()
    raise ValueError(f"Unsupported cadence {cadence!r}")


# ── Public API --------------------------------------------------------------
def run_scheduler(  # noqa: C901  (complexity is acceptable here)
    *,
    rules_path: Path | None = None,
    event_path: Path | None = None,
    today: date | None = None,
) -> int:
    """
    Evaluate recurring‑deposit rules that are *due today or earlier*.

    Writes Event rows and bumps each rule’s `next_due`.
    Returns the number of events written.
    """
    today = today or date.today()
    rules_fp = Path(rules_path) if rules_path else RULES_FILE
    events_fp = Path(event_path) if event_path else None

    # ---------------------------------------------------------------- rules
    rules: List[Dict] = []
    if rules_fp.exists():
        rules = yaml.safe_load(rules_fp.read_text()) or []

    events_to_write: List[Event] = []

    for rule in rules:
        due = _parse(rule["next_due"])
        cadence = rule["every"]

        # loop in case the job hasn’t run for multiple periods
        while due <= today:
            events_to_write.append(
                Event(
                    date=due,
                    category=rule["category"],
                    amount=rule["amount"],
                    type=EventType.DEPOSIT,
                    note=rule.get("note") or DEFAULT_NOTE,
                )
            )
            due = _next_due(due, cadence)

        rule["next_due"] = due.isoformat()  # persist bump

    # ---------------------------------------------------------------- write events
    for ev in events_to_write:
        add_event(ev, events_fp)

    # ---------------------------------------------------------------- save bumped rules
    rules_fp.parent.mkdir(parents=True, exist_ok=True)
    rules_fp.write_text(yaml.safe_dump(rules, sort_keys=False))

    return len(events_to_write)


# ── CLI entry‑point ---------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    count = run_scheduler()
    print(f" Scheduler finished — {count} event(s) written.")
