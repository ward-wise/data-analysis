"""Validate that our PDF extraction reproduces Sean's published numbers.

Run Sean's extract_pdf_data on a CIP menu PDF, clean the cost, aggregate per-ward totals, and compare
to the corresponding year in his published `data/2005-2023 menu spending.csv`. If the per-ward totals
match (within a small tolerance), the automated extraction is faithful and we can trust it on NEW years
the archive publishes (2024-H2, 2025+).

  python -m scripts_automation.validate_extraction --pdf "data/pdf/2023 Menu - 2-27-24.pdf" --year 2023
"""

from __future__ import annotations

import argparse
import csv
import re
import tempfile
from collections import defaultdict
from pathlib import Path

from src.chicago_participatory_urbanism.ward_spending.extract_text_from_pdf import extract_pdf_data

SEAN_CSV = Path("data/2005-2023 menu spending.csv")


def _cost(raw: str) -> float:
    cleaned = re.sub(r"[^0-9.]", "", raw or "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_ward_totals(pdf_path: str) -> dict:
    """Run Sean's extractor on a PDF -> {ward: total_dollars}."""
    with tempfile.NamedTemporaryFile("r", suffix=".csv", delete=False) as tmp:
        extract_pdf_data(pdf_path, tmp.name)
        out = defaultdict(float)
        for row in csv.DictReader(open(tmp.name)):
            if row.get("ward"):
                out[int(row["ward"])] += _cost(row.get("cost"))
    return dict(out)


def sean_ward_totals(year: int) -> dict:
    out = defaultdict(float)
    for row in csv.DictReader(open(SEAN_CSV)):
        if row.get("year") == str(year) and row.get("ward") and row.get("cost"):
            out[int(row["ward"])] += _cost(row["cost"])
    return dict(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", required=True, help="path to a CIP menu PDF (2019+ format)")
    ap.add_argument("--year", type=int, required=True)
    ap.add_argument("--tol", type=float, default=0.01, help="per-ward relative tolerance (default 1%)")
    args = ap.parse_args()

    ours, theirs = extract_ward_totals(args.pdf), sean_ward_totals(args.year)
    wards = sorted(set(ours) | set(theirs))
    ok = mism = 0
    print(f"{'ward':>4}  {'ours':>14}  {'Sean':>14}  {'match?':>7}")
    for w in wards:
        a, b = ours.get(w, 0.0), theirs.get(w, 0.0)
        match = abs(a - b) <= max(args.tol * b, 1.0)
        ok += match
        mism += not match
        flag = "ok" if match else "DIFF"
        if not match or w <= 3:  # show mismatches + a few samples
            print(f"{w:>4}  {a:>14,.0f}  {b:>14,.0f}  {flag:>7}")
    tot_o, tot_s = sum(ours.values()), sum(theirs.values())
    print(f"\n  wards matching within {args.tol:.0%}: {ok}/{len(wards)} ({mism} differ)")
    print(f"  citywide total: ours ${tot_o:,.0f} vs Sean ${tot_s:,.0f} "
          f"({(tot_o-tot_s)/tot_s*100:+.2f}%)" if tot_s else "")


if __name__ == "__main__":
    main()
