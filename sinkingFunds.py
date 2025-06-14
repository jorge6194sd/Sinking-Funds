def sinking_funds_simulation(
    categories,
    start_year=2025,
    start_month=1,
    lumpsums=None,
    payment_adjustments=None,
    future_contribution_changes=None,
    monthly_interest=True,
    num_months=12,
    verbose=True
):
    """
    categories: List[dict], each with:
        {
            'name': str,
            'balance': float,
            'monthly_contribution': float,
            'apr': float         # e.g., 0.04 for 4% interest
        }

    start_year, start_month: The calendar year/month you begin tracking.

    lumpsums: Dict[str, Dict[(year, month), float]]
      e.g., {
         'Tools': {
             (2025, 9): 500.0
         },
         'Condo': {
             (2025, 10): 1000.0
         }
      }
      Means in Sept 2025, Tools gets an extra $500; in Oct 2025, Condo gets $1000, etc.

    payment_adjustments: Dict[str, Dict[(year, month), float]]
      e.g., {
         'Tools': {
             (2025, 9): -20.0
         },
         'Condo': {
             (2025, 10): 50.0
         }
      }
      Means Tools deposit is $20 less in Sept 2025, Condo deposit is $50 more in Oct 2025
      (for that month only).

    future_contribution_changes: Dict[str, Dict[(year, month), float]]
      e.g., {
         'Investment': {
             (2026, 6): 500.0
         }
      }
      Means that starting in June 2026, the 'Investment' category's base monthly_contribution
      is changed permanently to $500.00 for all future months (until changed again).

    monthly_interest: bool
      If True, each category with apr>0.0 earns (apr/12)*balance at the start of each month.

    num_months: int
      How many months to simulate before stopping.

    verbose: bool
      If True, prints a summary table. Otherwise just returns the data.

    Returns:
        month_summaries: list of dict, each entry containing:
          {
            'year': int,
            'month_num': int,
            'categories': List[{
                'name': str,
                'apr': float,
                'balance': float,
                'amount_deposited': float,
                'payment_change_marker': str,       # e.g. "*** Payment increased by $50.00 ***"
                'lumpsum_marker': str,             # e.g. "*** LUMP SUM APPLIED: $300.00 ***"
                'contribution_change_marker': str   # e.g. "*** Monthly contribution increased by $100.00 ***"
            }]
          }
        Summaries for each month simulated.
    """

    if lumpsums is None:
        lumpsums = {}
    if payment_adjustments is None:
        payment_adjustments = {}
    if future_contribution_changes is None:
        future_contribution_changes = {}

    # Copy categories so as not to mutate the original
    categories = [dict(cat) for cat in categories]

    month_summaries = []

    for month_index in range(num_months):
        # Determine the current year/month
        current_month_num = ((start_month - 1) + month_index) % 12 + 1
        year_shift        = ((start_month - 1) + month_index) // 12
        current_year      = start_year + year_shift

        # 1) Apply monthly interest if applicable
        if monthly_interest:
            for cat in categories:
                if cat['apr'] > 0 and cat['balance'] > 0:
                    interest = cat['balance'] * (cat['apr'] / 12.0)
                    cat['balance'] += interest

        # 2) Check if this month triggers a permanent monthly_contribution change
        #    We store the old->new amounts in a dictionary so we know exactly
        #    how much it changed for the marker.
        contribution_changes_this_month = {}
        for cat in categories:
            cat_name = cat['name']
            if cat_name in future_contribution_changes:
                if (current_year, current_month_num) in future_contribution_changes[cat_name]:
                    old_contribution = cat['monthly_contribution']
                    new_contribution = future_contribution_changes[cat_name][(current_year, current_month_num)]
                    cat['monthly_contribution'] = new_contribution
                    contribution_changes_this_month[cat_name] = (old_contribution, new_contribution)

        # 3) Handle monthly contributions + adjustments
        lumpsum_paid = {cat['name']: 0.0 for cat in categories}  # track lumpsum usage
        this_month_deposit = {cat['name']: 0.0 for cat in categories}
        payment_adjs_this_month = {}  # track the payment adjustment (increase/decrease) for each cat

        for cat in categories:
            name = cat['name']
            base_contrib = cat['monthly_contribution']
            adj = 0.0
            if name in payment_adjustments:
                adj = payment_adjustments[name].get((current_year, current_month_num), 0.0)

            deposit_amount = base_contrib + adj
            if deposit_amount < 0:
                deposit_amount = 0.0  # prevent negative deposit

            # Add deposit to the category's balance
            cat['balance'] += deposit_amount
            this_month_deposit[name] = deposit_amount
            payment_adjs_this_month[name] = adj

        # 4) Lumpsums
        for cat in categories:
            name = cat['name']
            lumpsum_dict_for_cat = lumpsums.get(name, {})
            lumpsum_this_month = lumpsum_dict_for_cat.get((current_year, current_month_num), 0.0)
            if lumpsum_this_month > 0:
                cat['balance'] += lumpsum_this_month
                lumpsum_paid[name] = lumpsum_this_month

        # Build month data for reporting
        month_data = {
            'year': current_year,
            'month_num': current_month_num,
            'categories': []
        }

        # 5) Determine markers
        for cat in categories:
            name = cat['name']
            apr_val = cat['apr']
            bal_val = round(cat['balance'], 2)
            deposited_val = round(this_month_deposit[name], 2)

            # Payment change marker (if any) - display increase or decrease
            adj_amt = payment_adjs_this_month[name]
            payment_change_marker = ""
            if adj_amt > 0:
                payment_change_marker = f"*** Payment increased by ${adj_amt:.2f} ***"
            elif adj_amt < 0:
                payment_change_marker = f"*** Payment decreased by ${abs(adj_amt):.2f} ***"

            # Lumpsum marker
            lumpsum_marker = ""
            if lumpsum_paid[name] > 0.0:
                lumpsum_marker = f"*** LUMP SUM APPLIED: ${lumpsum_paid[name]:.2f} ***"

            # Monthly contribution change marker (permanent changes)
            contribution_change_marker = ""
            if name in contribution_changes_this_month:
                old_c, new_c = contribution_changes_this_month[name]
                diff_c = new_c - old_c
                if diff_c > 0:
                    contribution_change_marker = f"*** Monthly contribution increased by ${diff_c:.2f} ***"
                elif diff_c < 0:
                    contribution_change_marker = f"*** Monthly contribution decreased by ${abs(diff_c):.2f} ***"
                else:
                    # If somehow it didn't change, we won't print anything
                    pass

            month_data['categories'].append({
                'name': name,
                'apr': apr_val,
                'balance': bal_val,
                'amount_deposited': deposited_val,
                'payment_change_marker': payment_change_marker,
                'lumpsum_marker': lumpsum_marker,
                'contribution_change_marker': contribution_change_marker
            })

        month_summaries.append(month_data)

    # -- Print results if verbose --
    if verbose:
        print("\nSINKING FUNDS SCHEDULE (by Calendar Month)\n" + "="*70)
        for month_info in month_summaries:
            y = month_info['year']
            m = month_info['month_num']
            print(f"\n{y}-{m:02d}")
            print("-"*70)
            for cat_info in month_info['categories']:
                apr_str = f"{cat_info['apr']*100:.2f}%"
                bal_str = f"${cat_info['balance']:.2f}"
                dep_str = f"${cat_info['amount_deposited']:.2f}"

                # Markers
                payment_marker = cat_info['payment_change_marker']
                lumpsum_marker = cat_info['lumpsum_marker']
                contrib_marker = cat_info['contribution_change_marker']

                line_str = (
                    f"  {cat_info['name']:<20} {apr_str:<8} "
                    f"Dep: {dep_str:<8} Bal: {bal_str:<10}"
                )
                # Append markers if they exist
                if payment_marker:
                    line_str += " " + payment_marker
                if lumpsum_marker:
                    line_str += " " + lumpsum_marker
                if contrib_marker:
                    line_str += " " + contrib_marker

                print(line_str)
        print("\nSimulation complete for", num_months, "months.\n")

    return month_summaries


# ------------------
# EXAMPLE USAGE
# ------------------
if __name__ == "__main__":

    # Example categories
    sinking_funds_input = [
        {
            'name': 'Tools',
            'balance': 0.0,
            'monthly_contribution': 50.0,
            'apr': 0.00
        },
        {
            'name': 'Business Investments',
            'balance': 0.0,
            'monthly_contribution': 80.0,
            'apr': 0.00
        },
        {
            'name': 'Clothes',
            'balance': 0.0,
            'monthly_contribution': 35.0,
            'apr': 0.00
        },
        {
            'name': 'Savings',
            'balance': 0.0,
            'monthly_contribution': 200.0,
            'apr': 0.00
        },
        {
            'name': 'Investment',
            'balance': 0.0,
            'monthly_contribution': 200.0,
            'apr': 0.07
        },
         {
            'name': 'Car Maintenance',
            'balance': 0.0,
            'monthly_contribution': 70.0,
            'apr': 0.0
        },
        {
            'name': 'Condo',
            'balance': 0.0,
            'monthly_contribution': 100.0,
            'apr': 0.0
        },
          {
            'name': 'Health',
            'balance': 0.0,
            'monthly_contribution': 80.0,
            'apr': 0
        },
         {
            'name': 'Travel',
            'balance': 0.0,
            'monthly_contribution': 60.0,
            'apr': 0.0
        }
    ]

    # Number of months to simulate
    months_to_simulate = 120

    # Lumpsums
    lumpsums_dict = {
        'Tools': {
            (2025, 6): 60,
             (2026, 3): 100
        },
          'Condo': {
            (2026, 3): 150,
          },
            'Investment': {
            (2026, 3): 150,
          }
          
    }

    # Payment adjustments (one-time)
    payment_adjustments_dict = {
        'Tools': {
            (2025, 11): 150
        },
         'Car Maintenance': {
            (2025, 6): -70
        },
        'Condo': {
            (2025, 11): 300
        },
        'Clothes': {
            (2025, 6): -50
        },
          'Health': {
            (2025, 6): -80
        },
         
          'Travel': {
            (2025, 6): -60
        }
    }

    # Future contribution changes (permanent)
    future_contribution_changes_dict = {
        'Investment': {
            (2026, 7): 2200.0
        },
        'Condo': {
            (2026, 7): 200.0
        }
    }

    # Run the simulation starting in June 2025
    summaries = sinking_funds_simulation(
        categories=sinking_funds_input,
        start_year=2025,
        start_month=6,
        lumpsums=lumpsums_dict,
        payment_adjustments=payment_adjustments_dict,
        future_contribution_changes=future_contribution_changes_dict,
        monthly_interest=True,
        num_months=months_to_simulate,
        verbose=True
    )
