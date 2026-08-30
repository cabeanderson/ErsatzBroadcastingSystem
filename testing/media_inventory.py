#!/usr/bin/env python3
"""
Media Inventory

Writes a single reference document listing every content key the framework
knows about: what it queries, which collections list it, and which channels
actually air it.

Generated rather than hand-maintained, because the registry is 700 lines across
a dozen dicts and any handwritten copy of it is wrong within a week.

Usage:
    python3 -m scripts.testing.media_inventory              # -> scripts/reference/
    python3 -m scripts.testing.media_inventory --days 30
    python3 -m scripts.testing.media_inventory --out /tmp/inventory.md
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import install_mocks

install_mocks()

from scripts.testing.collision_report import (
    collect_airings, collection_membership, discover_channels,
    library_collections, query_for,
)
from scripts.library import sources

# The registry is assembled from these, and which one a key came from is the
# only record of what it is *for*. MASTER_SOURCES flattens that away.
REGISTRY_GROUPS = [
    ("Film", "MOVIE_REGISTRY"),
    ("Playlists", "PLAYLIST_REGISTRY"),
    ("Television", "TV_REGISTRY"),
    ("Animation", "ANIMATED_REGISTRY"),
    ("Nickelodeon", "NICK_REGISTRY"),
    ("Disney", "DISNEY_REGISTRY"),
    ("Cartoon Network", "CARTOON_NETWORK_REGISTRY"),
    ("Themed & Holiday", "THEME_REGISTRY"),
    ("Marathons", "MARATHONS"),
    ("Seasonal Variants", "SEASONAL_VARIANTS"),
    ("Fillers & Bumpers", "FILLERS"),
    ("Test", "TEST_REGISTRY"),
]


def describe(entry):
    """One-line rendering of a registry value."""
    if isinstance(entry, dict):
        query = entry.get("query")
        if query:
            return query
        # Playlist references carry no query at all.
        parts = [f"{k}={v}" for k, v in entry.items() if v is not None]
        return "playlist: " + ", ".join(parts)
    return str(entry)


def build(days, start):
    channels = discover_channels()
    airings = collect_airings(channels, start, days)

    aired_by = defaultdict(set)
    hours = defaultdict(float)
    for a in airings:
        aired_by[a["base"]].add(a["channel"])
        hours[a["base"]] += (a["end"] - a["start"]).total_seconds() / 3600

    membership = collection_membership(library_collections())
    return channels, aired_by, hours, membership


def render(channels, aired_by, hours, membership, days, start):
    out = []
    w = out.append

    w("# Registry Inventory")
    w("")
    w(f"Generated {datetime.now():%Y-%m-%d} by "
      "`python3 -m scripts.testing.media_inventory`. Do not edit by hand.")
    w("")
    w(f"Airtime columns reflect a **{days}-day simulation from "
      f"{start:%Y-%m-%d}** across {len(channels)} channels. A key with no "
      "airtime is not necessarily unused -- holiday and seasonal pools only "
      "surface inside their window.")
    w("")

    total = sum(len(getattr(sources, name, {})) for _, name in REGISTRY_GROUPS)
    claimed = sum(1 for k in aired_by if k)
    w(f"**{total} keys** in the registry. **{claimed}** aired in this window.")
    w("")

    # Contents
    w("## Contents")
    w("")
    for label, name in REGISTRY_GROUPS:
        registry = getattr(sources, name, {})
        if registry:
            anchor = label.lower().replace(" & ", "--").replace(" ", "-")
            w(f"- [{label}](#{anchor}) — {len(registry)} keys")
    w("")

    for label, name in REGISTRY_GROUPS:
        registry = getattr(sources, name, {})
        if not registry:
            continue

        w(f"## {label}")
        w("")
        w("| Key | On air | Hours | Collections | Query |")
        w("|---|---|---|---|---|")

        for key in sorted(registry):
            on_air = ", ".join(sorted(aired_by.get(key, []))) or "—"
            airtime = f"{hours[key]:.0f}h" if hours.get(key) else "—"
            collections = ", ".join(sorted(membership.get(key, []))) or "—"
            # Pipes and newlines would break the table; queries contain neither
            # today, but a future one easily could.
            query = describe(registry[key]).replace("|", "\\|").replace("\n", " ")
            w(f"| `{key}` | {on_air} | {airtime} | {collections} | `{query}` |")
        w("")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate the media inventory.")
    parser.add_argument("--out", default="scripts/reference/registry-inventory.md")
    parser.add_argument("--days", type=int, default=28,
                        help="Simulation window, in days (default: 28)")
    parser.add_argument("--date", help="Start date YYYY-MM-DD (default: Jan 1)")
    args = parser.parse_args()

    # A four-week window from January misses Halloween and Christmas entirely.
    # Start at the top of the year and run long enough to cross a season edge;
    # the header says plainly what the window was, so nobody reads an unaired
    # holiday pool as dead content.
    start = datetime(datetime.now().year, 1, 1)
    if args.date:
        start = datetime.strptime(args.date, "%Y-%m-%d")

    channels, aired_by, hours, membership = build(args.days, start)
    text = render(channels, aired_by, hours, membership, args.days, start)

    with open(args.out, "w") as handle:
        handle.write(text)

    print(f"Wrote {args.out} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
