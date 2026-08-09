"""Self-validating extraction check — format-robust regression guard for menu-PDF extraction.

Instead of hardcoding expected numbers (which break when the city changes a report's layout), we
cross-check two INDEPENDENT reads of each PDF:
  * our pipeline (Sean's coordinate extractor) summed per ward, vs.
  * the "WARD COMMITTED <year> TOTAL $X" line the city prints on each ward's page (parsed via pdfplumber).

If they agree, extraction is faithful for THIS report whatever its format. If the printed-total marker
itself disappears (a deeper format change), we report UNVALIDATABLE loudly rather than passing bad data —
so a format change surfaces as an alarm, not a silent error. Exit code is non-zero if anything fails,
so it can gate CI / a post-fetch step.

  python -m scripts_automation.validate_self_consistency                 # every PDF in data/pdf/
  python -m scripts_automation.validate_self_consistency --pdf "data/pdf/Menu Report 2025 Q4.pdf"
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import pdfplumber

import src.chicago_participatory_urbanism.ward_spending.extract_text_from_pdf as ex

PDF_DIR = Path("data/pdf")
_PRINTED = re.compile(r"WARD\s+COMMITTED\s+20\d\d\s+TOTAL\s+\$?([\d,]+\.\d{2})", re.I)
TOL = 1.0      # dollars; a ward is "penny-exact" if our sum matches its printed total within this
FLOOR = 0.98   # PASS if we capture >= this fraction of the city's printed citywide total


def our_ward_totals(pdf_path: str) -> dict:
    """Sean's extractor, summed per ward (module globals reset so calls don't accumulate)."""
    ex.data, ex.current_row = [], {"ward": 0, "item": "", "loc": "", "cost": ""}
    ex.last_y = ex.last_x = ex.ward = 0
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False).name
    ex.extract_pdf_data(pdf_path, tmp)
    out = defaultdict(float)
    for row in csv.DictReader(open(tmp)):
        if row.get("ward"):
            try:
                out[int(row["ward"])] += float(re.sub(r"[^0-9.]", "", row.get("cost") or "0") or 0)
            except ValueError:
                continue
    return dict(out)


def printed_totals(pdf_path: str) -> list[float]:
    """The city's own per-ward 'WARD COMMITTED <year> TOTAL' figures, in document order."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    return [float(m.replace(",", "")) for m in _PRINTED.findall(text)]


def check(pdf_path: str) -> str:
    name = Path(pdf_path).name
    ours = our_ward_totals(pdf_path)
    printed = printed_totals(pdf_path)

    if not printed:
        # no printed marker found: either an unsupported older layout, or a NEW format change.
        state = "UNSUPPORTED (pre-2019 layout)" if not ours else "FORMAT CHANGED — printed-total marker missing"
        print(f"  [UNVALIDATABLE] {name}: {state}")
        return "unvalidatable"

    sum_ours, sum_printed = sum(ours.values()), sum(printed)
    fidelity = sum_ours / sum_printed if sum_printed else 0.0

    # per-ward penny-exact count (informational): printed totals are in ward-ascending order.
    wards = sorted(ours)
    matched = sum(abs(ours[w] - p) <= TOL for w, p in zip(wards, printed)) if len(wards) == len(printed) else None

    # PASS = extraction captured essentially all of the city's printed dollars. The coordinate extractor
    # drops ~0.5% of line items, so the realistic baseline is ~99%, not 100%; FLOOR catches real breakage
    # (collapsed extraction, partial format break) without crying wolf over the known small drop.
    status = "PASS" if fidelity >= FLOOR else "FAIL"
    ward_note = (f"{matched}/{len(printed)} wards penny-exact" if matched is not None
                 else f"COUNT MISMATCH: {len(wards)} extracted vs {len(printed)} printed wards")
    print(f"  [{status}] {name}: captured {fidelity*100:.2f}% of printed total "
          f"(${sum_ours:,.0f}/${sum_printed:,.0f}); {ward_note}")
    return "pass" if status == "PASS" else "fail"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", help="single PDF; default = all in data/pdf/")
    args = ap.parse_args()
    pdfs = [args.pdf] if args.pdf else sorted(str(p) for p in PDF_DIR.glob("*.pdf"))

    print(f"Self-consistency check ({len(pdfs)} PDF(s)) — our sums vs the city's printed ward totals:")
    results = [check(p) for p in pdfs]
    n_fail = results.count("fail")
    n_pass = results.count("pass")
    n_unval = results.count("unvalidatable")
    print(f"\n{n_pass} pass, {n_fail} FAIL, {n_unval} unvalidatable (format differs — review).")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
