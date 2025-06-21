"""
Command‑line helper to record a mid‑month event quickly.

Usage examples
--------------
# unexpected withdrawal
python sinking_funds/cli_add_event.py --cat Tools --amount -180 --date 2026-06-12 --note "Drill press"

# skip July Travel deposit (adjustment)
python sinking_funds/cli_add_event.py --cat Travel --amount -60 --date 2026-07-01 --type adjust
"""

import argparse
from datetime import date

from sinking_funds.events import Event, EventType, add_event


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Add a mid‑month sinking‑fund event")
    p.add_argument("--cat", required=True, help="Category name (case‑sensitive)")
    p.add_argument("--amount", required=True, type=float, help="+ or − dollar amount")
    p.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="YYYY‑MM‑DD (default: today)",
    )
    p.add_argument(
        "--type",
        choices=[e.value for e in EventType],
        default="deposit",
        help="deposit | withdraw | adjust | correction",
    )
    p.add_argument("--note", help="Optional memo")
    return p


def main() -> None:
    args = _build_parser().parse_args()
    ev = Event(
        date=date.fromisoformat(args.date),
        category=args.cat,
        amount=args.amount,
        type=EventType(args.type),
        note=args.note,
    )
    add_event(ev)
    print("Event logged:", ev)


if __name__ == "__main__":
    main()
