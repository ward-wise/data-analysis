"""Spread vs. centralized: how geographically dispersed is a ward's menu spending?

For each project we take the centroid of its geocoded geometry, then per ward compute the $-WEIGHTED
STANDARD DISTANCE — the spatial standard deviation of where the dollars go (km). High = spending fans
out across the ward; low = concentrated in a few spots. A PB-critics angle: does PB spread money more
evenly, or concentrate it where the voters are?

Prototyped on Sean's already-geocoded 2019-2022 data; the same code runs on the geocoded gap years.

  python -m scripts_automation.spread_metric
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from shapely.geometry import shape

GEOJSON = Path("data/2019-2022 data_geocoded.geojson")


def _to_km(dx, dy, lat):
    """Degrees -> km if coords are lat/lon; else assume Illinois State Plane feet -> km."""
    if abs(dx) < 5 and abs(dy) < 5:        # lat/lon deltas are tiny
        return math.hypot(dx * 111.0, dy * 111.0 * math.cos(math.radians(lat)))
    return math.hypot(dx, dy) * 0.0003048  # feet -> km


def standard_distance(points, trim_km=12.0):
    """points = [(x, y, weight)] -> $-weighted standard distance (km) around the weighted mean center.

    Robust to mis-geocodes: drops points farther than trim_km from the MEDIAN center first (no Chicago
    ward spans >12km, and standard distance squares deviations so one bad point dominates). Returns
    (std_km, n_trimmed)."""
    if len(points) < 2:
        return None, 0
    cx, cy = statistics.median([p[0] for p in points]), statistics.median([p[1] for p in points])
    lat0 = cy if abs(cy) < 90 else 41.88
    kept = [p for p in points if _to_km(p[0] - cx, p[1] - cy, lat0) <= trim_km]
    n_trim = len(points) - len(kept)
    w = sum(p[2] for p in kept)
    if w <= 0 or len(kept) < 2:
        return None, n_trim
    mx = sum(p[0] * p[2] for p in kept) / w
    my = sum(p[1] * p[2] for p in kept) / w
    lat = my if abs(my) < 90 else 41.88
    var_km2 = sum(p[2] * _to_km(p[0] - mx, p[1] - my, lat) ** 2 for p in kept) / w
    return math.sqrt(var_km2), n_trim


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--geojson", default=str(GEOJSON), help="geocoded geojson (default 2019-2022)")
    ap.add_argument("--year", type=int, help="restrict to one year (the gap-year file mixes years)")
    args = ap.parse_args()

    feats = json.load(open(args.geojson))["features"]
    label = f"{args.year}" if args.year else Path(args.geojson).stem
    by_ward = defaultdict(list)
    geocoded = 0
    for f in feats:
        g, p = f.get("geometry"), f["properties"]
        try:
            cost = float(p["cost"])
            ward = int(p["ward"])
        except (ValueError, TypeError, KeyError):
            continue
        if args.year and int(p.get("year", 0)) != args.year:
            continue
        if not g:
            continue
        try:
            c = shape(g).centroid
        except Exception:  # noqa: BLE001 — a few malformed (single-point) geometries
            continue
        if c.is_empty:
            continue
        by_ward[ward].append((c.x, c.y, cost))
        geocoded += 1

    raw = {w: standard_distance(pts) for w, pts in by_ward.items()}
    spread = {w: s for w, (s, _n) in raw.items() if s is not None}
    n_trim = sum(n for (_s, n) in raw.values())
    print(f"{geocoded:,}/{len(feats):,} line items geocoded; {n_trim} far-outlier points trimmed (mis-geocodes).")
    ranked = sorted(spread.items(), key=lambda kv: kv[1])

    print(f"\nSpending SPREAD by ward, {label} ($-weighted standard distance, km):")
    print("  most CONCENTRATED (spending clustered in a few spots):")
    for w, s in ranked[:5]:
        print(f"    Ward {w:2d}: {s:.2f} km")
    print("  most SPREAD OUT (dollars fan across the ward):")
    for w, s in ranked[-5:]:
        print(f"    Ward {w:2d}: {s:.2f} km")
    vals = sorted(spread.values())
    print(f"\n  median ward spread: {vals[len(vals)//2]:.2f} km  (range {vals[0]:.2f}-{vals[-1]:.2f})")


if __name__ == "__main__":
    main()
