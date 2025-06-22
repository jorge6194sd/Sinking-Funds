"""
Verify exact wording of the contribution‑change marker and its amount.
"""

from sinking_funds.simulation import sinking_funds_simulation


def test_contribution_marker_wording():
    cats = [
        {"name": "Jar", "balance": 0.0, "monthly_contribution": 40.0, "apr": 0},
    ]
    change = {"Jar": {(2025, 3): 100.0}}

    out = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=3,
        num_months=1,
        future_contribution_changes=change,
        monthly_interest=False,
        verbose=False,
    )[0]["categories"][0]

    assert out["amount_deposited"] == 100.0
    assert (
        out["contribution_change_marker"]
        == "*** Monthly contribution increased by $60.00 ***"
    )
