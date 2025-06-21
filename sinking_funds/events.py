"""
sinking_funds/events.py
------------------------------------------------------
Dataclass + helpers for mid‑month deposit / withdrawal events.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from pathlib import Path
from typing import List

# ---------- Event model ------------------------------------------------------

class EventType(str, Enum):
    DEPOSIT = "deposit"        # positive amount
    WITHDRAW = "withdraw"      # negative amount
    ADJUST = "adjust"          # ± amount that replaces or skips a planned deposit
    CORRECTION = "correction"  # retroactive balance fix


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
    """
    Append a single Event to the JSON‑Lines ledger.
    """
    fp = Path(file_path) if file_path else EVENT_FILE
    _ensure_parent(fp)
    with fp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(event), default=str) + "\n")


def load_events(file_path: Path | str | None = None) -> List[Event]:
    """
    Return every recorded Event (empty list if no file yet).
    """
    fp = Path(file_path) if file_path else EVENT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Event(**json.loads(line)) for line in f]
