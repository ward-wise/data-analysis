"""Auto-fetch Chicago aldermanic menu-spending PDFs from the city's CIP asset paths.

The city's index PAGES are WAF-gated to scripts and the PDF filenames are inconsistent (varying date
suffixes, "Menu Posting" vs quarterly "Aldermanic Menu Program Report" vs "AMR-YYYY"), so we can't guess
URLs. But the PDF ASSET files (under /content/dam/.../) are NOT gated, and the Wayback Machine keeps
un-gated snapshots of the index pages that LIST those asset URLs. So we discover URLs from Wayback
snapshots of the index pages + a manifest of verified ones, then download the assets directly.

  python -m scripts_automation.fetch_menu_pdfs            # discover + download to data/pdf/
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
DEST = Path("data/pdf")
DAM = "https://www.chicago.gov/content/dam/city/depts/obm"
# Index pages the city has used for menu spending (Wayback has un-gated snapshots that list the assets).
INDEX_PAGES = [
    "https://www.chicago.gov/city/en/depts/obm/provdrs/cap_improve/svcs/cip-archive.html",
    "https://www.chicago.gov/city/en/depts/obm/provdrs/budget/svcs/CapitalPublications.html",
]
# Verified-working asset URLs (a floor in case Wayback misses one).
MANIFEST = [
    f"{DAM}/general/CIP/CIPDocs/AldermanicMenuPostings/{n}"
    for n in ("2012Menu.pdf", "2013Menu.pdf", "2014Menu.pdf", "2015Menu.pdf", "2016Menu.pdf",
              "2017OBMMenu50WardDetailsRpt3Dec2018.pdf", "2018OBMrpt_MenuWarddetailsprojects2DEC2019.pdf",
              "2019 Menu Posting - 22-10-02.pdf", "2020 Menu Posting - 22-10-02.pdf",
              "2021 Menu Posting - 22-10-02.pdf")
] + [
    f"{DAM}/supp_info/CIP_Archive/Aldermanic Menu/2022 Menu - 2-9-23.pdf",
    f"{DAM}/supp_info/CIP_Archive/Aldermanic Menu/AMR-2024-(Q1-Q3).pdf",
    f"{DAM}/supp_info/CIP_Archive/Q1 2025 Aldermanic Menu Program Report.pdf",
]
_ASSET_RE = re.compile(r"https://www\.chicago\.gov/content/dam[^\"'\\ )]*?(?:Menu|AMR)[^\"'\\ )]*?\.pdf",
                       re.IGNORECASE)


def _norm(url: str) -> str:
    """Percent-encode spaces in the path (urllib rejects them) while preserving (), /, and existing %."""
    parts = urlsplit(url)
    return urlunsplit(parts._replace(path=quote(parts.path, safe="/()%")))


def _get(url, timeout=60):
    return urlopen(Request(_norm(url), headers={"User-Agent": UA}), timeout=timeout)


def _exists(url: str) -> bool:
    """True if the asset returns 200 (GET headers, don't download the body)."""
    try:
        resp = _get(url, 15)
        ok = getattr(resp, "status", 200) == 200
        resp.close()
        return ok
    except Exception:  # noqa: BLE001 — 404/network -> treat as absent
        return False


def probe_recent_quarters(through_year=None) -> set:
    """Directly probe recent quarterly reports. Filenames are inconsistent (three observed styles), so
    try each style per (year, quarter). Removes the Wayback-snapshot lag for current-term data."""
    import datetime

    last = through_year or datetime.date.today().year
    cip = f"{DAM}/supp_info/CIP_Archive"
    found = set()
    for y in range(2024, last + 2):  # +2 so a just-started next year is covered
        for q in (1, 2, 3, 4):
            for cand in (f"{cip}/Aldermanic Menu/{y} Q{q} Menu Report.pdf",
                         f"{cip}/Aldermanic Menu/Menu Report {y} Q{q}.pdf",
                         f"{cip}/Q{q} {y} Aldermanic Menu Program Report.pdf"):
                if _exists(cand):
                    found.add(cand)
                time.sleep(0.15)
    return found


def discover_from_wayback() -> set:
    """Menu-PDF asset URLs found in the latest Wayback snapshot of each index page."""
    found = set()
    for page in INDEX_PAGES:
        try:
            avail = json.loads(_get(f"http://archive.org/wayback/available?url={quote(page)}", 30).read())
            snap = avail.get("archived_snapshots", {}).get("closest", {}).get("url")
            if not snap:
                continue
            html = _get(snap).read().decode("utf-8", "replace")
            found |= {m for m in _ASSET_RE.findall(html) if "author.chicago" not in m}
        except Exception as exc:  # noqa: BLE001
            print(f"  wayback discovery failed for {page}: {exc}")
    return found


def download(url: str) -> str | None:
    DEST.mkdir(parents=True, exist_ok=True)
    name = unquote(url.rsplit("/", 1)[-1])
    dest = DEST / name
    if dest.exists() and dest.stat().st_size > 1000:
        return f"have    {name}"
    try:
        data = _get(url, 120).read()
    except Exception as exc:  # noqa: BLE001 — 404s + network blips are expected; skip
        return f"MISS    {name} ({getattr(exc, 'code', exc)})"
    if not data.startswith(b"%PDF"):
        return f"NOTPDF  {name}"
    dest.write_bytes(data)
    return f"got     {name} ({len(data)//1024} KB)"


def main():
    print("probing recent quarters + Wayback discovery …")
    urls = sorted({_norm(u) for u in set(MANIFEST) | discover_from_wayback() | probe_recent_quarters()})
    print(f"resolved {len(urls)} menu-PDF URLs (manifest + Wayback + recent-quarter probe); downloading to {DEST}/ …")
    got = miss = 0
    for url in urls:
        result = download(url)
        print("  " + result)
        got += result.startswith(("got", "have"))
        miss += result.startswith(("MISS", "NOTPDF"))
        time.sleep(0.3)  # be polite to the city's server
    print(f"\n{got} PDFs available locally, {miss} missing/unreadable.")


if __name__ == "__main__":
    main()
