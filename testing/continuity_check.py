#!/usr/bin/env python3
"""
continuity_check.py — find dead air in the live guide.

Walks every channel in ErsatzTV's XMLTV export in start order and reports each
place where one programme stops before the next one starts. That gap is dead
air: the channel has nothing scheduled and the stream has nothing to send.

**Why this exists.** The other offline tools ask whether the library can
satisfy a query. `key_census` scores keys, `validate_titles` checks that titles
resolve, `collision_report` compares channels against each other — and a
channel can pass all three while broadcasting nothing at 04:00, because the
block that owns 04:00 resolved to an empty collection and the fill strategy let
the slot run out. `validate_schedule` does not catch it either: it reports the
structure it was given, and a block that plays zero items is structurally fine.

Three separate defects were found this way and none of them were visible any
other route -- a bare content key handed to `Block(items=...)`, a `Fallback`
secondary given a wrapper, and `fill_strategy="bridge"` unable to close a tail
shorter than one item.

**Reads the live server, not a simulation.** A simulation shows what the
current code would build. This shows what is actually going to air, which
includes playouts built by older code and never reset -- the single most common
cause of a gap that no simulation reproduces.

Usage:

    python3 -m scripts.testing.continuity_check
    python3 -m scripts.testing.continuity_check --future-only
    python3 -m scripts.testing.continuity_check --min-minutes 5
    python3 -m scripts.testing.continuity_check --channel "Totally 80s"
    python3 -m scripts.testing.continuity_check --file /path/to/xmltv.xml

Exit status is 1 when a gap is reported, so this works as a check in a
pipeline. `--future-only` is the one to gate on: a past gap already aired and
cannot be fixed, while a future one still can.
"""
from __future__ import annotations

import argparse
import collections
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from scripts import config

# XMLTV stamps are `YYYYMMDDHHMMSS +ZZZZ`. Every programme in one export shares
# the server's offset, so comparing the naive prefix is safe here and keeps the
# tool free of a timezone dependency.
_STAMP = "%Y%m%d%H%M%S"


def _parse(stamp: str) -> datetime:
    return datetime.strptime(stamp[:14], _STAMP)


def load(source: str | None):
    """Return the parsed XMLTV root, from a file or the live server."""
    if source:
        return ET.parse(source).getroot()
    with urllib.request.urlopen(config.XMLTV_URL, timeout=120) as r:
        return ET.fromstring(r.read())


def channel_names(root) -> dict:
    out = {}
    for c in root.findall("channel"):
        name = c.find("display-name")
        out[c.get("id")] = name.text if name is not None else c.get("id")
    return out


def airings(root) -> dict:
    """channel id -> [(start, stop)], sorted by start."""
    out = collections.defaultdict(list)
    for p in root.findall("programme"):
        out[p.get("channel")].append((_parse(p.get("start")), _parse(p.get("stop"))))
    for v in out.values():
        v.sort()
    return out


def gaps(items, min_minutes: float):
    """Every place the next programme starts after the previous one stops."""
    found = []
    for (_, stop), (start, _) in zip(items, items[1:]):
        minutes = (start - stop).total_seconds() / 60
        if minutes >= min_minutes:
            found.append((stop, start, minutes))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="read an XMLTV file instead of the live server")
    ap.add_argument("--channel", help="substring match on channel name")
    ap.add_argument("--min-minutes", type=float, default=1.0,
                    help="ignore gaps shorter than this (default 1.0)")
    ap.add_argument("--future-only", action="store_true",
                    help="only gaps that have not aired yet -- the fixable ones")
    args = ap.parse_args()

    root = load(args.file)
    names = channel_names(root)
    by_channel = airings(root)
    now = datetime.now()

    total = 0
    channels_hit = 0
    for cid, items in sorted(by_channel.items(), key=lambda kv: names.get(kv[0], "")):
        name = names.get(cid, cid)
        if args.channel and args.channel.lower() not in name.lower():
            continue
        found = gaps(items, args.min_minutes)
        if args.future_only:
            found = [g for g in found if g[1] > now]
        if not found:
            continue
        channels_hit += 1
        minutes = sum(g[2] for g in found)
        total += minutes
        print(f"\n{name}  —  {len(found)} gap(s), {minutes:.0f} min")
        for stop, start, m in found:
            when = "FUTURE" if start > now else "past  "
            print(f"    {when}  {stop:%a %d %b %H:%M} -> {start:%H:%M}   {m:6.0f} min")

    scope = "future " if args.future_only else ""
    if not total:
        print(f"No {scope}dead air. {len(by_channel)} channels are continuous.")
        return 0
    print(f"\n{total:.0f} minutes of {scope}dead air across {channels_hit} channel(s).")
    print("A gap on a channel whose code simulates clean is a stale playout: "
          "reset it rather than editing the channel.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
