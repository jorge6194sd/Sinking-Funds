#!/usr/bin/env python3
"""
next_pay_total.py
-------------------------------------------------------------------
Show how much cash to move from checking to savings for upcoming
recurring deposits.

Reads:   data/recurring.yaml
Writes:  nothing
Usage:
    python next_pay_total.py          # look ahead 14 days (default)
    python next_pay_total.py 7        # look ahead 7 days
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

import yaml

RULES_FILE = Path("data/recurring.yaml")
DEFAULT_WINDOW = 14  # days


def load_rules(fp: Path) -> List[Dict]:
    if not fp.exists():
        return []
    return yaml.safe_load(fp.read_text()) or []


def upcoming_totals(rules: List[Dict], *, window_days: int) -> Dict[date, float]:
    today = date.today()
    horizon = today + timedelta(days=window_days)
    totals: Dict[date, float] = {}

    for rule in rules:
        due = date.fromisoformat(rule["next_due"])
        if today <= due <= horizon:
            totals.setdefault(due, 0.0)
            totals[due] += rule["amount"]

    return totals


if __name__ == "__main__":
    try:
        window = int(sys.argv[1])
    except (IndexError, ValueError):
        window = DEFAULT_WINDOW

    rules = load_rules(RULES_FILE)
    schedule = upcoming_totals(rules, window_days=window)

    if not schedule:
        print(f"No deposits due in the next {window} days.")
        sys.exit(0)

    for paydate, total in sorted(schedule.items()):
        print(f"Send ${total:.2f} from checking to savings on {paydate.isoformat()}.")

    if len(schedule) > 1:
        grand = sum(schedule.values())
        print(f"\nTotal for the next {window} days: ${grand:.2f}")
