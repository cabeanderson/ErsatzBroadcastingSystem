#!/usr/bin/env python3
"""
scout_archive.py — find candidate interstitial material on archive.org.

Read-only. This never downloads anything; it reports what exists, how big it
is, and what it would cost, so the download decision stays a human one.

§8 of interstitial-policy.md ranks eight acquisition gaps and names the search
term that unlocks them ("aircheck"), but not where to point it. This is that
half. Each gap below is one named query, so the ranked list and the search are
the same artifact and cannot drift apart.

## Why advancedsearch and not the scrape API

`services/search/v1/scrape` silently ignores unfielded phrases. A query of
`mediatype:movies AND "nick at nite"` returns 57.7 million items -- the entire
archive, sorted by identifier -- rather than an error, so a caller who does not
check `total` gets a confident page of Malayalam literature and no warning at
all. `advancedsearch.php` parses the same query correctly. The scrape endpoint
is still right for enumerating a *collection*, where the query is one fielded
term; it is wrong for everything here.

## Why size is reported so loudly

The material is stored at archival bitrates and we want it at broadcast filler
bitrates. A Vista Group aircheck is 5-77 GB of 60fps VHS upscale and yields
perhaps 40 usable spots; run through `split_reels.py` those 40 spots are about
200 MB. The ratio is roughly 35:1, and the pool has 3.3 TB free against a 1.2 TB
collection, so "download the collection" is not a plan.

The intended cycle is one item at a time: fetch, split, keep the segments,
delete the source. `--plan` prints that arithmetic for a chosen gap.

## Downloading, when it comes to that

Every item is plain HTTPS -- `https://archive.org/download/<identifier>/` lists
its files, and each file is fetchable with curl. There is no API key and no
`ia` CLI dependency, which keeps this consistent with the repo's stdlib-only
rule. Prefer the smallest derivative that is still SD: the h.264 `*.ia.mp4`
derivative is typically a fifth of the listed item size and is already the
format the staged reels arrived in.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict

ENDPOINT = "https://archive.org/advancedsearch.php"
DOWNLOAD = "https://archive.org/download"

# Keyed to the §8 ranking. The rank is the dict order; the comment on each is
# the gap it fills, in the policy document's own words.
GAPS = OrderedDict([
    ("disney", {
        "why": "#2 — named ask, zero assets on disk, sharpest block definition",
        "q": 'mediatype:movies AND (title:("Disney Channel") OR title:("Disney Afternoon")'
             ' OR title:("One Saturday Morning"))'
             ' AND (title:(bumper OR ident OR promo OR commercial OR break))',
    }),
    ("goodtimes-50s60s", {
        "why": "#3 — widest span on the lineup; 50s/60s is scarcest and also serves 120 and 247",
        "q": 'mediatype:movies AND (title:(commercials OR aircheck OR promos))'
             ' AND (title:(1950s OR 1960s OR 1955 OR 1958 OR 1962 OR 1965 OR 1968))',
    }),
    ("nick-at-nite", {
        "why": "#4 — strong graphic identity, well preserved, serves two blocks on 247",
        "q": 'mediatype:movies AND title:("Nick at Nite" OR Nickelodeon)'
             ' AND (title:(bumper OR ident OR promo OR "commercial break"))',
    }),
    ("uk-continuity", {
        "why": "#5 — highest distinctiveness per file; cannot be substituted from US material",
        "q": 'mediatype:movies AND (title:(BBC OR ITV OR "Channel 4" OR Thames OR Granada))'
             ' AND (title:(continuity OR idents OR ident OR "off air" OR aircheck))',
    }),
    ("dragonball", {
        "why": "#6 — the one per-show set where airtime badly outruns assets (5 files)",
        "q": 'mediatype:movies AND title:("Dragon Ball" OR Toonami)'
             ' AND (title:(bumper OR bumpers OR promo OR promos OR ident))',
    }),
    ("cn-daytime", {
        "why": "#7 — cartoon network/general/ is scaffolded and empty",
        "q": 'mediatype:movies AND title:("Cartoon Network")'
             ' AND (title:(bumper OR bumpers OR ident OR promo OR "commercial break"))',
    }),
    ("woc", {
        "why": "the highest-yield token on this archive — 'with original commercials', "
               "ad breaks intact, usually one dated network evening",
        "q": 'mediatype:movies AND title:(WOC)',
    }),
    ("disney-afternoon", {
        "why": "the 15:00 appointment's wraparounds — well covered under WOC, "
               "contrary to the policy's read",
        "q": 'mediatype:movies AND title:("Disney Afternoon")',
    }),
    ("bbc-continuity", {
        "why": "Across the Pond's remaining gap. The tier-5 fetch turned out to be "
               "Channel 4, not BBC, and skews 1995-96 -- the older decades are "
               "still unserved",
        "q": 'mediatype:movies AND title:(BBC)'
             ' AND title:(continuity OR closedown OR "test card" OR testcard OR idents)',
    }),
    ("bbc-early", {
        "why": "the scarce end -- BBC closedowns of the 70s and 80s exist and are "
               "tiny (a few MB each), unlike the 15-33 GB 2000s captures",
        "q": 'mediatype:movies AND title:(BBC)'
             ' AND title:(closedown OR continuity)'
             ' AND title:(1970 OR 1975 OR 1978 OR 1979 OR 1980 OR 1981 OR 1982'
             ' OR 1983 OR 1984 OR 1985 OR 1986 OR 1987 OR 1988 OR 1989 OR 70s OR 80s)',
    }),
    ("vista-airchecks", {
        "why": "#1's successor — the deepest single well of US off-air captures found",
        "q": 'collection:the-vista-group-video AND title:("TV Commercials")',
    }),
])


def search(query: str, rows: int, sort: str) -> dict:
    """One advancedsearch call. Returns the parsed `response` object.

    `numFound` is returned to the caller rather than swallowed because it is
    the only signal that a query was understood -- see the module docstring on
    what an ignored query looks like.
    """
    params = [("q", query), ("rows", str(rows)), ("output", "json"),
              ("sort[]", sort)]
    params += [("fl[]", f) for f in ("identifier", "title", "year", "item_size", "downloads")]
    url = f"{ENDPOINT}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "scripted-schedules/scout"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.load(fh)["response"]


def gigabytes(n) -> float:
    return (n or 0) / 1e9


def report(name: str, gap: dict, rows: int, sort: str) -> None:
    try:
        resp = search(gap["q"], rows, sort)
    except (urllib.error.URLError, ValueError, KeyError) as e:
        print(f"\n## {name}\n  query failed: {e}")
        return

    docs = resp["docs"]
    print(f"\n## {name} — {gap['why']}")
    print(f"   {resp['numFound']} items match; showing {len(docs)} by {sort}")
    if not docs:
        return
    print(f"   {'size':>8}  {'dls':>7}  {'yr':>4}  identifier")
    for d in docs:
        title = str(d.get("title", ""))[:60]
        print(f"   {gigabytes(d.get('item_size')):7.2f}G  {d.get('downloads', 0):7}  "
              f"{str(d.get('year', '?'))[:4]:>4}  {d['identifier'][:48]}")
        print(f"   {'':>8}  {'':>7}  {'':>4}  {title}")


def plan(name: str, gap: dict, rows: int, sort: str) -> None:
    """Print the storage arithmetic for one gap.

    The yield estimate is deliberately crude -- 40 spots per hour of capture,
    at the 26.1h-to-3721-spot rate the staged reels actually produced -- because
    the point is the order of magnitude, not a forecast.
    """
    resp = search(gap["q"], rows, sort)
    docs = resp["docs"]
    total = sum(gigabytes(d.get("item_size")) for d in docs)
    # 3721 spots from 28.6h staged; spots average ~25s and land near 5 MB.
    est_hours = total / 7.0          # ~7 GB per hour at these archival bitrates
    est_spots = est_hours * 130      # the staged reels ran ~130 spots per hour
    print(f"\n## {name} — download plan for the top {len(docs)}")
    print(f"   source to fetch     {total:8.1f} GB")
    print(f"   estimated capture   {est_hours:8.1f} hours")
    print(f"   estimated spots     {est_spots:8.0f}")
    print(f"   kept after split    {est_spots * 0.005:8.1f} GB  (~5 MB per spot)")
    print(f"   reduction           {total / max(est_spots * 0.005, 0.001):8.0f}:1")
    print("\n   fetch one at a time, split it, delete the source:")
    for d in docs[:3]:
        print(f"     {DOWNLOAD}/{d['identifier']}/")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("gap", nargs="?", help=f"one of: {', '.join(GAPS)} (default: all)")
    ap.add_argument("--rows", type=int, default=8, help="results per gap")
    ap.add_argument("--sort", default="downloads desc",
                    help='"downloads desc" finds the well-known, "addeddate desc" the newest')
    ap.add_argument("--plan", action="store_true", help="print storage arithmetic instead")
    ap.add_argument("--query", help="run an arbitrary query instead of a named gap")
    args = ap.parse_args()

    if args.query:
        report("custom", {"why": "ad hoc", "q": args.query}, args.rows, args.sort)
        return

    if args.gap and args.gap not in GAPS:
        sys.exit(f"unknown gap {args.gap!r}; choose from {', '.join(GAPS)}")

    chosen = {args.gap: GAPS[args.gap]} if args.gap else GAPS
    for name, gap in chosen.items():
        if args.plan:
            plan(name, gap, args.rows, args.sort)
        else:
            report(name, gap, args.rows, args.sort)

    print("\nnothing was downloaded. archive.org items are plain HTTPS:")
    print(f"  {DOWNLOAD}/<identifier>/   lists an item's files")
    print("  prefer the *.ia.mp4 derivative; it is ~1/5 the item size and already SD.")


if __name__ == "__main__":
    main()
