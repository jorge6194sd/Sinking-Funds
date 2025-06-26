"""
sinking_funds/persistence.py
--------------------------------------------------------------------
Snapshot ledger I/O utilities.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

# ───────────────────  ledger location (honours SNAP_DIR) ────────────────── #
LEDGER_ROOT = Path(os.getenv("SNAP_DIR", "data"))
LEDGER_ROOT.mkdir(parents=True, exist_ok=True)
SNAPSHOT_FILE = LEDGER_ROOT / "snapshots.jsonl"
# ─────────────────────────────────────────────────────────────────────────── #


@dataclass
class Snapshot:
    year: int
    month: int
    category: str
    balance: float


# ------------------------------------------------------------------ writers #
def save_snapshot(rows: List[Snapshot], file_path: str | Path | None = None) -> None:
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    fp.parent.mkdir(parents=True, exist_ok=True)
    with fp.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row)) + "\n")


# ------------------------------------------------------------------- readers #
def load_snapshots(file_path: str | Path | None = None) -> List[Snapshot]:
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Snapshot(**json.loads(line)) for line in f]


def latest_balances(file_path: str | Path | None = None) -> Dict[str, float]:
    """
    Return the most recent balance per *real* category.
    Meta rows whose category starts with '__' are ignored.
    """
    latest: Dict[str, Snapshot] = {}
    for row in load_snapshots(file_path):
        if row.category.startswith("__"):
            continue
        latest[row.category] = row
    return {cat: snap.balance for cat, snap in latest.items()}
