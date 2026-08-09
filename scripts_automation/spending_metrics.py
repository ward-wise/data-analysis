"""Demo the proposed menu-spending metrics on the processed current-term data.

Metrics that need only ward/year/cost/category (no geocoding):
  * spending RATE — from cumulative quarterly reports: how fast a ward spends its $1.5M through the year,
    and (for the live year) how much discretionary budget is left.
  * project COUNT + SIZE — many small projects vs few large ones.
  * project FOCUS — category concentration (Herfindahl) + dominant category.
(spread vs centralized needs geocoded locations — a later step.)

  python -m scripts_automation.spending_metrics
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ALLOCATION = 1_500_000  # annual menu allotment per ward since 2021
DATA = Path("data/output/menu_2024_2026_processed.csv")


def _focus(sub: pd.DataFrame):
    """Herfindahl concentration (0=spread across categories, 1=all in one) + dominant category."""
    shares = sub.groupby("category")["cost"].sum() / sub["cost"].sum()
    return float((shares**2).sum()), shares.idxmax(), float(shares.max())


def main():
    df = pd.read_csv(DATA)

    # ---- spending RATE (2025, full cycle: cumulative Q1 -> Q2 -> Q4) ----
    y25 = df[df.year == 2025]
    cum = y25.pivot_table(index="ward", columns="period", values="cost", aggfunc="sum").fillna(0.0)
    cum["pace_H1"] = (cum.get("Q2", 0) / cum["Q4"]).clip(upper=1) * 100   # % of annual spent by mid-year
    cum["utilization"] = cum["Q4"] / ALLOCATION * 100                     # % of $1.5M used by year-end
    print("Spending RATE, 2025 (cumulative through each quarter):")
    fast = cum.sort_values("pace_H1", ascending=False)
    print("  fastest spenders (most of the year's $ out the door by H1):")
    for w, r in fast.head(4).iterrows():
        print(f"    Ward {int(w):2d}: {r['pace_H1']:4.0f}% spent by mid-2025, {r['utilization']:3.0f}% of $1.5M used")
    print("  slowest:")
    for w, r in fast.tail(3).iterrows():
        print(f"    Ward {int(w):2d}: {r['pace_H1']:4.0f}% spent by mid-2025, {r['utilization']:3.0f}% of $1.5M used")

    # ---- budget LEFT (live year 2026, through Q1) ----
    q1_26 = df[(df.year == 2026)].groupby("ward")["cost"].sum()
    print("\nBudget LEFT, 2026 (through Q1 — nominal $1.5M, excludes rollover):")
    spent_most = q1_26.sort_values(ascending=False)
    print("  furthest along:")
    for w, spent in spent_most.head(3).items():
        print(f"    Ward {int(w):2d}: ${spent:>10,.0f} spent  ->  ${ALLOCATION-spent:>10,.0f} left ({spent/ALLOCATION*100:.0f}% used)")
    print(f"  {(q1_26 < ALLOCATION*0.02).sum()} of 50 wards have spent <2% so far (near-full budget remaining).")

    # ---- project COUNT, SIZE, FOCUS (2025 full year) ----
    full25 = y25[y25.period == "Q4"]
    print("\nProject profile, 2025 (count / avg size / focus):")
    prof = full25.groupby("ward").agg(n=("cost", "size"), avg=("cost", "mean"), total=("cost", "sum"))
    print(f"  most projects: Ward {int(prof.n.idxmax())} ({prof.n.max()}), "
          f"fewest: Ward {int(prof.n.idxmin())} ({prof.n.min()})")
    print(f"  biggest avg project: Ward {int(prof.avg.idxmax())} (${prof.avg.max():,.0f}), "
          f"smallest: Ward {int(prof.avg.idxmin())} (${prof.avg.min():,.0f})")
    foc = {w: _focus(full25[full25.ward == w]) for w in full25.ward.unique()}
    most = max(foc, key=lambda w: foc[w][0]); least = min(foc, key=lambda w: foc[w][0])
    print(f"  most focused: Ward {int(most)} (HHI {foc[most][0]:.2f}, {foc[most][2]*100:.0f}% on {foc[most][1]})")
    print(f"  most diversified: Ward {int(least)} (HHI {foc[least][0]:.2f}, top is {foc[least][2]*100:.0f}% {foc[least][1]})")


if __name__ == "__main__":
    main()
