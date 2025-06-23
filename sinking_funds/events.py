"""
sinking_funds/events.py
------------------------------------------------------
Dataclass, helpers, and query utilities for Event ledger.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Iterable, List

# ---------- Event model ------------------------------------------------------

class EventType(str, Enum):
    DEPOSIT = "deposit"        # +amount
    WITHDRAW = "withdraw"      # -amount
    ADJUST = "adjust"          # ± amount that replaces/plugs planned deposit
    CORRECTION = "correction"  # retro fix


@dataclass
class Event:
    date: date
    category: str
    amount: float
    type: EventType = EventType.DEPOSIT
    note: str | None = None


# ---------- File locations ---------------------------------------------------

EVENT_DIR = Path("data")
EVENT_FILE = EVENT_DIR / "events.jsonl"


# ---------- I/O helpers ------------------------------------------------------

def _ensure_parent(fp: Path) -> None:
    fp.parent.mkdir(parents=True, exist_ok=True)


def add_event(event: Event, file_path: Path | str | None = None) -> None:
    """Append a single Event to JSON‑Lines ledger."""
    fp = Path(file_path) if file_path else EVENT_FILE
    _ensure_parent(fp)
    as_json = json.dumps(asdict(event), default=str)
    with fp.open("a", encoding="utf-8") as f:
        f.write(as_json + "\n")


def load_events(file_path: Path | str | None = None) -> List[Event]:
    """Return *all* recorded Events (chronological order)."""
    fp = Path(file_path) if file_path else EVENT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Event(**_parse_jsonl(line)) for line in f]


# ---------- Query helpers ----------------------------------------------------

def events_between(
    events: Iterable[Event],
    date_from: date,
    date_to: date,
) -> List[Event]:
    """Return events where  date_from ≤ ev.date < date_to ."""
    return [e for e in events if date_from <= e.date < date_to]


# ---------- internal ---------------------------------------------------------

def _parse_jsonl(line: str) -> dict:
    raw = json.loads(line)
    # convert date string back to datetime.date
    if isinstance(raw.get("date"), str):
        raw["date"] = datetime.fromisoformat(raw["date"]).date()
    raw["type"] = EventType(raw["type"])
    return raw
