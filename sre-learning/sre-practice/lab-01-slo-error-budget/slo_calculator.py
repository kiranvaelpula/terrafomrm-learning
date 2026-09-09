#!/usr/bin/env python3
"""
Lab 01: SLO and Error Budget Calculator.
Turns an SLO into an error budget and reports burn rate + recommended action.
"""


def error_budget_minutes(slo_percent, window_days=30):
    """How many 'bad' minutes are allowed by the SLO over the window."""
    window_minutes = window_days * 24 * 60
    return (100 - slo_percent) / 100 * window_minutes


def budget_status(slo_percent, actual_percent, window_days=30):
    """Report budget consumed, remaining, and recommended action."""
    window_minutes = window_days * 24 * 60
    total_budget = error_budget_minutes(slo_percent, window_days)
    consumed = (100 - actual_percent) / 100 * window_minutes
    remaining = total_budget - consumed
    remaining_pct = (remaining / total_budget * 100) if total_budget else 0

    print(f"SLO: {slo_percent}% | Window: {window_days} days")
    print(f"Total error budget: {total_budget:.1f} minutes")
    print(f"Consumed: {consumed:.1f} min | "
          f"Remaining: {remaining:.1f} min ({remaining_pct:.0f}%)")

    # Error budget policy → recommended action
    if remaining <= 0:
        print("Status: EXHAUSTED — freeze risky releases, focus on reliability")
    elif remaining_pct < 10:
        print("Status: LOW — caution, only low-risk changes")
    elif remaining_pct < 50:
        print("Status: MODERATE — proceed with extra review")
    else:
        print("Status: HEALTHY — ship freely, take calculated risks")

    return remaining_pct


def burn_rate(slo_percent, actual_percent):
    """How fast budget is being consumed vs the sustainable rate.
    1x = consuming exactly at the SLO threshold. >1x = burning too fast."""
    allowed_error = (100 - slo_percent)
    actual_error = (100 - actual_percent)
    if allowed_error == 0:
        return float("inf")
    rate = actual_error / allowed_error
    print(f"Burn rate: {rate:.1f}x", end="  ")
    if rate >= 10:
        print("→ FAST BURN: page immediately!")
    elif rate > 1:
        print("→ burning faster than sustainable")
    else:
        print("→ sustainable")
    return rate


if __name__ == "__main__":
    print("═══ Error Budget Report ═══\n")

    # Example: 99.9% SLO, actual availability 99.95%
    budget_status(slo_percent=99.9, actual_percent=99.95)
    print()
    burn_rate(slo_percent=99.9, actual_percent=99.95)

    print("\n─── Scenario: bad month ───")
    budget_status(slo_percent=99.9, actual_percent=99.5)   # over-budget
    burn_rate(slo_percent=99.9, actual_percent=99.5)
