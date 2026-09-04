"""
Same title, same moment, two channels -- C1 asked literally, for television.

`collision_report` groups airings by content-key *name*, so it can only see a
collision when two channels schedule the *same key*. That makes it structurally
blind to the most common real case: one show reached through two different keys.
Cartoon Network's Toonami schedules One Piece as an inline `{"title": "One
Piece"}` item; Japanorama schedules it as `one_piece_syndication_tv`. To
`collision_report` those are unrelated pools, and the 574 episodes underneath
them are invisible.

`same_title_check` answers the question properly for *keys* -- it resolves two
Lucene queries and intersects their title sets -- but it compares registry keys
against each other rather than against the clock, so it cannot tell a shared
pool that is carefully scheduled apart from one that is not.

This tool closes the gap. It simulates every channel, resolves each scheduled
key down to the actual library titles it can put on screen, and intersects those
sets wherever two channels' airings overlap in time. What comes out is the
number C1 is actually about: how many times a viewer could find the same show on
two channels at once.

It was written to verify Japanorama, which shares roughly 2,450 episodes with
Cartoon Network under an hours rule, and it found two real defects on its first
run -- a syndication wheel in an overnight vault sitting opposite Toonami's
Midnight Run, and Laid-Back Camp the Movie reaching Be Kind Rewind through a
`NOT genre:animation` clause that the library's `Anime` tag walks straight past.

Usage:
    python3 -m scripts.testing.same_show_check                  # all channels, 30 days
    python3 -m scripts.testing.same_show_check --days 60
    python3 -m scripts.testing.same_show_check --channel japanorama
    python3 -m scripts.testing.same_show_check --all            # artifacts too

READING THE RESULT. Keys carrying a clause the manifests cannot answer --
`studio:`, `tag:`, `content_rating:` -- resolve to a *superset* of their real
pool, exactly as they do in `same_title_check`'s POSSIBLE section. A hit that
depends on one of those is reported as an ARTIFACT and excluded from the total,
because `studio:Pixar` scored on its checkable clauses alone means "every
animated film". Only CONFIRMED hits are defects.
"""

import argparse
import collections
import contextlib
import importlib
import io
import re
from datetime import datetime, timedelta

from scripts.testing import key_census as kc
from scripts.library.sources import MASTER_SOURCES

# Every channel with a module in scripts/channels, minus the harness fixtures.
CHANNELS = [
    "be_kind_rewind", "british", "cartoon_network", "classic_movies", "corncob",
    "detective", "disney", "eighties", "high_noon", "japanorama", "nick",
    "nightmare_theatre", "scifi", "sitcoms",
]

START = datetime(2026, 1, 1)
_FILMS, _SHOWS = None, None
_CACHE = {}


def _manifests():
    global _FILMS, _SHOWS
    if _FILMS is None:
        _FILMS, _SHOWS = kc.load_films(), kc.load_shows()
    return _FILMS, _SHOWS


def titles_for(key):
    """Every library title a scheduled key can put on screen, and whether it is exact.

    Returns (titles, exact). `exact` is False when the query carries a clause
    the manifests cannot score, which makes the title set a superset.
    """
    if not isinstance(key, str):
        return set(), True
    if key in _CACHE:
        return _CACHE[key]

    films, shows = _manifests()
    # Seasonal injection rewrites `frieren_tv` as `frieren_tv_auto_winter`.
    # Normalising this off is the same trap the Good Times hours-rule checker
    # hit: without it, a checker reports clean over airings it never inspected.
    base = re.sub(r"_auto_[a-z0-9_]+$", "", key)

    query = MASTER_SOURCES.get(base)
    if isinstance(query, dict):
        query = query.get("query")

    result = (set(), True)
    if isinstance(query, str):
        kind = kc.query_kind(query)
        if kind:
            records = films if kind == "movie" else shows
            selected, unchecked = kc.evaluate(query, records)
            result = ({r["title"] for r in selected}, not unchecked)
    else:
        # Appointment keys the factories generate: `__auto_blue_eye_samurai_s1`,
        # `auto_gen_agatha_christie_s_poirot_da84d2`. The show name is in the key.
        match = re.match(r"^_*auto_(?:gen_)?(.+?)(?:_s\d+)?(?:_[0-9a-f]{6})?$", base)
        if match:
            guess = kc._phrase(match.group(1).replace("_", " "))
            titles = {s["title"] for s in shows if guess in kc._phrase(s["title"])}
            titles |= {f["title"] for f in films if guess in kc._phrase(f["title"])}
            result = (titles, True)

    _CACHE[key] = result
    return result


def airings(channel):
    """(start, end, key) for every play, from one continuous simulation."""
    module = importlib.import_module(f"scripts.channels.{channel}")
    from scripts.testing.simulator import ChannelSimulator

    sim = ChannelSimulator(module)
    with contextlib.redirect_stdout(io.StringIO()):
        schedule = sim.simulate_day(START, hours=DAYS * 24)

    out = []
    for i, entry in enumerate(schedule):
        start = entry["time"]
        end = (schedule[i + 1]["time"] if i + 1 < len(schedule)
               else start + timedelta(minutes=30))
        out.append((start, end, str(entry["content"])))
    return out


def overlaps(a, b):
    """Pairs of airings from two channels whose airtime intersects."""
    b_sorted = sorted(b)
    j = 0
    for a_start, a_end, a_key in sorted(a):
        while j < len(b_sorted) and b_sorted[j][1] <= a_start:
            j += 1
        for b_start, b_end, b_key in b_sorted[j:]:
            if b_start >= a_end:
                break
            yield (max(a_start, b_start), a_key, b_key)


def main():
    ap = argparse.ArgumentParser(
        description="Same title on two channels at the same time -- C1, literally.")
    ap.add_argument("--days", type=int, default=30, help="days to simulate (default 30)")
    ap.add_argument("--channel", help="only pairs involving this channel")
    ap.add_argument("--all", action="store_true",
                    help="also list ARTIFACT hits (keys the manifests cannot fully score)")
    args = ap.parse_args()

    global DAYS
    DAYS = args.days

    names = CHANNELS
    if args.channel and args.channel not in names:
        ap.error(f"unknown channel {args.channel!r}; known: {', '.join(names)}")

    print("=" * 78)
    print("SAME-SHOW CHECK -- one title, two channels, overlapping airtime")
    print("=" * 78)
    print(f"  simulating {len(names)} channels over {DAYS} days from {START:%Y-%m-%d}\n")

    schedules = {}
    for name in names:
        try:
            schedules[name] = airings(name)
            print(f"  {name:<20} {len(schedules[name]):>6} plays")
        except Exception as exc:
            print(f"  {name:<20} SKIPPED ({type(exc).__name__}: {exc})")

    pairs = [(a, b) for i, a in enumerate(sorted(schedules))
             for b in sorted(schedules)[i + 1:]]
    if args.channel:
        pairs = [p for p in pairs if args.channel in p]

    confirmed = collections.defaultdict(collections.Counter)
    artifact = collections.defaultdict(collections.Counter)
    examples = {}

    for a, b in pairs:
        for when, ka, kb in overlaps(schedules[a], schedules[b]):
            ta, exact_a = titles_for(ka)
            if not ta:
                continue
            tb, exact_b = titles_for(kb)
            for title in ta & tb:
                bucket = confirmed if (exact_a and exact_b) else artifact
                bucket[(a, b)][title] += 1
                examples.setdefault((a, b, title),
                                    f"{when:%a %d %b %H:%M}  {a}:{ka}  {b}:{kb}")

    print("\n" + "-" * 78)
    print("CONFIRMED -- both keys fully evaluable, same title on air at once")
    print("-" * 78)
    total = 0
    for (a, b), titles in sorted(confirmed.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(titles.values())
        total += n
        print(f"  {a} / {b} -- {n} airing(s), {len(titles)} title(s)")
        for title, count in titles.most_common(10):
            print(f"      {count:>4}x  {title}")
            print(f"            {examples[(a, b, title)]}")
    if not confirmed:
        print("  none")

    art_total = sum(sum(t.values()) for t in artifact.values())
    print("\n" + "-" * 78)
    print(f"ARTIFACT -- at least one key has a clause the TSV cannot score ({art_total} airings)")
    print("-" * 78)
    if args.all:
        for (a, b), titles in sorted(artifact.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"  {a} / {b} -- {sum(titles.values())} airing(s)")
            for title, count in titles.most_common(6):
                print(f"      {count:>4}x  {title}")
                print(f"            {examples[(a, b, title)]}")
    else:
        for (a, b), titles in sorted(artifact.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"  {a} / {b} -- {sum(titles.values())} airing(s), "
                  f"{len(titles)} title(s)  (--all to list)")
        if not artifact:
            print("  none")
    print("\n  These are supersets, not findings: a `studio:` or `tag:` clause the")
    print("  manifests cannot answer is dropped, which widens the key rather than")
    print("  narrowing it. Same category as same_title_check's POSSIBLE section.")

    print("\n" + "=" * 78)
    print(f"  {total} confirmed simultaneous same-title airing(s) over {DAYS} days")
    print("=" * 78)
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
