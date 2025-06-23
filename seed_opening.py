from sinking_funds.persistence import Snapshot, save_snapshot

rows = [
    Snapshot(2025, 6, "Clothes",        10.0),
    Snapshot(2025, 6, "Condo fund",     50.0),
    Snapshot(2025, 6, "Savings",       150.0),
    Snapshot(2025, 6, "Health",         0.0),
    Snapshot(2025, 6, "Tools",          20.0),
    Snapshot(2025, 6, "Supplements",    13.69),
    Snapshot(2025, 6, "Household Essentials",    25.0),
    Snapshot(2025, 6, "Business",       60.0),
    Snapshot(2025, 6, "Utilities",       20.0),
    Snapshot(2025, 6, "Car maintenance", 0.0),
    Snapshot(2025, 6, "Travel", 0.0),
    Snapshot(2025, 6, "Law School", 0.0),
]

save_snapshot(rows)        # writes data/snapshots.jsonl
print(" Opening snapshot for 2025/06/30 written.")
