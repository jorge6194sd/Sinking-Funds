"""
sinking_funds/simulation.py
Core engine + auto‑resume logic (Epic 2).
"""

from pathlib import Path
from typing import Any, Dict, List

from .persistence import Snapshot, latest_balances, save_snapshot


def sinking_funds_simulation(  # noqa: C901 (complexity)
    categories: List[Dict[str, Any]],
    start_year: int = 2025,
    start_month: int = 1,
    *,
    lumpsums: Dict[str, Dict[tuple, float]] | None = None,
    payment_adjustments: Dict[str, Dict[tuple, float]] | None = None,
    future_contribution_changes: Dict[str, Dict[tuple, float]] | None = None,
    monthly_interest: bool = True,
    num_months: int = 12,
    verbose: bool = True,
    resume: bool = True,
    snapshot_path: str | Path | None = None,
):
    """
    Simulate sinking‑fund balances.

    If `resume` is True (default) then any category whose incoming
    `balance` is *zero or omitted* is automatically populated with the
    latest closing balance found in the snapshot ledger.
    """

    # ------------------------ auto‑resume ---------------------------------
    if resume:
        last = latest_balances(snapshot_path)
        for cat in categories:
            if cat.get("balance") in (None, 0):
                if cat["name"] in last:
                    cat["balance"] = last[cat["name"]]

    # ------------------------ defensive defaults --------------------------
    lumpsums = lumpsums or {}
    payment_adjustments = payment_adjustments or {}
    future_contribution_changes = future_contribution_changes or {}

    # work on a copy so caller data remains untouched
    categories = [dict(cat) for cat in categories]
    month_summaries = []

    # ------------------------ month loop ----------------------------------
    for m_idx in range(num_months):
        month_num = ((start_month - 1) + m_idx) % 12 + 1
        year_shift = ((start_month - 1) + m_idx) // 12
        year = start_year + year_shift

        # 1) interest
        if monthly_interest:
            for cat in categories:
                if cat["apr"] > 0 and cat["balance"] > 0:
                    cat["balance"] += cat["balance"] * (cat["apr"] / 12)

        # 2) permanent contribution changes
        contrib_change_this_month = {}
        for cat in categories:
            name = cat["name"]
            if (name in future_contribution_changes and
                (year, month_num) in future_contribution_changes[name]):
                old = cat["monthly_contribution"]
                new = future_contribution_changes[name][(year, month_num)]
                cat["monthly_contribution"] = new
                contrib_change_this_month[name] = (old, new)

        # 3) deposits + ad‑hoc adjustments
        lump_paid = {c["name"]: 0.0 for c in categories}
        deposited = {}
        pay_adj_this_month = {}
        for cat in categories:
            name = cat["name"]
            base = cat["monthly_contribution"]
            adj = payment_adjustments.get(name, {}).get((year, month_num), 0.0)
            amt = max(base + adj, 0.0)
            cat["balance"] += amt
            deposited[name] = amt
            pay_adj_this_month[name] = adj

        # 4) lumpsums
        for cat in categories:
            name = cat["name"]
            lump = lumpsums.get(name, {}).get((year, month_num), 0.0)
            if lump:
                cat["balance"] += lump
                lump_paid[name] = lump

        # 5) build month summary
        month_data = {
            "year": year,
            "month_num": month_num,
            "categories": [],
        }

        for cat in categories:
            name = cat["name"]
            adj = pay_adj_this_month[name]
            pay_marker = (
                f"*** Payment {'increased' if adj>0 else 'decreased'} by ${abs(adj):.2f} ***"
                if adj else ""
            )
            lump_marker = (
                f"*** LUMP SUM APPLIED: ${lump_paid[name]:.2f} ***"
                if lump_paid[name] else ""
            )
            contrib_marker = ""
            if name in contrib_change_this_month:
                old, new = contrib_change_this_month[name]
                diff = new - old
                contrib_marker = (
                    f"*** Monthly contribution {'increased' if diff>0 else 'decreased'} by ${abs(diff):.2f} ***"
                )

            month_data["categories"].append(
                {
                    "name": name,
                    "apr": cat["apr"],
                    "balance": round(cat["balance"], 2),
                    "amount_deposited": round(deposited[name], 2),
                    "payment_change_marker": pay_marker,
                    "lumpsum_marker": lump_marker,
                    "contribution_change_marker": contrib_marker,
                }
            )

        # 6) persist snapshots
        snap_rows = [
            Snapshot(year=year, month=month_num, category=c["name"], balance=c["balance"])
            for c in month_data["categories"]
        ]
        save_snapshot(snap_rows, snapshot_path)

        month_summaries.append(month_data)

    # Optional screen output
    if verbose:
        for m in month_summaries:
            print(f'\n{m["year"]}-{m["month_num"]:02d}')
            for c in m["categories"]:
                print(f'  {c["name"]:<15} Bal: ${c["balance"]:<8} {c["lumpsum_marker"]}')

    return month_summaries
