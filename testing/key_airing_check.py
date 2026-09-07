#!/usr/bin/env python3
"""
key_airing_check.py — did a scheduled key actually put anything on the air?

Every other checker asks a question that a dead key can pass.

    key_census        can the library satisfy this query?      manifests, offline
    validate_titles   does every scheduled title resolve?      manifests, offline
    validate_schedule is the schedule structurally sound?      simulation
    collision_report  do two channels clash?                   simulation
    continuity_check  is there dead air?                       live guide

`eighties_music_videos` passed all five and had never played. It names no
titles, so `validate_titles` had nothing to check. Its type is `music_video`,
which the TSV manifests do not contain, so `key_census` scored it unevaluable
and moved on. The simulator's mock returns content for any key, so both
simulation tools were satisfied. And the block carried a working
`fallback_content`, so the channel aired Knight Rider in the slot and
`continuity_check` found no gap at all.

**A gap is a loud failure. A fallback is a silent one.** This tool is for the
silent kind. It reads the live guide and asks, of every key a channel
schedules, whether anything attributable to it actually aired.

**Absence is not death, and the difference is the whole design.** A guide covers
days, not months, so most titles in a large rotation legitimately do not appear
in it. Saying so would produce a hundred false alarms and train you to ignore
the tool. So a key is only called DEAD on positive evidence:

    DEAD         Either the manifests confirm the library cannot satisfy it
                 (`key_census` count 0) and nothing aired, or a declared witness
                 airs its pool while the scheduling channel airs none of it.

    ABSENT       Named titles did not air in this guide window, but the library
                 does hold them. Almost always rotation depth. Informational.

    UNWITNESSED  Names no title, and its type is one the manifests cannot see.
                 Nothing in this repository verifies these -- including this
                 tool, until a witness is declared.

    OK / POOL    Aired, witness-confirmed, or a genre/era pool key_census owns.

**Witnesses.** An unwitnessed key can still be checked when another channel
demonstrably airs the pool it draws from. `--witness KEY=CHANNEL` says "this
channel airs this key's content"; the tool then requires the scheduling channel
to air at least one title the witness airs. That is exactly the check that
caught the music video bug -- The Beat airs 176 titles from the pool, Totally
80s airs none of them, and the key between them selects nothing.

Usage:

    python3 -m scripts.testing.key_airing_check
    python3 -m scripts.testing.key_airing_check --file guide.xml
    python3 -m scripts.testing.key_airing_check --channel "Totally 80s"
    python3 -m scripts.testing.key_airing_check --witness a_key="Some Channel"
    python3 -m scripts.testing.key_airing_check --show-absent
    python3 -m scripts.testing.key_airing_check --list-unwitnessed

Exit status is 1 when a key is DEAD, so this can gate a deploy.
"""
from __future__ import annotations

import argparse
import ast
import collections
import pathlib
import sys
from datetime import datetime

from scripts.testing import install_mocks

install_mocks()

from scripts.testing import key_census
from scripts.testing.continuity_check import channel_names, load

# Channel modules whose guide name differs from their docstring name. Only
# genuine disagreements belong here.
NAME_OVERRIDES = {
    "nick": "Nickelodeon",
}

# Keys whose pool is demonstrably aired by another channel. Extendable with
# --witness. A witness turns UNWITNESSED into a real pass or fail.
DEFAULT_WITNESSES = {
    "eighties_music_videos": "The Beat",
}

SKIP_MODULES = {"__init__", "example_channel", "test_channel"}


# ==============================================================================
# THE REPOSITORY SIDE -- which channel schedules which key
# ==============================================================================

def channel_modules():
    """Channel module stem -> the display name in its docstring."""
    root = pathlib.Path(__file__).resolve().parent.parent / "channels"
    out = {}
    for path in sorted(root.glob("*.py")):
        if path.stem in SKIP_MODULES:
            continue
        doc = ast.get_docstring(ast.parse(path.read_text())) or ""
        first = doc.strip().split("\n", 1)[0]
        # "Across the Pond (104) -- British television" -> "Across the Pond"
        name = first.split("(")[0].split(" -- ")[0].split(" - ")[0].strip()
        out[path.stem] = NAME_OVERRIDES.get(path.stem, name)
    return out


def library_imports(stem):
    """Library modules a channel imports, which is where most of its keys live."""
    path = pathlib.Path(__file__).resolve().parent.parent / "channels" / f"{stem}.py"
    libs = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "scripts.library":
                libs.update(a.name for a in node.names)
            elif node.module.startswith("scripts.library."):
                libs.add(node.module.split(".")[-1])
    return libs


def key_owners(stems, used_by):
    """key -> {channel stems that can schedule it}.

    A key reached through a shared module like `common` or `animation` belongs
    to every channel importing it, so it is credited to all of them and only
    counts against a channel when it aired on none of them.
    """
    scope = {stem: {stem} | library_imports(stem) for stem in stems}
    owners = collections.defaultdict(set)
    for key, sites in used_by.items():
        mods = {site.split(".", 1)[0] for site in sites}
        for stem, owned in scope.items():
            if mods & owned:
                owners[key].add(stem)
    return owners


# ==============================================================================
# THE GUIDE SIDE -- what actually aired
# ==============================================================================

def aired_titles(root):
    """Guide channel display name -> Counter of programme titles."""
    names = channel_names(root)
    out = collections.defaultdict(collections.Counter)
    for p in root.findall("programme"):
        title = p.find("title")
        if title is not None and title.text:
            out[names.get(p.get("channel"), p.get("channel"))][title.text] += 1
    return out


def horizon(root):
    stamps = [datetime.strptime(p.get("start")[:14], "%Y%m%d%H%M%S")
              for p in root.findall("programme")]
    return (min(stamps), max(stamps)) if stamps else (None, None)


def match_channel(display, aired):
    """Join a docstring name to a guide name, which carries a number prefix."""
    for guide in aired:
        stripped = guide.split(" ", 1)[1] if " " in guide else guide
        if stripped.lower() == display.lower():
            return guide
    return None


# ==============================================================================
# THE CHECK
# ==============================================================================

def classify(row, channels, aired, witnesses):
    """Return (verdict, detail) for one census row against the live guide."""
    key, query, targets = row["key"], row["query"], row["targets"]
    if not channels:
        return "UNMAPPED", "no channel in this guide schedules it"

    if targets:
        hits = sum(aired[c][t] for c in channels for t in targets
                   if t in aired[c])
        # Titles are compared case-insensitively: the manifests hold "wings",
        # the guide says "Wings".
        if not hits:
            lowered = {c: {t.lower(): n for t, n in aired[c].items()} for c in channels}
            hits = sum(lowered[c].get(t.lower(), 0) for c in channels for t in targets)
        if hits:
            return "OK", f"{hits} airing(s) of {len(targets)} named title(s)"
        named = ", ".join(targets[:4])
        if row["count"] == 0:
            return "DEAD", f"library holds nothing for it, and nothing aired: {named}"
        return "ABSENT", f"library holds it; did not air in this window: {named}"

    witness = witnesses.get(key)
    if witness:
        wname = match_channel(witness, aired) or next(
            (g for g in aired if witness.lower() in g.lower()), None)
        if not wname:
            return "UNWITNESSED", f"witness channel {witness!r} is not in this guide"
        pool = set(aired[wname])
        mine = set().union(*(set(aired[c]) for c in channels))
        shared = pool & mine
        if shared:
            return "OK", f"{len(shared)} title(s) shared with witness {wname}"
        return ("DEAD", f"witness {wname} airs {len(pool)} title(s) from this pool; "
                        f"{', '.join(channels)} airs none of them")

    if row["kind"] is None:
        return "UNWITNESSED", "names no title, and the manifests cannot see this type"
    return "POOL", "genre/era pool -- key_census owns this one"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", help="read an XMLTV file instead of the live server")
    ap.add_argument("--channel", help="substring match on channel name")
    ap.add_argument("--witness", action="append", default=[], metavar="KEY=CHANNEL",
                    help="declare a channel that demonstrably airs a key's pool")
    ap.add_argument("--show-absent", action="store_true",
                    help="list ABSENT keys too (noisy on a short guide)")
    ap.add_argument("--list-unwitnessed", action="store_true",
                    help="list every key no tool verifies, and stop")
    args = ap.parse_args()

    witnesses = dict(DEFAULT_WITNESSES)
    for spec in args.witness:
        if "=" not in spec:
            ap.error(f"--witness expects KEY=CHANNEL, got {spec!r}")
        k, v = spec.split("=", 1)
        witnesses[k.strip()] = v.strip()

    root = load(args.file)
    aired = aired_titles(root)
    first, last = horizon(root)
    stems = channel_modules()
    resolved = {s: match_channel(n, aired) for s, n in stems.items()}

    rows = key_census.census()
    owners = key_owners(stems, {r["key"]: r["used_by"] for r in rows})

    unmapped = [f"{s} ({stems[s]})" for s, g in resolved.items() if not g]
    if unmapped:
        print("Channel modules with no channel in this guide:")
        for u in unmapped:
            print(f"   {u}")
        print()

    results = []
    for row in rows:
        if not isinstance(row["query"], str):
            continue
        chans = sorted(c for c in (resolved.get(s) for s in owners.get(row["key"], ())) if c)
        if args.channel and not any(args.channel.lower() in c.lower() for c in chans):
            continue
        verdict, detail = classify(row, chans, aired, witnesses)
        if verdict == "UNMAPPED":
            continue
        results.append((verdict, row["key"], chans, detail, row["query"]))

    if args.list_unwitnessed:
        un = [r for r in results if r[0] == "UNWITNESSED"]
        print(f"{len(un)} scheduled key(s) that no tool in this repository verifies:\n")
        for _, key, chans, _, query in un:
            print(f"  {key}\n      on: {', '.join(chans)}\n      {query}")
        print("\nDeclare a witness for any of these with --witness KEY=CHANNEL.")
        return 0

    tiers = ["DEAD", "UNWITNESSED"] + (["ABSENT"] if args.show_absent else [])
    for verdict in tiers:
        hits = [r for r in results if r[0] == verdict]
        if not hits:
            continue
        print(f"\n=== {verdict} — {len(hits)} key(s) ===")
        for _, key, chans, detail, query in hits:
            print(f"\n  {key}   [{', '.join(chans)}]")
            print(f"      {detail}")
            print(f"      {query}")

    counts = collections.Counter(r[0] for r in results)
    span = f"{first:%d %b} to {last:%d %b}" if first else "unknown"
    print(f"\n{len(results)} scheduled keys checked against a guide covering {span}.")
    print("  " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    if counts["ABSENT"] and not args.show_absent:
        print(f"  ABSENT keys are in the library but did not air in this window; "
              f"re-run with --show-absent to list them.")

    if counts["DEAD"]:
        print("\nA DEAD key is scheduled and airs nothing. If the slot is not visibly\n"
              "empty then a fallback is covering it -- check the block's fallback_content.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
