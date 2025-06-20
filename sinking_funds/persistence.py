"""
sinking_funds/persistence.py
------------------------------------------------------
Append‑only JSON‑Lines storage + helper utilities.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

SNAPSHOT_DIR = Path("data")
SNAPSHOT_FILE = SNAPSHOT_DIR / "snapshots.jsonl"


@dataclass
class Snapshot:
    year: int
    month: int
    category: str
    balance: float


# ---------------------------------------------------------------------------


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_snapshot(rows: List[Snapshot], file_path: Path | None = None) -> None:
    """Append Snapshot rows to <file> in JSON‑Lines format."""
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    _ensure_parent(fp)
    with fp.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row)) + "\n")


def load_snapshots(file_path: Path | None = None) -> List[Snapshot]:
    """Return every Snapshot in the ledger ([] if file absent)."""
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        return [Snapshot(**json.loads(line)) for line in f]


def latest_balances(file_path: Path | None = None) -> Dict[str, float]:
    """
    Return a dict {category → most‑recent balance} by streaming the JSONL
    once.  Last row wins because file is chronological.
    """
    balances: Dict[str, float] = {}
    for row in load_snapshots(file_path):
        balances[row.category] = row.balance
    return balances
