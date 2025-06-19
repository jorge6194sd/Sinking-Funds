"""
sinking_funds package
Public API re‑exports.
"""

from .simulation import sinking_funds_simulation
from .persistence import Snapshot, save_snapshot, load_snapshots

__all__ = [
    "sinking_funds_simulation",
    "Snapshot",
    "save_snapshot",
    "load_snapshots",
]
