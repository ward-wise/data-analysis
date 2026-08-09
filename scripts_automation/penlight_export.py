"""Publish per-ward, per-YEAR menu-spending metrics for Penlight (vintage / period-anchored).

Each value belongs to a DATA YEAR (period_end), not the build date, so the timeline shows real
year-over-year change instead of refresh-noise. Computed from Sean's 2005-2023 menu data + our 2024-2026
extraction. COMPLETE years only (2005-2023 annual postings + 2025 full-year): partial years (2024-Q3,
2026-Q1) are skipped so budget_utilization and the latest-year scoring stay honest. spending_spread is
the current map era only (2025) — historical spread needs era-matched ward boundaries (2015/2023 remaps),
a follow-up.

  python -m scripts_automation.penlight_export
"""

from __future__ import annotations

import json
import math
import urllib.request
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

from scripts_automation.spread_metric import standard_distance

ACTIVE = {"Bicycle Infrastructure", "Pedestrian Infrastructure", "Street Redesign"}
SEAN_CSV = Path("data/2005-2023 menu spending.csv")
PROCESSED = Path("data/output/menu_2024_2026_processed.csv")
GEOJSON = Path("data/output/menu_2024_2026_geocoded.geojson")
OUT = Path("data/output/penlight_menu_spending.json")
WARD_BOUNDARIES = "https://data.cityofchicago.org/resource/p293-wvbd.geojson?$limit=5000"
SPREAD_YEAR = 2025  # current map era only; gyration normalization needs era-matched boundaries


def allocation(year: int) -> int:
    """Per-ward annual menu allotment by year (raised to $1.5M in 2021; ~$1.32M through the 2010s)."""
    return 1_500_000 if year >= 2021 else 1_320_000 if year >= 2012 else 1_300_000


def ward_gyration_radii(n_grid: int = 40) -> dict:
    """{ward: radius of gyration in km} from the 2023 ward boundaries (projected) — the spread a ward
    would have if spending were uniform. Shape-aware reference for spending spread."""
    from shapely.geometry import Point
    from shapely.prepared import prep

    data = json.loads(urllib.request.urlopen(WARD_BOUNDARIES, timeout=90).read())
    to_m = Transformer.from_crs("EPSG:4326", "EPSG:26971", always_xy=True)
    radii = {}
    for f in data.get("features", []):
        ward = f.get("properties", {}).get("ward")
        if not ward or not f.get("geometry"):
            continue
        geom = shp_transform(lambda x, y: to_m.transform(x, y), shape(f["geometry"]))
        minx, miny, maxx, maxy = geom.bounds
        pg = prep(geom)
        grid = [(minx + (maxx - minx) * i / n_grid, miny + (maxy - miny) * j / n_grid)
                for i in range(n_grid + 1) for j in range(n_grid + 1)]
        inside = [p for p in grid if pg.contains(Point(p))]
        if len(inside) < 5:
            continue
        mx = sum(p[0] for p in inside) / len(inside)
        my = sum(p[1] for p in inside) / len(inside)
        var = sum((p[0] - mx) ** 2 + (p[1] - my) ** 2 for p in inside) / len(inside)
        radii[str(int(ward))] = math.sqrt(var) / 1000.0
    return radii


def category_rows():
    """(ward, year, cost, category) for COMPLETE years: Sean's 2005-2023 + our 2025 full-year."""
    for _, r in pd.read_csv(SEAN_CSV).iterrows():
        try:
            y = int(r["year"])
            if 2005 <= y <= 2023 and float(r["cost"]) > 0:
                yield int(r["ward"]), y, float(r["cost"]), str(r.get("category", ""))
        except (ValueError, TypeError):
            continue
    proc = pd.read_csv(PROCESSED)
    for _, r in proc[(proc.year == 2025) & (proc.period == "Q4")].iterrows():
        try:
            if float(r["cost"]) > 0:
                yield int(r["ward"]), 2025, float(r["cost"]), str(r.get("category", ""))
        except (ValueError, TypeError):
            continue


def main():
    tot, active = defaultdict(float), defaultdict(float)
    cats = defaultdict(lambda: defaultdict(float))
    for ward, year, cost, cat in category_rows():
        tot[(year, ward)] += cost
        if cat in ACTIVE:
            active[(year, ward)] += cost
        cats[(year, ward)][cat] += cost

    # Per-category shares beyond active transport (Penlight request 2026-08-05): the seven
    # categories covering ~95% of all menu dollars, each as % of the ward-year's spending.
    CATEGORY_SHARES = {
        "share_street_resurfacing": {"Street Resurfacing"},
        "share_lighting": {"Lighting"},
        "share_sidewalks": {"Sidewalk Repair"},
        "share_alleys": {"Alleys"},
        "share_parks": {"Parks"},
        "share_police_cameras": {"Police Cameras"},
        "share_schools": {"Schools"},
    }
    years: dict[int, dict] = defaultdict(dict)
    for (year, ward), t in tot.items():
        if t <= 0:
            continue
        hhi = sum((c / t) ** 2 for c in cats[(year, ward)].values())
        years[year][str(ward)] = {
            "active_transport_share": round(active[(year, ward)] / t * 100, 1),
            # capped at 100 = "fully deployed": >100% happens via prior-year rollover (and the historical
            # allotment is approximate), and the accountability signal we want is UNDER-spending.
            "budget_utilization": round(min(100.0, t / allocation(year) * 100), 1),
            "project_diversity": round((1 - hhi) * 100, 1),
            **{field: round(sum(cats[(year, ward)][c] for c in members) / t * 100, 1)
               for field, members in CATEGORY_SHARES.items()},
        }

    # spending_spread for the current era only (2025), district-shape-adjusted
    radii = ward_gyration_radii()
    pts = defaultdict(list)
    for f in json.load(open(GEOJSON))["features"]:
        g, p = f.get("geometry"), f["properties"]
        if not g or int(p.get("year", 0)) != SPREAD_YEAR:
            continue
        try:
            c = shape(g).centroid
            pts[str(int(p["ward"]))].append((c.x, c.y, float(p["cost"])))
        except Exception:  # noqa: BLE001
            continue
    for w, pl in pts.items():
        r = radii.get(w)
        std_km, _ = standard_distance(pl, trim_km=max(4.0, 3 * r) if r else 12.0)
        if std_km is not None and r and w in years.get(SPREAD_YEAR, {}):
            years[SPREAD_YEAR][w]["spending_spread"] = round(std_km / r * 100, 1)

    payload = {
        "_about": (
            "Per-ward, per-YEAR aldermanic menu-money spending (the alder's most direct discretionary "
            "lever). Each metric is anchored to its DATA YEAR (a vintage/period metric), from the city's "
            "published CIP menu PDFs via the ward-wise/data-analysis pipeline. Complete years only "
            "(2005-2023 + 2025); 2024/2026 are partial and omitted. budget_utilization uses the year's "
            "allotment (~$1.32M pre-2021, $1.5M after). spending_spread is district-shape-adjusted and "
            "current-era only. NOTE: ward boundaries were remapped in 2015 and 2023, so cross-era "
            "comparisons should be read within a single map era (the term-delta view handles this)."
        ),
        "source": "Chicago aldermanic menu spending (CIP PDFs) via ward-wise/data-analysis pipeline",
        "as_of": "2026-06",
        "temporal_mode": "vintage",
        "metrics": ["active_transport_share", "budget_utilization", "project_diversity",
                    "spending_spread", *sorted(CATEGORY_SHARES)],
        "years": {str(y): years[y] for y in sorted(years)},
    }
    OUT.write_text(json.dumps(payload, indent=2))
    yr = sorted(years)
    print(f"wrote {len(yr)} years ({yr[0]}-{yr[-1]}) -> {OUT}")
    for y in yr:
        at = sorted(v["active_transport_share"] for v in years[y].values())
        print(f"  {y}: {len(years[y]):>2} wards, active-transport median {at[len(at)//2]:.1f}%")


if __name__ == "__main__":
    main()
