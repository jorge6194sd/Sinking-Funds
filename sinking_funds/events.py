"""
sinking_funds/events.py
--------------------------------------------------------------------
Mid‑month Event ledger I/O and helpers.

*   Uses LEDGER_ROOT / "events.jsonl" as the default file.
*   LEDGER_ROOT is controlled by the same SNAP_DIR env var so tests can
    redirect both ledgers together.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Iterable, List

# ─────────────────────────  directory selection  ────────────────────────── #
LEDGER_ROOT = Path(os.getenv("SNAP_DIR", "data"))
LEDGER_ROOT.mkdir(parents=True, exist_ok=True)

EVENT_FILE = LEDGER_ROOT / "events.jsonl"
# ─────────────────────────────────────────────────────────────────────────── #


# ========================================================================== #
#                                 Data model
# ========================================================================== #
class EventType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    ADJUST = "adjust"
    CORRECTION = "correction"


@dataclass
class Event:
    date: date
    category: str
    amount: float
    type: EventType = EventType.DEPOSIT
    note: str | None = None


# ========================================================================== #
#                               File helpers
# ========================================================================== #
def _ensure_parent(fp: Path) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)


def add_event(event: Event, file_path: str | Path | None = None) -> None:
    """Append a single Event row to the JSON‑Lines ledger."""
    fp = Path(file_path) if file_path else EVENT_FILE
    _ensure_parent(fp)
    with fp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), default=str) + "\n")


def load_events(file_path: str | Path | None = None) -> List[Event]:
    """Return every Event row (chronological order)."""
    fp = Path(file_path) if file_path else EVENT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Event(**_parse_jsonl(line)) for line in f]


# ========================================================================== #
#                               Query helpers
# ========================================================================== #
def events_between(events: Iterable[Event], d_from: date, d_to: date) -> List[Event]:
    """Return events where  d_from ≤ event.date < d_to ."""
    return [ev for ev in events if d_from <= ev.date < d_to]


# -------------------------------------------------------------------------- #
#                                Internals
# -------------------------------------------------------------------------- #
def _parse_jsonl(line: str) -> dict:
    raw = json.loads(line)
    raw["date"] = datetime.fromisoformat(raw["date"]).date()
    raw["type"] = EventType(raw["type"])
    return raw
