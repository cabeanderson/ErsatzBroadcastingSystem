#!/usr/bin/env python3
"""
Cross-Channel Collision Report

Answers the question the per-channel tools cannot: what does the *lineup* look
like? `visualize_week` and `simulator` each look at one channel in isolation, so
a key claimed by two channels -- or two channels airing the same film pool in
the same hour -- is invisible to both.

Four things get reported, in increasing order of subtlety:

  1. SHARED CLAIMS    -- one content key, or one library collection, claimed by
                         several channels. The ownership question.
  2. SIMULTANEOUS     -- two channels airing the same films, or merely the same
                         *kind* of thing, in overlapping wall-clock time. A
                         viewer flipping between them sees one channel twice.
  3. POOL OVERLAP     -- *different* keys whose Lucene queries are equal or
                         subset-related, so they draw the same films under two
                         names. This is the one nothing else can see.
  4. UNCLAIMED        -- registry keys no channel airs. The free pool.

Sections 1 and 2 are simulated (they depend on the calendar, so a date range
matters). Sections 3 and 4 are static -- they read the registry and the
simulated key usage, and do not change with the date.

On tiers in section 2: exact-key equality is far too strict to be useful here.
Two channels can both hand their Saturday prime to SCI_FI_SHOWCASE and still
never collide on a key, because each draws a different arm of the collection.
Nothing is shared, and yet both channels run sci-fi features all evening. The
SAME GENRE tier exists to catch precisely that.

Usage:
    python -m scripts.testing.collision_report
    python -m scripts.testing.collision_report --days 14 --movies-only
    python -m scripts.testing.collision_report --channel scifi
"""

import argparse
import importlib
import logging
import os
import pkgutil
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import install_mocks, ChannelSimulator

install_mocks()

from scripts.library.sources import MASTER_SOURCES

# Placeholder channels -- their keys are illustrative, not library content, so
# every one of them would show up as a false collision.
SKIP_CHANNELS = {"example_channel", "test_channel"}

# Tag injection registers a narrowed copy of a key as `<base>_auto_<label>`
# (queries.py:inject_tag_query). The narrowed pool is a subset of the base pool,
# so for collision purposes the two are the same claim on the same films.
AUTO_SUFFIX = re.compile(r"_auto_[a-z0-9_]+$")

# factories.annual_show mints `__auto_<title>_s<n>` for appointment shows. That
# is a whole key, not a narrowed one, and it matches AUTO_SUFFIX -- stripping it
# left every appointment show on every channel sharing the base key "_", which
# is a collision the report would have invented out of nothing.
FACTORY_PREFIX = "__auto_"


def base_key(key):
    """Strip a tag-injection suffix back to the key that was narrowed."""
    if not isinstance(key, str) or key.startswith(FACTORY_PREFIX):
        return key
    return AUTO_SUFFIX.sub("", key)


# ==============================================================================
# DISCOVERY
# ==============================================================================

def discover_channels():
    """Find channel modules the same way visualize_week does -- by import, not
    by a hardcoded list, which is how british and eighties stayed invisible to
    the older tooling for as long as they did."""
    import scripts.channels as channels_pkg

    found = {}
    for mod in pkgutil.iter_modules(channels_pkg.__path__):
        if mod.name.startswith("_") or mod.name in SKIP_CHANNELS:
            continue
        module = importlib.import_module(f"scripts.channels.{mod.name}")
        if hasattr(module, "build_playout"):
            found[mod.name] = module
    return found


# ==============================================================================
# SIMULATION
# ==============================================================================

def collect_airings(channels, start_date, days):
    """Simulate every channel across the window.

    Returns a list of airing dicts: channel, key (as aired), base, start, end.
    """
    airings = []

    # Channel loggers write to stdout *and* to logs/<channel>.log. A report that
    # simulates nine channels over a fortnight would append tens of megabytes of
    # noise to the real log files and bury its own output, so silence logging
    # for the duration rather than trying to suppress it per channel.
    logging.disable(logging.CRITICAL)
    try:
        for name, module in channels.items():
            sim = ChannelSimulator(module)
            for offset in range(days):
                day = start_date + timedelta(days=offset)
                for entry in sim.simulate_day(day, hours=24):
                    if entry.get("type") != "content":
                        continue
                    key = entry["content"]
                    if not isinstance(key, str):
                        continue
                    start = entry["time"]
                    duration = entry.get("duration") or 0
                    airings.append({
                        "channel": name,
                        "key": key,
                        "base": base_key(key),
                        "start": start,
                        "end": start + timedelta(minutes=duration),
                    })
    finally:
        logging.disable(logging.NOTSET)

    return airings


# ==============================================================================
# QUERY ANALYSIS
# ==============================================================================

def split_clauses(query):
    """Split a Lucene query into its top-level AND clauses.

    Every query in the library is built by queries.py's `*_source` helpers, which
    join their parts with ' AND ' and parenthesise anything compound. Splitting
    on top-level ' AND ' therefore recovers exactly the constraint set that built
    the key, which is what makes subset comparison meaningful rather than a
    string-similarity guess.
    """
    if not isinstance(query, str):
        return frozenset()

    clauses, depth, current = [], 0, []
    tokens = re.split(r"(\s+AND\s+|\(|\))", query)
    for token in tokens:
        if token == "(":
            depth += 1
            current.append(token)
        elif token == ")":
            depth -= 1
            current.append(token)
        elif re.fullmatch(r"\s+AND\s+", token or "") and depth == 0:
            clauses.append("".join(current).strip())
            current = []
        else:
            current.append(token)
    clauses.append("".join(current).strip())

    return frozenset(c for c in clauses if c)


def query_for(key):
    """The registered Lucene query for a key, or None for playlists/unknowns."""
    entry = MASTER_SOURCES.get(base_key(key))
    if isinstance(entry, dict):
        return entry.get("query")
    return entry if isinstance(entry, str) else None


def is_movie_key(key):
    query = query_for(key)
    return bool(query and "type:movie" in query)


def pair_marker(key_a, key_b):
    """FILM when both keys are film pools, MIX when one is, tv when neither."""
    films = is_movie_key(key_a) + is_movie_key(key_b)
    return {2: "FILM", 1: "MIX ", 0: "tv  "}[films]


def relate(clauses_a, clauses_b):
    """How two clause sets relate: 'identical', 'subset', 'superset', or None.

    Only these three relations are reported. Partial overlap ('both are movies')
    is true of most of the registry and would drown the signal.
    """
    if not clauses_a or not clauses_b:
        return None
    if clauses_a == clauses_b:
        return "identical"
    if clauses_a < clauses_b:
        return "superset"   # a is broader: b's films are a subset of a's
    if clauses_b < clauses_a:
        return "subset"
    return None


# A clause is "generic" when nearly every key in the registry carries it, so two
# keys sharing it says nothing. Everything else -- a genre, a tag, a studio --
# is a signature: it describes what the programming *is*.
GENERIC_CLAUSE = re.compile(
    r"^(NOT\s+)?(type:|release_date:|minutes:|content_rating:|genre:animation$)"
)


def signature_clauses(clauses):
    """The clauses that characterise a pool, minus the boilerplate."""
    return frozenset(
        c for c in clauses
        if not GENERIC_CLAUSE.match(c) and not c.startswith("NOT ")
    )


# ==============================================================================
# COLLECTION OWNERSHIP
# ==============================================================================
#
# Keys are the wrong altitude for one important case. When two channels both
# reference `movies.SCI_FI_SHOWCASE`, they have not merely picked overlapping
# keys -- they have handed the same object to two schedules. That is a single
# editorial decision showing up in two places, and it is worth naming as such.

# Container types the schedules are built out of. Walking these by hand rather
# than by generic reflection keeps the traversal predictable; a stray __dict__
# crawl wanders into loggers, modules and mock API objects.
_COLLECTION_ATTRS = ("items", "base", "seasonal", "content", "collection",
                     "primary", "secondary", "filler")

# Populated by library_collections(); keeps each named collection alive so its
# id() stays unique for the life of the report.
_OBJECTS_BY_ID = {}


def library_collections():
    """Map id(obj) -> 'module.NAME' for every named collection in the library."""
    import scripts.library as library_pkg

    named = {}
    for mod_name in getattr(library_pkg, "__all__", []):
        module = getattr(library_pkg, mod_name, None)
        if module is None:
            continue
        for var_name, value in vars(module).items():
            if not var_name.isupper() or var_name.startswith("_"):
                continue
            # Registries are dicts of queries, not schedulable collections.
            if isinstance(value, (str, int, float, bool, dict, type(None))):
                continue
            named[id(value)] = f"{mod_name}.{var_name}"
            # id() alone cannot get the object back, and holding a reference
            # also pins it so no later allocation reuses the id.
            _OBJECTS_BY_ID[id(value)] = value
    return named


def collection_membership(named):
    """Map content key -> the named collections that list it.

    Query analysis cannot see that `cyberpunk_movie` and `modern_scifi_movie`
    are the same kind of programming -- one is a tag, the other a genre, and the
    clause sets are disjoint. Membership can: both are arms of SCI_FI_SHOWCASE,
    which is an editorial statement that they are interchangeable.
    """
    membership = defaultdict(set)
    seen = set()

    def walk(node, collection_name):
        if id(node) in seen:
            return
        seen.add(id(node))

        if isinstance(node, str):
            membership[node].add(collection_name)
            return
        if isinstance(node, (int, float, bool, type(None))):
            return
        if isinstance(node, dict):
            for value in node.values():
                walk(value, collection_name)
            return
        if isinstance(node, (list, tuple, set, frozenset)):
            for value in node:
                walk(value, collection_name)
            return
        for attr in _COLLECTION_ATTRS:
            if hasattr(node, attr):
                walk(getattr(node, attr), collection_name)

    for obj_id, name in named.items():
        seen.clear()
        obj = _OBJECTS_BY_ID.get(obj_id)
        if obj is not None:
            walk(obj, name)
    return membership


def referenced_collections(module, named):
    """Every named library collection reachable from a channel's schedules."""
    found, seen = set(), set()

    def walk(node):
        if id(node) in seen:
            return
        seen.add(id(node))

        if id(node) in named:
            found.add(named[id(node)])

        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, (list, tuple, set, frozenset)):
            for value in node:
                walk(value)
        elif not isinstance(node, (str, int, float, bool, type(None))):
            for attr in _COLLECTION_ATTRS:
                if hasattr(node, attr):
                    walk(getattr(node, attr))

    for var_name, value in vars(module).items():
        if var_name.isupper() and not var_name.startswith("_"):
            walk(value)
    return found


# ==============================================================================
# SECTIONS
# ==============================================================================

def section_shared_keys(airings, focus=None):
    """Keys claimed by more than one channel."""
    usage = defaultdict(lambda: defaultdict(int))
    for a in airings:
        usage[a["base"]][a["channel"]] += 1

    shared = {k: v for k, v in usage.items() if len(v) > 1}
    if focus:
        shared = {k: v for k, v in shared.items() if focus in v}

    print("\n" + "=" * 78)
    print("1. SHARED KEYS -- one pool, several channels")
    print("=" * 78)

    if not shared:
        print("  None. Every key has exactly one channel claiming it.")
        return shared

    for key in sorted(shared, key=lambda k: (not is_movie_key(k), k)):
        marker = "FILM" if is_movie_key(key) else "tv  "
        owners = shared[key]
        breakdown = ", ".join(
            f"{ch} ({n})" for ch, n in sorted(owners.items(), key=lambda x: -x[1])
        )
        print(f"  [{marker}] {key}")
        print(f"         {breakdown}")

    print(f"\n  {len(shared)} shared key(s); "
          f"{sum(1 for k in shared if is_movie_key(k))} of them film pools.")
    return shared


def section_shared_collections(channels, focus=None):
    """Library collections handed to more than one channel's schedule."""
    named = library_collections()

    owners = defaultdict(set)
    for name, module in channels.items():
        for collection in referenced_collections(module, named):
            owners[collection].add(name)

    shared = {c: chans for c, chans in owners.items() if len(chans) > 1}
    if focus:
        shared = {c: chans for c, chans in shared.items() if focus in chans}

    print("\n" + "-" * 78)
    print("1b. SHARED COLLECTIONS -- one library object, several schedules")
    print("-" * 78)

    if not shared:
        print("  None. No collection is referenced by two channels.")
        return shared

    for collection in sorted(shared):
        print(f"  {collection}")
        print(f"         {', '.join(sorted(shared[collection]))}")

    print(f"\n  {len(shared)} shared collection(s).")
    return shared


def section_simultaneous(airings, focus=None):
    """Two channels programming the same thing at the same time.

    Reported in three tiers, strongest first:

      SAME POOL       the same films can literally appear on both channels
      SAME COLLECTION different keys, but both are arms of one library
                      collection -- the library already calls them equivalent
      SAME GENRE      the queries share a genre, tag or studio clause

    The lower two tiers are the ones that shape a lineup. Two channels never
    airing the same file can still be the same channel twice over.
    """
    print("\n" + "=" * 78)
    print("2. SIMULTANEOUS AIRINGS -- same hour, different channel")
    print("=" * 78)

    # Precompute per-key query facts once; the overlap scan is quadratic in
    # airings-per-hour and re-splitting queries inside it is pure waste.
    keys = {a["base"] for a in airings}
    clauses = {k: split_clauses(query_for(k)) for k in keys}
    signatures = {k: signature_clauses(clauses[k]) for k in keys}
    membership = collection_membership(library_collections())

    ordered = sorted(airings, key=lambda a: a["start"])

    clashes = []
    for i, first in enumerate(ordered):
        for second in ordered[i + 1:]:
            if second["start"] >= first["end"]:
                break  # sorted by start: nothing later can overlap this one
            if first["channel"] == second["channel"]:
                continue
            if focus and focus not in (first["channel"], second["channel"]):
                continue

            key_a, key_b = first["base"], second["base"]
            shared_collections = membership[key_a] & membership[key_b]
            if key_a == key_b or relate(clauses[key_a], clauses[key_b]):
                tier = "SAME POOL"
            elif shared_collections:
                tier = "SAME COLLECTION"
            elif signatures[key_a] & signatures[key_b]:
                tier = "SAME GENRE"
            else:
                continue

            clashes.append((tier, key_a, key_b, first, second, shared_collections))

    if not clashes:
        print("  None. No two channels program the same thing at once.")
        return clashes

    # Individual airings are noisy -- the same Saturday-night pairing recurs
    # every week and would print seven times. Collapse to the distinct pairing
    # and report how often and when it happens.
    grouped = defaultdict(list)
    via = {}
    for tier, key_a, key_b, first, second, shared_collections in clashes:
        pairing = tuple(sorted([(first["channel"], key_a), (second["channel"], key_b)]))
        grouped[(tier, pairing)].append((first, second))
        via[(tier, pairing)] = shared_collections

    tier_order = {"SAME POOL": 0, "SAME COLLECTION": 1, "SAME GENRE": 2}
    for (tier, pairing), instances in sorted(
            grouped.items(),
            key=lambda g: (tier_order[g[0][0]], -len(g[1]), g[0][1])):
        (chan_a, key_a), (chan_b, key_b) = pairing
        marker = pair_marker(key_a, key_b)

        print(f"  [{tier:<15}] [{marker}] x{len(instances)}")
        print(f"       {chan_a:<16} {key_a}")
        print(f"       {chan_b:<16} {key_b}")
        shared_collections = via[(tier, pairing)]
        if shared_collections:
            print(f"       via {', '.join(sorted(shared_collections))}")

        # A few concrete times, so the finding is checkable against the
        # visualiser rather than merely asserted.
        for first, second in instances[:3]:
            overlap_start = max(first["start"], second["start"])
            overlap_end = min(first["end"], second["end"])
            minutes = int((overlap_end - overlap_start).total_seconds() // 60)
            print(f"         {overlap_start:%a %d %b %H:%M}"
                  f"-{overlap_end:%H:%M} ({minutes}m)")
        if len(instances) > 3:
            print(f"         ... and {len(instances) - 3} more")

    film_clashes = sum(1 for c in clashes if is_movie_key(c[1]) and is_movie_key(c[2]))
    print(f"\n  {len(grouped)} distinct pairing(s) over {len(clashes)} airing(s); "
          f"{film_clashes} airing(s) film-on-film.")
    return clashes


def section_pool_overlap(airings, focus=None, movies_only=False):
    """Distinct keys on different channels that draw from the same films."""
    print("\n" + "=" * 78)
    print("3. POOL OVERLAP -- different keys, overlapping film sets")
    print("=" * 78)

    channels_by_key = defaultdict(set)
    for a in airings:
        channels_by_key[a["base"]].add(a["channel"])

    keys = [k for k in channels_by_key if query_for(k)]
    if movies_only:
        keys = [k for k in keys if is_movie_key(k)]
    keys.sort()

    clauses = {k: split_clauses(query_for(k)) for k in keys}

    findings = []
    for i, key_a in enumerate(keys):
        for key_b in keys[i + 1:]:
            # Same channel owning both is a deliberate variety choice, not a
            # collision. Only cross-channel overlap is a lineup problem.
            shared_channels = channels_by_key[key_a] & channels_by_key[key_b]
            cross = channels_by_key[key_a] != channels_by_key[key_b] or not shared_channels
            if not cross:
                continue
            if focus and focus not in (channels_by_key[key_a] | channels_by_key[key_b]):
                continue

            relation = relate(clauses[key_a], clauses[key_b])
            if not relation:
                continue
            findings.append((relation, key_a, key_b,
                             channels_by_key[key_a], channels_by_key[key_b]))

    if not findings:
        print("  None. No two keys across channels resolve to overlapping sets.")
        return findings

    order = {"identical": 0, "superset": 1, "subset": 2}
    findings.sort(key=lambda f: (order[f[0]], f[1]))

    for relation, key_a, key_b, chans_a, chans_b in findings:
        a_on = ", ".join(sorted(chans_a))
        b_on = ", ".join(sorted(chans_b))
        if relation == "identical":
            print(f"  [IDENTICAL] {key_a}  ==  {key_b}")
        elif relation == "superset":
            print(f"  [CONTAINS ] {key_a}  >  {key_b}")
        else:
            print(f"  [CONTAINS ] {key_b}  >  {key_a}")
        print(f"              {key_a} on {a_on}  |  {key_b} on {b_on}")

    print(f"\n  {len(findings)} overlapping pair(s).")
    return findings


def section_unclaimed(airings, movies_only=False):
    """Registry keys nothing airs -- the pool still available to a new channel."""
    print("\n" + "=" * 78)
    print("4. UNCLAIMED KEYS -- in the registry, on no channel")
    print("=" * 78)
    print("  Window-dependent: holiday and seasonal keys read as unclaimed")
    print("  outside their season. Re-run over October or December before")
    print("  concluding a christmas_* or halloween_* pool is genuinely free.")

    aired = {a["base"] for a in airings}
    candidates = [k for k in MASTER_SOURCES if k not in aired]
    if movies_only:
        candidates = [k for k in candidates if is_movie_key(k)]
    candidates.sort()

    if not candidates:
        print("  None. Every registry key is claimed.")
        return candidates

    film = [k for k in candidates if is_movie_key(k)]
    other = [k for k in candidates if k not in set(film)]

    if film:
        print(f"\n  Film pools ({len(film)}):")
        for key in film:
            print(f"    {key}")
    if other and not movies_only:
        print(f"\n  Other ({len(other)}):")
        for key in other:
            print(f"    {key}")

    print(f"\n  {len(candidates)} unclaimed key(s); {len(film)} of them film pools.")
    return candidates


def section_summary(channels, airings):
    """Per-channel film footprint -- which channels are in the movie business."""
    print("\n" + "=" * 78)
    print("SUMMARY -- film footprint by channel")
    print("=" * 78)

    film_keys = defaultdict(set)
    film_hours = defaultdict(float)
    for a in airings:
        if is_movie_key(a["base"]):
            film_keys[a["channel"]].add(a["base"])
            film_hours[a["channel"]] += (a["end"] - a["start"]).total_seconds() / 3600

    print(f"  {'channel':<18} {'film keys':>10} {'film hours':>12}")
    print(f"  {'-'*18} {'-'*10:>10} {'-'*12:>12}")
    for name in sorted(channels):
        print(f"  {name:<18} {len(film_keys[name]):>10} {film_hours[name]:>11.1f}h")


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cross-channel collision report for the lineup.")
    parser.add_argument("--date", help="Start date YYYY-MM-DD (default: today)")
    parser.add_argument("--days", type=int, default=7,
                        help="Days to simulate (default: 7)")
    parser.add_argument("--channel",
                        help="Only report collisions involving this channel")
    parser.add_argument("--movies-only", action="store_true",
                        help="Restrict sections 3 and 4 to film pools")
    parser.add_argument("--section", type=int, choices=[1, 2, 3, 4],
                        help="Print only one section")
    args = parser.parse_args()

    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if args.date:
        start = datetime.strptime(args.date, "%Y-%m-%d")

    channels = discover_channels()
    if args.channel and args.channel not in channels:
        print(f"Unknown channel: {args.channel}")
        print(f"Available: {', '.join(sorted(channels))}")
        return 1

    print("=" * 78)
    print("CROSS-CHANNEL COLLISION REPORT")
    print("=" * 78)
    print(f"  Window   : {start:%Y-%m-%d} + {args.days} day(s)")
    print(f"  Channels : {', '.join(sorted(channels))}")
    if args.channel:
        print(f"  Focus    : {args.channel}")

    airings = collect_airings(channels, start, args.days)
    print(f"  Airings  : {len(airings)}")

    if args.section in (None, 1):
        section_shared_keys(airings, focus=args.channel)
        section_shared_collections(channels, focus=args.channel)
    if args.section in (None, 2):
        section_simultaneous(airings, focus=args.channel)
    if args.section in (None, 3):
        section_pool_overlap(airings, focus=args.channel,
                             movies_only=args.movies_only)
    if args.section in (None, 4):
        section_unclaimed(airings, movies_only=args.movies_only)
    if args.section is None:
        section_summary(channels, airings)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
