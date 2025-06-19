from pathlib import Path

from sinking_funds.persistence import Snapshot, save_snapshot, load_snapshots


def test_save_and_load_roundtrip(tmp_path):
    file_ = tmp_path / "snap.jsonl"
    rows = [
        Snapshot(year=2025, month=6, category="Tools", balance=48.0),
        Snapshot(year=2025, month=6, category="Savings", balance=300.0),
    ]
    save_snapshot(rows, file_)
    loaded = load_snapshots(file_)
    assert loaded == rows
