"""
sinking_funds/persistence.py
------------------------------------------------------
Lightweight, append‑only storage for month‑end snapshots.

* Each snapshot row is written as one JSON object per line (JSON‑Lines).
* Default path: data/snapshots.jsonl  (folder created on first use).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

SNAPSHOT_DIR = Path("data")
SNAPSHOT_FILE = SNAPSHOT_DIR / "snapshots.jsonl"


@dataclass
class Snapshot:
    year: int
    month: int
    category: str
    balance: float


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_snapshot(rows: List[Snapshot], file_path: Path | None = None) -> None:
    """
    Append a list of Snapshot rows to disk (JSON‑Lines).
    """
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    _ensure_parent(fp)
    with fp.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row)) + "\n")


def load_snapshots(file_path: Path | None = None) -> List[Snapshot]:
    """
    Load all snapshots; returns [] if file is missing.
    """
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Snapshot(**json.loads(line)) for line in f]
