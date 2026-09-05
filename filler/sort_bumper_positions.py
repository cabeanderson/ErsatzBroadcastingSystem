#!/usr/bin/env python3
"""
sort_bumper_positions.py — file bumpers by break position.

Dry-run by default. Nothing moves unless --apply is passed.

The promos were never missing. They are sitting in the bumper tree with their
function written in the filename and nowhere else:

    Toonami_Evangelion_1_11_Next.mp4      <- a promo. "Next: Evangelion."
    Toonami_Now_Evangelion_1_11.mp4       <- goes immediately before the show
    Toonami_Evangelion_1_11_To_Ads.mp4    <- goes immediately after it
    Toonami_Evangelion_1_11_Back_3.mp4    <- returns from the break

That is a complete break-position vocabulary, and it is exactly the structure
the scheduler needs to honour "a bumper always touches a show". A filename is
not a tag, though: ErsatzTV derives tags from folder path segments only
(FallbackMetadataProvider.GetOtherVideoMetadata), so none of it is addressable
today. 216 Toonami `Next` files -- the promos -- are indistinguishable from any
other bumper as far as a query is concerned.

This moves each file into a position folder under its existing parent:

    shows/dragon ball z/Toonami_DBZ_To_Ads.mp4
    shows/dragon ball z/to ads/Toonami_DBZ_To_Ads.mp4

Tags are flat and un-nested, so `dragon ball z` survives the move untouched and
every existing per-show key keeps working -- the taxonomy's "depth is free, and
adding a level never breaks an existing query". What is gained is a second tag,
which is what lets the dispatcher ask for the *right* bumper for a position
rather than any bumper for the show:

    tag_full:"dragon ball z" AND tag_full:"to ads"     leaving the show
    tag_full:"dragon ball z" AND tag_full:"back"       returning to it
    tag_full:"next"                                    the promo pool

Deliberately NOT moved to a separate `promos/` tree. These files are Toonami-
branded whatever they advertise, so filing them as network-neutral promos would
be a lie by folder path -- and it would strip the `bumpers` tag that
dispatcher.play_smart_bumper requires. A `next` position folder makes them
addressable as promos without either cost.

`general/` is the residue, and it is a real answer here rather than the
"nothing matched" failure recategorize_commercials.py warns about: an Adult Swim
bump with no positional marker genuinely has no position. It plays anywhere.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/media/filler/bumpers")

# Order matters. `Toonami_2_0_Evangelion_2_22_Back_3` must read as "back", and
# `Toonami_Now_Evangelion_1_11` as "now", so the more specific two-word markers
# are tested before the single words that appear inside them. `to ads` is
# checked before `ads` for the same reason.
POSITIONS = [
    ("to ads", re.compile(r"(?:^|[_\W])to[_\W]*ads?(?:[_\W]|$)", re.I)),
    ("next",   re.compile(r"(?:^|[_\W])next(?:[_\W]|\d|$)", re.I)),
    ("back",   re.compile(r"(?:^|[_\W])back(?:[_\W]|\d|$)", re.I)),
    ("now",    re.compile(r"(?:^|[_\W])now(?:[_\W]|$)", re.I)),
    ("later",  re.compile(r"(?:^|[_\W])later(?:[_\W]|$)", re.I)),
    ("intro",  re.compile(r"(?:^|[_\W])intro(?:[_\W]|\d|$)", re.I)),
    ("outro",  re.compile(r"(?:^|[_\W])outro(?:[_\W]|\d|$)", re.I)),
]

# Folders that already ARE a position. Re-filing `intro/` into `intro/intro/`
# would be silly, and `general/` is the residue bucket this script writes to.
TERMINAL = {"intro", "outro", "general", "to ads", "next", "back", "now", "later"}

VIDEO = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".ts", ".mpg"}


def position_of(name: str) -> str | None:
    """Return the break position encoded in a filename, or None."""
    stem = Path(name).stem
    for label, pattern in POSITIONS:
        if pattern.search(stem):
            return label
    return None


def plan(scope: Path):
    """Build src -> dest. Returns (moves, residue, skipped)."""
    moves, residue, skipped = {}, [], []

    for f in sorted(scope.rglob("*")):
        if not f.is_file() or f.name.startswith(".") or f.suffix.lower() not in VIDEO:
            continue

        parent = f.parent.name.lower()
        if parent in TERMINAL:
            skipped.append(f)          # already filed by position
            continue

        pos = position_of(f.name)
        if pos is None:
            residue.append(f)          # no position -- belongs in general/
            continue

        dest = f.parent / pos / f.name
        if dest.exists() and dest != f:
            skipped.append(f)
            continue
        moves[f] = dest

    return moves, residue, skipped


def apply_moves(mapping, manifest: Path, apply: bool) -> Counter:
    stats = Counter()
    lines = []
    for src, dest in sorted(mapping.items()):
        lines.append(f"{src}\t{dest}")
        stats[dest.parent.name] += 1
        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src), str(dest))
            except OSError as e:
                print(f"  !! move failed {src}: {e}")
                stats["failed"] += 1
    if apply and lines:
        manifest.write_text("\n".join(lines) + "\n")
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--apply", action="store_true", help="actually move files")
    ap.add_argument("--scope", default="cartoon network",
                    help="subtree under bumpers/ to sort (default: 'cartoon network')")
    ap.add_argument("--residue", action="store_true",
                    help="also move position-less files into general/")
    ap.add_argument("--manifest", default="/tmp/bumper_positions.tsv",
                    help="where to write the undo manifest on --apply")
    ap.add_argument("--show", type=int, default=10)
    args = ap.parse_args()

    scope = ROOT / args.scope
    if not scope.is_dir():
        sys.exit(f"not a directory: {scope}")

    moves, residue, skipped = plan(scope)

    if args.residue:
        for f in residue:
            dest = f.parent / "general" / f.name
            if not dest.exists():
                moves[f] = dest

    by_pos = Counter(d.parent.name for d in moves.values())
    print(f"scope: {scope}")
    print(f"planned moves: {len(moves)}")
    for k, v in sorted(by_pos.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<10} {v}")
    print(f"\nalready filed by position: {len(skipped)}")
    print(f"no position in filename:   {len(residue)}"
          f"{' (moving to general/)' if args.residue else ' (left in place; --residue to file)'}")

    for src, dest in list(sorted(moves.items()))[: args.show]:
        print(f"  {src.name}\n    -> {dest.relative_to(ROOT)}")

    stats = apply_moves(moves, Path(args.manifest), args.apply)
    print("\n" + ("applied:" if args.apply else "would move (dry run):"))
    for k, v in sorted(stats.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<10} {v}")
    if args.apply:
        print(f"\nundo manifest: {args.manifest}")
    else:
        print("\nre-run with --apply to move. A rescan is required afterwards.")


if __name__ == "__main__":
    main()
