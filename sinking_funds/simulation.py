"""
sinking_funds/simulation.py
--------------------------------------------------------------------
Core engine with Event processing (Epic 4) — all tests green.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List

from .events import Event, EventType, events_between, load_events
from .persistence import Snapshot, latest_balances, save_snapshot


# --------------------------------------------------------------------------- #
def _first_of_next_month(d: date) -> date:
    return date(d.year + (d.month // 12), (d.month % 12) + 1, 1)


# --------------------------------------------------------------------------- #
def sinking_funds_simulation(  # noqa: C901
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
    use_events: bool = True,
    snapshot_path: str | Path | None = None,
    event_path: str | Path | None = None,
):
    """Simulate sinking‑fund balances month‑by‑month."""

    # ------------------------------ defensive defaults ----------------------
    lumpsums = lumpsums or {}
    payment_adjustments = payment_adjustments or {}
    future_contribution_changes = future_contribution_changes or {}

    cats = [dict(c) for c in categories]
    cat_index = {c["name"]: c for c in cats}

    # ------------------------------ opening balances ------------------------
    if resume and snapshot_path:
        bal: Dict[str, float] = latest_balances(snapshot_path)
    else:
        bal = {}
    for c in cats:
        bal.setdefault(c["name"], c.get("balance", 0.0))

    # ------------------------------ load events -----------------------------
    all_events: List[Event] = (
        load_events(event_path) if use_events and event_path else []
    )

    window_start = date(start_year, start_month, 1)
    if use_events:
        for ev in all_events:
            if ev.date < window_start:
                bal.setdefault(ev.category, 0.0)
                bal[ev.category] += ev.amount

    month_summaries: List[Dict[str, Any]] = []

    # =======================================================================
    #                               MONTH LOOP
    # =======================================================================
    for m_idx in range(num_months):
        month_num = (start_month - 1 + m_idx) % 12 + 1
        year_num = start_year + (start_month - 1 + m_idx) // 12
        month_start = date(year_num, month_num, 1)
        month_end = _first_of_next_month(month_start)

        markers: Dict[str, List[str]] = {n: [] for n in cat_index}

        # ---------- permanent contribution changes BEFORE deposits ----------
        for name, info in cat_index.items():
            if name in future_contribution_changes and (
                (month_start.year, month_start.month)
                in future_contribution_changes[name]
            ):
                old = info["monthly_contribution"]
                new = future_contribution_changes[name][
                    (month_start.year, month_start.month)
                ]
                info["monthly_contribution"] = new
                diff = new - old
                # **changed line → legacy wording**
                markers[name].append(
                    f"*** Monthly contribution {'increased' if diff>0 else 'decreased'} "
                    f"by ${abs(diff):.2f} ***"
                )

        # -------------------------- apply interest --------------------------
        if monthly_interest:
            for name, info in cat_index.items():
                if info["apr"] > 0 and bal.get(name, 0.0) > 0:
                    bal[name] += bal[name] * (info["apr"] / 12)

        # ------------------- deposits and payment adjustments ---------------
        deposited: Dict[str, float] = {}
        for name, info in cat_index.items():
            base = info["monthly_contribution"]
            adj = payment_adjustments.get(name, {}).get(
                (month_start.year, month_start.month), 0.0
            )
            deposited[name] = max(base + adj, 0.0)
            bal[name] += deposited[name]

            if adj != 0:
                markers[name].append(
                    f"*** Payment {'increased' if adj>0 else 'decreased'} "
                    f"by ${abs(adj):.2f} ***"
                )

        # -------------------------- month events ----------------------------
        in_month_events = events_between(all_events, month_start, month_end)
        for ev in in_month_events:
            bal.setdefault(ev.category, 0.0)
            bal[ev.category] += ev.amount
            markers[ev.category].append(
                f"*** {ev.type.value.upper()} {ev.amount:+.2f}"
                f" on {ev.date.strftime('%m-%d')}"
                + (f" ({ev.note})" if ev.note else "")
                + " ***"
            )

        # ------------------------------ lumpsums ----------------------------
        for name in cat_index:
            lump = lumpsums.get(name, {}).get(
                (month_start.year, month_start.month), 0.0
            )
            if lump:
                bal[name] += lump
                markers[name].append(f"*** LUMP SUM +{lump:.2f} ***")

        # --------------------- summary row & snapshot -----------------------
        month_row = {
            "year": month_start.year,
            "month_num": month_start.month,
            "categories": [],
        }
        snap_rows: List[Snapshot] = []

        for name, info in cat_index.items():
            bal[name] = round(bal[name], 2)

            payment_marker = next(
                (m for m in markers[name] if m.startswith("*** Payment")), ""
            )
            lumpsum_marker = next(
                (m for m in markers[name] if m.startswith("*** LUMP SUM")), ""
            )
            contrib_marker = next(
                (m for m in markers[name] if m.startswith("*** Monthly contribution")), ""
            )

            month_row["categories"].append(
                {
                    "name": name,
                    "apr": info["apr"],
                    "balance": bal[name],
                    "amount_deposited": round(deposited.get(name, 0.0), 2),
                    "payment_change_marker": payment_marker,
                    "lumpsum_marker": lumpsum_marker,
                    "contribution_change_marker": contrib_marker,
                    "markers": " ".join(markers[name]),
                }
            )
            snap_rows.append(
                Snapshot(month_start.year, month_start.month, name, bal[name])
            )

        save_snapshot(snap_rows, snapshot_path)
        month_summaries.append(month_row)

    # ------------------------- optional console output ---------------------
    if verbose:
        for m in month_summaries:
            print(f"\n{m['year']}-{m['month_num']:02d}")
            print("-" * 50)
            for c in m["categories"]:
                print(
                    f"{c['name']:<15} Bal: ${c['balance']:<8}"
                    + ("  " + c["markers"] if c["markers"] else "")
                )

    return month_summaries
