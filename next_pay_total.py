"""
next_pay_total.py
────────────────────────────────────────────────────────────────────
1. Calculates the lump‑sum you should transfer from checking to your
   savings account on the next payday.
2. Shows your *current* grand total across all sinking‑fund buckets
   (based on the latest snapshot) and what the new total will be
   **after** this deposit.
3. Optionally writes one Event row per category so you don’t have to
   call the CLI seven times.

Run:
    python next_pay_total.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict

from sinking_funds.events import Event, add_event
from sinking_funds.persistence import latest_balances

# ────────────────── 1. CONFIGURE YOUR BI‑WEEKLY PLAN ────────────────── #
DEPOSITS: Dict[str, float] = {
    "Clothes": 10,
    "Condo fund": 50,
    "Savings": 150,
    "Health": 20,
    "Tools": 20,
    "Business": 60,
    "Car maintenance": 0,
    # add/remove categories as needed
}

# Next payday
PAYDATE = date(2025, 6, 27)  # <–– change each time you run

# Path to the snapshot ledger (keep default unless you moved the file)
SNAPSHOT_FILE = Path("data/snapshots.jsonl")
# ─────────────────────────────────────────────────────────────────────── #


def main() -> None:
    # --- 2. calculate lump‑sum to move ---------------------------------
    lump_sum = sum(DEPOSITS.values())
    print(f"\n➡️  Transfer  ${lump_sum:.2f}  from checking to savings on {PAYDATE}.")

    # --- 3. show current vs projected grand total ----------------------
    current_total = sum(latest_balances(SNAPSHOT_FILE).values()) if SNAPSHOT_FILE.exists() else 0.0
    projected_total = current_total + lump_sum
    print(f"   Current sinking‑fund total:  ${current_total:.2f}")
    print(f"   Projected total after pay:  ${projected_total:.2f}\n")

    # --- 4. ask user whether to log events -----------------------------
    choice = input("Log these deposits as Events now? [y/N] ").strip().lower()
    if choice == "y":
        for cat, amt in DEPOSITS.items():
            if amt:               # skip zero‑amount categories
                add_event(
                    Event(
                        date=PAYDATE,
                        category=cat,
                        amount=amt,
                        note="Bi‑weekly paycheck deposit",
                    )
                )
        print("✅  Events written to data/events.jsonl")
    else:
        print("ℹ️  No events logged; you can run this script again later.")

    print("Done.")


if __name__ == "__main__":
    main()
