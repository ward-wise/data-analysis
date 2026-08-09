"""Process the 2024-2026 gap-year PDFs through extract + categorize, extending Sean's 2005-2023 data.

Sean's published CSV stops at 2023. The fetched quarterly reports (cumulative year-to-date) cover the
current term. We run them through Sean's own extractor + categorizer so the schema matches, tagging each
with (year, period) — the latest period per year gives annual totals; the quarterly sequence within a
year (e.g. 2025 Q1->Q2->Q4) gives the spending-rate curve.

  python -m scripts_automation.process_gap_years
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

import src.chicago_participatory_urbanism.ward_spending.extract_text_from_pdf as ex
from src.chicago_participatory_urbanism.ward_spending.post_processor import post_process_data

# (filename, year, period). Period is the cumulative-through-quarter the report covers.
GAP_PDFS = [
    ("AMR-2024-(Q1-Q3).pdf", 2024, "Q3"),
    ("Q1 2025 Aldermanic Menu Program Report.pdf", 2025, "Q1"),
    ("Menu Report 2025 Q2.pdf", 2025, "Q2"),
    ("Menu Report 2025 Q4.pdf", 2025, "Q4"),
    ("2026 Q1 Menu Report.pdf", 2026, "Q1"),
]
PDF_DIR = Path("data/pdf")
OUT = Path("data/output/menu_2024_2026_processed.csv")


def _extract_reset(pdf_path: str, csv_path: str):
    """Run Sean's extractor with module-global state reset (it accumulates across calls otherwise)."""
    ex.data, ex.current_row = [], {"ward": 0, "item": "", "loc": "", "cost": ""}
    ex.last_y = ex.last_x = ex.ward = 0
    ex.extract_pdf_data(pdf_path, csv_path)


def process_one(filename: str, year: int, period: str) -> pd.DataFrame:
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False).name
    _extract_reset(str(PDF_DIR / filename), tmp)
    df = post_process_data(tmp, year)  # cleans cost, strips year suffix, adds category
    df["period"] = period
    df["source_pdf"] = filename
    return df


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for filename, year, period in GAP_PDFS:
        df = process_one(filename, year, period)
        frames.append(df)
        print(f"{year} {period:5} {filename[:34]:36} rows={len(df):>4}  wards={df['ward'].nunique():>3}  "
              f"${df['cost'].sum():>13,.0f}  cats={df['category'].nunique()}")
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(OUT, index=False)
    print(f"\nwrote {len(combined):,} categorized line items -> {OUT}")

    print("\nAnnual snapshot (latest cumulative period per year):")
    latest = {2024: "Q3", 2025: "Q4", 2026: "Q1"}
    for year, period in latest.items():
        sub = combined[(combined.year == year) & (combined.period == period)]
        top = sub.groupby("category")["cost"].sum().sort_values(ascending=False).head(3)
        topstr = ", ".join(f"{c} {v/sub.cost.sum()*100:.0f}%" for c, v in top.items())
        print(f"  {year} (thru {period}): {sub['ward'].nunique()} wards, ${sub.cost.sum():,.0f} | top: {topstr}")


if __name__ == "__main__":
    main()
