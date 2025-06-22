"""
Ensure month arithmetic never repeats the same calendar month.
"""

from sinking_funds.simulation import sinking_funds_simulation


def test_month_progression_unique():
    cats = [{"name": "Jar", "balance": 0.0, "monthly_contribution": 0.0, "apr": 0}]
    out = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=1,
        num_months=13,              # span more than a year
        monthly_interest=False,
        verbose=False,
        resume=False,
    )

    months = [(m["year"], m["month_num"]) for m in out]
    assert len(months) == len(set(months)), "Month duplication detected"
    assert months[0] == (2025, 1)
    assert months[-1] == (2026, 1)
