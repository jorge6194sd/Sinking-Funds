"""
sinking_funds/persistence.py
--------------------------------------------------------------------
Snapshot ledger I/O utilities.

*   Uses LEDGER_ROOT / "snapshots.jsonl" as the default file.
*   LEDGER_ROOT is read from the environment variable SNAP_DIR;
    if SNAP_DIR is unset, it falls back to "data".
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

# ─────────────────────────  directory selection  ────────────────────────── #
LEDGER_ROOT = Path(os.getenv("SNAP_DIR", "data"))
LEDGER_ROOT.mkdir(parents=True, exist_ok=True)

SNAPSHOT_FILE = LEDGER_ROOT / "snapshots.jsonl"
# ─────────────────────────────────────────────────────────────────────────── #


# ========================================================================== #
#                                Data model
# ========================================================================== #
@dataclass
class Snapshot:
    year: int
    month: int            # 1‑12
    category: str
    balance: float


# ========================================================================== #
#                              File operations
# ========================================================================== #
def save_snapshot(rows: List[Snapshot], file_path: str | Path | None = None) -> None:
    """Append one or more Snapshot rows to the ledger (JSON‑Lines)."""
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    fp.parent.mkdir(parents=True, exist_ok=True)

    with fp.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row)) + "\n")


def load_snapshots(file_path: str | Path | None = None) -> List[Snapshot]:
    """Return every Snapshot row in chronological order."""
    fp = Path(file_path) if file_path else SNAPSHOT_FILE
    if not fp.exists():
        return []

    with fp.open(encoding="utf-8") as f:
        return [Snapshot(**json.loads(line)) for line in f]


def latest_balances(file_path: str | Path | None = None) -> Dict[str, float]:
    """
    For each category, return the balance from the most recent snapshot row.
    """
    latest: Dict[str, Snapshot] = {}
    for row in load_snapshots(file_path):
        latest[row.category] = row
    return {cat: snap.balance for cat, snap in latest.items()}
