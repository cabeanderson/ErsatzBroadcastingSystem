#!/usr/bin/env python3
"""
Unaired Configuration Check
===========================

Finds content a channel's configuration names and the channel can never play.

Why this exists: **this repo's characteristic failure is a schedule that is
wrong and looks right.** Four of them are on the record, and no test caught
any of the four --

  * `monthly_rotation` returned twelve slots and silently dropped a
    thirteenth item, so Be Kind Rewind ran eight directors while its module
    listed more.
  * A `("SEASON","DAY")` tuple resolved to no season windows at all, so an
    appointment scheduled nothing.
  * `frequency` paced an appointment without gating it, so a Friday show
    aired seven nights a week.
  * `_apply_schedule_looping` re-anchored on a raw day count, so 21 of 35
    annual appointments opened on episode 2.

Every one produced a plausible playout, a clean log and a passing suite. What
they share is not a mechanism -- it is that **the config named content that
never reached air**, and nothing compared the two lists. This does.

## Method

Simulate every channel across a long window, collect the content keys that
actually aired, and diff that against every content identity reachable from
the channel module's configuration. Anonymous `{title, query}` items are
identified by `_auto_gen_key`, the same function the resolver uses, so a named
film matches whether it aired as a key or as a generated one.

Findings are split by *why* something did not air, because the two cases
deserve very different attention:

  DEAD    every item under one branch of the config never aired. A branch is
          a path through the label dicts -- `PRIME_BLOCK[default][WEEKDAY]`.
          Nothing under it airing means the branch itself is unreachable,
          which is a defect in the configuration and the finding this tool
          exists for. Exits non-zero.

  THIN    some items under a branch aired and some did not. That is a random
          collection not getting round to everything in the window, which is
          ordinary, and it is reported only under --all.

## Where it sits among the others

    key_census        can the library satisfy this query?      manifests, offline
    validate_titles   does every scheduled title resolve?      manifests, offline
    collision_report  do two channels clash?                   simulation
    unaired_check     can the schedule reach this config?      simulation
    key_airing_check  did a reached key put anything on air?   live guide
    continuity_check  is there dead air?                       live guide

`key_airing_check` is the closest sibling and asks the opposite half of the
question. It takes the keys a channel *reaches* and asks whether the server
played them. This takes the config a channel *declares* and asks whether the
schedule reaches it. A branch can be perfectly healthy by every other measure
and simply never be selected.

## What this cannot see

**A window shorter than the content's own cycle reads as DEAD.** A three-year
spotlight checked over one year reports two thirds of itself missing. The
default window is three years for that reason, and the tool refuses to report
DEAD findings for a cycle longer than the window rather than crying wolf.

Seasonal and holiday branches need their season inside the window; three years
covers every one currently in the lineup. Marathon collections fire on
triggers and may legitimately not exhaust themselves -- they are reported, but
read them as THIN even when they come up DEAD.

This says nothing about whether the *server* can play what aired here.
`key_census` answers that question; this one is only about the config.

Usage:
    python3 -m scripts.testing.unaired_check
    python3 -m scripts.testing.unaired_check --days 400
    python3 -m scripts.testing.unaired_check disney
    python3 -m scripts.testing.unaired_check --all
"""

import argparse
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from scripts.testing.simulator import install_mocks, ChannelSimulator

install_mocks()

from scripts.testing.collision_report import discover_channels, base_key
from scripts.library.queries import show_by_title
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.models import ContentItem
from scripts.logic.resolution.resolver import _auto_gen_key

# The attributes a content container can hold its children under. Same list
# `collision_report` walks, and for the same reason: a Block, a Program, a
# Collection and a SeasonalBlock keep their contents in differently-named
# slots and there is no common base class to ask.
_CHILD_ATTRS = ("items", "content", "base", "seasonal", "collection", "reruns")

# Three years. Long enough for every cycle the lineup currently declares --
# the longest is Be Kind Rewind's three-year spotlight -- plus every season
# and holiday.
DEFAULT_DAYS = 1096

_YEAR_CYCLE = re.compile(r"^YEAR_OF_(\d+)_\d+$")


def declared(module):
    """Map content identity -> every config path that names it.

    The path is what makes a finding actionable: `PRIME_BLOCK[default][default]`
    says which branch to go and look at, where a bare content key would only
    say that something, somewhere, is not airing.

    **An identity is recorded under every path that declares it, not the first
    one walked.** Be Kind Rewind's spotlights share films -- Beetlejuice is
    Burton's and Keaton's, Jackie Brown is Tarantino's and Keaton's and De
    Niro's -- and attributing each film to one branch made the others look
    emptier than they are. Michael Keaton's month reported DEAD on that bug.
    """
    found, seen = defaultdict(set), set()

    def walk(node, path):
        if id(node) in seen:
            return
        seen.add(id(node))

        if isinstance(node, str):
            # Only registry keys. A bare string in a config is as likely to be
            # a block name or a query fragment as a content key.
            if node in MASTER_SOURCES:
                found[node].add(path)
            return

        if isinstance(node, ContentItem):
            query = node.query or show_by_title(node.title)
            found[_auto_gen_key(node.title, query)].add(path)
            return

        if isinstance(node, dict):
            # A {title, query} pair is a content definition, not a branch.
            if "title" in node:
                query = node.get("query") or show_by_title(node["title"])
                found[_auto_gen_key(node["title"], query)].add(path)
                return
            for key, value in node.items():
                walk(value, f"{path}[{key}]")
            return

        if isinstance(node, (list, tuple, set, frozenset)):
            for value in node:
                walk(value, path)
            return

        for attr in _CHILD_ATTRS:
            if hasattr(node, attr):
                walk(getattr(node, attr), path)

    for name, value in vars(module).items():
        if name.isupper() and not name.startswith("_"):
            walk(value, name)
    return found


def aired(module, start, days):
    """Every content key a channel actually plays across the window."""
    played = set()
    sim = ChannelSimulator(module)
    for offset in range(days):
        for entry in sim.simulate_day(start + timedelta(days=offset), hours=24):
            key = entry.get("content")
            if isinstance(key, str):
                # Injection rewrites `90s_pure_movie` to `90s_pure_movie_auto_fall`.
                played.add(base_key(key))
    return played


def longest_cycle(paths):
    """Longest declared year-cycle, in years, from the YEAR_OF_<n>_<r> paths."""
    longest = 1
    for path in paths:
        for token in re.findall(r"\[([^\]]+)\]", path):
            match = _YEAR_CYCLE.match(token)
            if match:
                longest = max(longest, int(match.group(1)))
    return longest


def classify(config, played):
    """Split a channel's never-aired declarations into DEAD and THIN branches.

    A branch is DEAD only when *nothing* it declares aired anywhere on the
    channel. That is deliberately conservative: a shared identity cannot be
    attributed to the branch that played it, so a branch whose every film also
    sits in some other spotlight can hide a genuine defect. The alternative --
    calling a branch dead because its films aired under another name -- is the
    false positive that makes a checker get ignored.
    """
    by_branch = defaultdict(lambda: {"aired": [], "missing": []})
    for identity, paths in config.items():
        bucket = "aired" if identity in played else "missing"
        for path in paths:
            by_branch[path][bucket].append(identity)

    dead, thin = {}, {}
    for path, split in by_branch.items():
        if not split["missing"]:
            continue
        (dead if not split["aired"] else thin)[path] = split
    return dead, thin


def report(name, dead, thin, show_all, years, window_years):
    """Print one channel's findings. Returns the number of DEAD branches."""
    if years > window_years:
        if dead:
            print(f"\n{name}: SKIPPED -- declares a {years}-year cycle, window "
                  f"is {window_years:.1f} years. Re-run with --days "
                  f"{years * 366} before believing a DEAD finding here.")
        return 0

    if not dead and not (thin and show_all):
        return 0

    print(f"\n{name}")
    for path, split in sorted(dead.items()):
        print(f"  DEAD  {path} -- {len(split['missing'])} item(s), none ever aired")
        for identity in sorted(split["missing"])[:8]:
            print(f"          {identity}")
        if len(split["missing"]) > 8:
            print(f"          ... and {len(split['missing']) - 8} more")
    if show_all:
        for path, split in sorted(thin.items()):
            print(f"  thin  {path} -- {len(split['missing'])} of "
                  f"{len(split['missing']) + len(split['aired'])} not reached")
    return len(dead)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("channel", nargs="?", help="check one channel")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--start", default="2027-01-01")
    parser.add_argument("--all", action="store_true",
                        help="include THIN branches -- random collections that "
                             "did not get round to everything")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    window_years = args.days / 365.25

    channels = discover_channels()
    if args.channel:
        if args.channel not in channels:
            parser.error(f"unknown channel {args.channel!r}; have "
                         f"{', '.join(sorted(channels))}")
        channels = {args.channel: channels[args.channel]}

    print("=" * 78)
    print("UNAIRED CONFIGURATION CHECK")
    print("=" * 78)
    print(f"  Window   : {start.date()} + {args.days} day(s) ({window_years:.1f} years)")
    print(f"  Channels : {len(channels)}")

    logging.disable(logging.CRITICAL)
    try:
        results = {}
        for name, module in sorted(channels.items()):
            config = declared(module)
            results[name] = (config, aired(module, start, args.days))
    finally:
        logging.disable(logging.NOTSET)

    total_dead = 0
    total_declared = 0
    for name, (config, played) in sorted(results.items()):
        total_declared += len(config)
        dead, thin = classify(config, played)
        paths = {p for group in config.values() for p in group}
        total_dead += report(name, dead, thin, args.all,
                             longest_cycle(paths), window_years)

    print("\n" + "=" * 78)
    print(f"  {total_declared} declarations across {len(results)} channel(s); "
          f"{total_dead} dead branch(es)")
    print("=" * 78)

    if total_dead:
        print("\nA DEAD branch names content the channel cannot reach. Either the")
        print("branch is shadowed by one listed before it, or its parent routes")
        print("every date somewhere else. Both are config bugs, not engine bugs.")
        return 1
    print("\nPASS: every configured branch reaches air.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
