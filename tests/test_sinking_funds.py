"""
tests/test_sinking_funds.py
Unit‑tests for sinking_funds_simulation.sinking_funds_simulation
Run with:  pytest
"""

import copy
from decimal import Decimal

import pytest

# Import the function under test
from sinking_funds import sinking_funds_simulation


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def base_categories():
    """Return a minimal copy of the categories list used in the example."""
    return [
        {
            "name": "TestFund",
            "balance": 100.00,
            "monthly_contribution": 0.00,
            "apr": 0.12,                   # 12 % annual nominal, for easy math
        }
    ]


# ---------------------------------------------------------------------------
# Core regression tests
# ---------------------------------------------------------------------------

def test_returns_requested_number_of_months(base_categories):
    months = 6
    result = sinking_funds_simulation(
        categories=copy.deepcopy(base_categories),
        start_year=2025,
        start_month=1,
        num_months=months,
        monthly_interest=False,
        verbose=False,
    )
    assert len(result) == months


def test_output_schema_stable(base_categories):
    """Top‑level keys & per‑category keys should stay the same."""
    result = sinking_funds_simulation(
        categories=copy.deepcopy(base_categories),
        start_year=2025,
        start_month=1,
        num_months=1,
        monthly_interest=False,
        verbose=False,
    )[0]  # first (and only) month

    # Top‑level keys
    assert {"year", "month_num", "categories"} <= result.keys()

    # Per‑category keys
    cat = result["categories"][0]
    expected_cat_keys = {
        "name",
        "apr",
        "balance",
        "amount_deposited",
        "payment_change_marker",
        "lumpsum_marker",
        "contribution_change_marker",
    }
    assert expected_cat_keys <= cat.keys()


def test_monthly_interest_application(base_categories):
    """
    Start balance = 100
    APR = 12 %
    Monthly interest = 1 % => 1.00
    No deposits, no withdrawals.
    Balance after one month should be 101.00
    """
    result = sinking_funds_simulation(
        categories=copy.deepcopy(base_categories),
        start_year=2025,
        start_month=1,
        num_months=1,
        monthly_interest=True,
        verbose=False,
    )[0]["categories"][0]["balance"]

    assert Decimal(str(result)) == Decimal("101.00")


def test_lumpsum_marker_and_balance_change(base_categories):
    lumpsums = {"TestFund": {(2025, 3): 250.0}}

    # Run three months (Jan, Feb, Mar) so the lump‑sum hits in month 3
    summaries = sinking_funds_simulation(
        categories=copy.deepcopy(base_categories),
        start_year=2025,
        start_month=1,
        lumpsums=lumpsums,
        num_months=3,
        monthly_interest=False,
        verbose=False,
    )

    jan_bal = summaries[0]["categories"][0]["balance"]
    mar_cat = summaries[2]["categories"][0]

    assert mar_cat["lumpsum_marker"]  # non‑empty
    assert mar_cat["balance"] == pytest.approx(jan_bal + 250.0)  # interest off


def test_negative_payment_adjustment_does_not_trigger_withdrawal(base_categories):
    """
    A negative adjustment larger than the monthly contribution should floor
    the deposit at zero (i.e., *not* create a withdrawal).
    """
    cats = copy.deepcopy(base_categories)
    cats[0]["monthly_contribution"] = 30.0

    payment_adjustments = {"TestFund": {(2025, 1): -100.0}}

    summary = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=1,
        payment_adjustments=payment_adjustments,
        num_months=1,
        monthly_interest=False,
        verbose=False,
    )[0]["categories"][0]

    assert summary["amount_deposited"] == 0.0
    assert summary["payment_change_marker"] == "*** Payment decreased by $100.00 ***"


def test_contribution_change_takes_effect_on_exact_month(base_categories):
    """
    Contribution should switch permanently starting the *effective* month.
    """
    cats = copy.deepcopy(base_categories)
    cats[0]["monthly_contribution"] = 50.0

    future_changes = {"TestFund": {(2025, 2): 150.0}}

    # Jan & Feb
    summaries = sinking_funds_simulation(
        categories=cats,
        start_year=2025,
        start_month=1,
        future_contribution_changes=future_changes,
        num_months=2,
        monthly_interest=False,
        verbose=False,
    )

    jan_dep = summaries[0]["categories"][0]["amount_deposited"]
    feb_dep = summaries[1]["categories"][0]["amount_deposited"]

    assert jan_dep == 50.0
    assert feb_dep == 150.0
    assert summaries[1]["categories"][0]["contribution_change_marker"] \
        == "*** Monthly contribution increased by $100.00 ***"

