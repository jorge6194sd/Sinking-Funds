"""
sinking_funds/simulation.py
Core engine for sinking‑fund projections.
Now writes month‑end snapshots via persistence.save_snapshot().
"""

from pathlib import Path
from typing import List, Dict, Any

from .persistence import Snapshot, save_snapshot


def sinking_funds_simulation(
    categories: List[Dict[str, Any]],
    start_year: int = 2025,
    start_month: int = 1,
    lumpsums: Dict[str, Dict[tuple, float]] | None = None,
    payment_adjustments: Dict[str, Dict[tuple, float]] | None = None,
    future_contribution_changes: Dict[str, Dict[tuple, float]] | None = None,
    monthly_interest: bool = True,
    num_months: int = 12,
    verbose: bool = True,
    snapshot_path: str | Path | None = None,
):
    # ------------------------------------------------------------------ setup
    if lumpsums is None:
        lumpsums = {}
    if payment_adjustments is None:
        payment_adjustments = {}
    if future_contribution_changes is None:
        future_contribution_changes = {}

    # copy so caller's list is untouched
    categories = [dict(cat) for cat in categories]
    month_summaries = []

    # -------------------------------------------------------------- main loop
    for month_index in range(num_months):
        current_month_num = ((start_month - 1) + month_index) % 12 + 1
        year_shift = ((start_month - 1) + month_index) // 12
        current_year = start_year + year_shift

        # 1) monthly interest
        if monthly_interest:
            for cat in categories:
                if cat["apr"] > 0 and cat["balance"] > 0:
                    cat["balance"] += cat["balance"] * (cat["apr"] / 12.0)

        # 2) permanent contribution changes
        contribution_changes_this_month = {}
        for cat in categories:
            name = cat["name"]
            if name in future_contribution_changes and (
                current_year,
                current_month_num,
            ) in future_contribution_changes[name]:
                old = cat["monthly_contribution"]
                new = future_contribution_changes[name][
                    (current_year, current_month_num)
                ]
                cat["monthly_contribution"] = new
                contribution_changes_this_month[name] = (old, new)

        # 3) deposits + one‑off payment adjustments
        lumpsum_paid = {cat["name"]: 0.0 for cat in categories}
        this_month_dep = {}
        payment_adj_this_month = {}
        for cat in categories:
            name = cat["name"]
            base = cat["monthly_contribution"]
            adj = payment_adjustments.get(name, {}).get(
                (current_year, current_month_num), 0.0
            )
            deposit = max(base + adj, 0.0)
            cat["balance"] += deposit
            this_month_dep[name] = deposit
            payment_adj_this_month[name] = adj

        # 4) lumpsums
        for cat in categories:
            name = cat["name"]
            lump = lumpsums.get(name, {}).get(
                (current_year, current_month_num), 0.0
            )
            if lump > 0:
                cat["balance"] += lump
                lumpsum_paid[name] = lump

        # 5) build month summary (for return / printing)
        month_data = {
            "year": current_year,
            "month_num": current_month_num,
            "categories": [],
        }

        for cat in categories:
            name = cat["name"]
            adj = payment_adj_this_month[name]
            pay_marker = (
                f"*** Payment increased by ${adj:.2f} ***"
                if adj > 0
                else f"*** Payment decreased by ${abs(adj):.2f} ***"
                if adj < 0
                else ""
            )
            lump_marker = (
                f"*** LUMP SUM APPLIED: ${lumpsum_paid[name]:.2f} ***"
                if lumpsum_paid[name] > 0
                else ""
            )
            contrib_marker = ""
            if name in contribution_changes_this_month:
                old_c, new_c = contribution_changes_this_month[name]
                diff = new_c - old_c
                contrib_marker = (
                    f"*** Monthly contribution increased by ${diff:.2f} ***"
                    if diff > 0
                    else f"*** Monthly contribution decreased by ${abs(diff):.2f} ***"
                    if diff < 0
                    else ""
                )

            month_data["categories"].append(
                {
                    "name": name,
                    "apr": cat["apr"],
                    "balance": round(cat["balance"], 2),
                    "amount_deposited": round(this_month_dep[name], 2),
                    "payment_change_marker": pay_marker,
                    "lumpsum_marker": lump_marker,
                    "contribution_change_marker": contrib_marker,
                }
            )

        # ---- NEW: persist snapshots ------------------------------------
        snap_rows = [
            Snapshot(
                year=current_year,
                month=current_month_num,
                category=c["name"],
                balance=c["balance"],
            )
            for c in month_data["categories"]
        ]
        save_snapshot(snap_rows, Path(snapshot_path) if snapshot_path else None)

        month_summaries.append(month_data)

    # ---------------------------------------------------------------- print
    if verbose:
        print("\nSINKING FUNDS SCHEDULE\n" + "=" * 60)
        for m in month_summaries:
            print(f"\n{m['year']}-{m['month_num']:02d}")
            for cat in m["categories"]:
                print(
                    f"  {cat['name']:<18}"
                    f"Bal: ${cat['balance']:<10}"
                    + (
                        f" {cat['payment_change_marker']}"
                        if cat["payment_change_marker"]
                        else ""
                    )
                    + (f" {cat['lumpsum_marker']}" if cat["lumpsum_marker"] else "")
                    + (
                        f" {cat['contribution_change_marker']}"
                        if cat["contribution_change_marker"]
                        else ""
                    )
                )
        print("\nSimulation complete.\n")

    return month_summaries
