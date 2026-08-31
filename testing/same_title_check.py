#!/usr/bin/env python3
"""
Same-Title Simultaneity Check

The collision report answers "are two channels airing the same *kind* of thing
at once". This answers the stricter and more literal question the lineup's
actual rule asks: **can the same title be on two channels in the same hour?**

The difference matters. The report's SAME GENRE tier flags Cabes Classic
Cinema's `classic_crime_movie` against Mystery Theatre's `modern_crime_movie`
every night, which looks alarming and is harmless -- the two keys were split at
1980 precisely so neither channel can draw the other's film. Genre equality is
a proxy; title-set intersection is the thing itself.

Method: simulate every channel, take each pair of overlapping film airings on
different channels, resolve both keys' Lucene queries against
`reference/library-movies.tsv`, and intersect the resulting title sets. A pair
whose sets are disjoint cannot collide no matter how similar the keys look.

The evaluator understands the clauses this library's film keys are actually
built from -- type, genre, release_date, minutes, title -- and reports any key
it cannot fully evaluate rather than guessing. `tag:`, `studio:` and
`content_rating:` are not in the TSV, so a key using them is scored on the
clauses that *are* checkable, which makes the title set a superset of the truth
and the check conservative: it can over-report a collision, never miss one.

Usage:
    python -m scripts.testing.same_title_check
    python -m scripts.testing.same_title_check --days 30
"""

import argparse
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import install_mocks

install_mocks()

from scripts.testing.collision_report import (
    discover_channels, collect_airings, is_movie_key, query_for, base_key,
)
# One resolver, shared. `key_census` owns it because "what does this key
# actually select" is its whole subject; this check is one consumer of the
# answer. Both therefore agree by construction about what a key contains.
from scripts.testing.key_census import evaluate, load_films


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--start", default=None)
    args = ap.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else datetime.now()
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    films = load_films()
    channels = discover_channels()

    print("=" * 78)
    print("SAME-TITLE SIMULTANEITY CHECK")
    print("=" * 78)
    print(f"  Window   : {start.date()} + {args.days} day(s)")
    print(f"  Channels : {', '.join(sorted(channels))}")
    print(f"  Films    : {len(films)} with a parseable year")

    airings = [a for a in collect_airings(channels, start, args.days) if is_movie_key(a["key"])]
    print(f"  Film airings: {len(airings)}")

    # Resolve every film key once.
    title_sets, partial = {}, {}
    for a in airings:
        key = base_key(a["key"])
        if key in title_sets:
            continue
        selected, unchecked = evaluate(query_for(key), films)
        # Identity is (title, year), not title. The library holds Father of the
        # Bride 1950 and 1991, and The Parent Trap 1961 and 1998 -- distinct
        # films sharing a title string. Keying on the string alone reported
        # Cabes Classic Cinema and Be Kind Rewind as colliding on remakes
        # neither one can draw.
        title_sets[key] = {(f["title"], f["year"]) for f in selected}
        if unchecked:
            partial[key] = unchecked

    # Pairwise overlap in wall-clock time, different channels.
    airings.sort(key=lambda a: a["start"])
    collisions = defaultdict(list)
    for i, a in enumerate(airings):
        for b in airings[i + 1:]:
            if b["start"] >= a["end"]:
                break
            if a["channel"] == b["channel"]:
                continue
            ka, kb = base_key(a["key"]), base_key(b["key"])
            sa, sb = title_sets.get(ka), title_sets.get(kb)
            if not sa or not sb:
                continue
            shared = sa & sb
            if shared:
                pair = tuple(sorted([(a["channel"], ka), (b["channel"], kb)]))
                exact = ka not in partial and kb not in partial
                collisions[pair].append((max(a["start"], b["start"]), shared, exact))

    confirmed = {p: h for p, h in collisions.items() if h[0][2]}
    possible = {p: h for p, h in collisions.items() if not h[0][2]}

    def render(title, group, note=None):
        print()
        print("-" * 78)
        print(title)
        print("-" * 78)
        if note:
            print(note)
        if not group:
            print("  None.")
            return
        for pair, hits in sorted(group.items(), key=lambda kv: -len(kv[1])):
            (ch_a, key_a), (ch_b, key_b) = pair
            shared = hits[0][1]
            print(f"  x{len(hits):<4} {ch_a} {key_a}")
            print(f"        {ch_b} {key_b}")
            print(f"        {len(shared)} shared title(s): "
                  f"{', '.join(f'{t} ({y})' for t, y in sorted(shared)[:6])}"
                  f"{' ...' if len(shared) > 6 else ''}")
            for when, _, _ in hits[:3]:
                print(f"          {when:%a %d %b %H:%M}")
            print()

    render("CONFIRMED -- both keys fully evaluable, title sets intersect",
           confirmed,
           "  These are real. The same film can air on both channels at once.")
    render("POSSIBLE -- at least one key has a clause the TSV cannot check",
           possible,
           "  A tag/studio/rating clause was dropped, so the title set is a\n"
           "  superset and most of these are artefacts of that. Read the shared\n"
           "  titles and judge; do not treat the count as a defect list.")

    if partial:
        print("-" * 78)
        print("KEYS SCORED ON A SUBSET OF THEIR CLAUSES")
        print("-" * 78)
        print("  The TSV has no tag, studio or rating column. These keys were")
        print("  evaluated on their checkable clauses only, so their title sets")
        print("  are supersets -- the check over-reports rather than misses.")
        for key, clauses in sorted(partial.items()):
            print(f"    {key}: {', '.join(clauses)}")

    print()
    print("=" * 78)
    print(f"  {len(confirmed)} confirmed, {len(possible)} possible")
    print("=" * 78)
    return 1 if confirmed else 0


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    sys.exit(main())
