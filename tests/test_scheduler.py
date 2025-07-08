from datetime import date
from pathlib import Path

import yaml

from sinking_funds.events import load_events
from sinking_funds.scheduler import run_scheduler

def test_rule_due_today(tmp_path: Path):
    rules = [
        {
            "category": "Savings",
            "amount": 150,
            "every": "14d",
            "next_due": "2025-07-12",
        }
    ]
    rules_fp = tmp_path / "recurring.yaml"
    rules_fp.write_text(yaml.safe_dump(rules))

    events_fp = tmp_path / "events.jsonl"

    written = run_scheduler(
        rules_path=rules_fp,
        event_path=events_fp,
        today=date(2025, 7, 12),
    )
    assert written == 1

    evs = load_events(events_fp)
    assert evs[0].category == "Savings"
    assert evs[0].amount == 150
    # next_due bumped by 14 days
    next_due = yaml.safe_load(rules_fp.read_text())[0]["next_due"]
    assert next_due == "2025-07-26"
