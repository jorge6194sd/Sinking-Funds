# run_month.py  (place beside pyproject.toml)
from datetime import date
from sinking_funds.simulation import sinking_funds_simulation

cats = [
    {"name": "Tools", "balance": 0, "monthly_contribution": 40, "apr": 0},
    {"name": "Travel", "balance": 0, "monthly_contribution": 60, "apr": 0},
]

today = date.today()
sinking_funds_simulation(
    categories=cats,
    start_year=today.year,
    start_month=today.month,
    num_months=1,
    snapshot_path="data/snapshots.jsonl",   # <- forces single file
    verbose=False,
)
print("Month recorded    data/snapshots.jsonl")
