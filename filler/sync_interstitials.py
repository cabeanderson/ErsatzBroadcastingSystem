#!/usr/bin/env python3
"""
sync_interstitials.py — mirror movie trailers/extras into the filler tree.

Dry-run by default. Nothing touches disk unless --apply is passed.

ErsatzTV's movie scanner cannot see any of this content. `MovieFolderScanner`
recurses into subfolders only when the folder holds no video files of its own
(and separately drops any file whose stem ends in one of `ExtraFiles`), so a
movie folder containing the film never has its `extras/` or `trailers/` walked.
The `ExtraDirectories` constant that names those folders is referenced only by
a test's ValueSource -- the exclusion is a side effect of the recursion gate,
not a folder blocklist.

So the way in is an Other Videos library, which recurses unconditionally and
applies no extras filter. This builds the parallel tree it scans, using
hardlinks: the extras are 1.2TB against 3.3TB free, and a hardlink costs
nothing. Both trees are on the same NFS export, so links are possible at all.

Layout is `<type>/<decade>/<film title>/`, and every level is deliberate.
`FallbackMetadataProvider.GetOtherVideoMetadata` splits the path into *flat*
tags -- order and nesting are not recorded -- so one tree serves two queries at
once: `tag:"trailers" AND tag:"1970s"` for a decade pool, and the film-title
level for `dispatcher.play_smart_bumper`, which interpolates
`type:"other_video" AND tag:"{title}" AND tag:"trailers"` and therefore fires a
film's own trailer before that film with no registry key at all. Depth is free;
adding a level costs one tag and breaks no existing query.

Types are kept apart rather than flattened into `extras/` because the folder is
the only length signal there is, and the spread is an order of magnitude:
trailers run a 2m11s median against a 2m51s max, interviews 12m56s against
49m45s. Flattened, a 50-minute interview lands in the same pool as a 98-second
deleted scene.

Source folders are matched case-insensitively and destinations are always
written lowercase. 71 source dirs are capitalised (`Extras`, `Trailers`,
`Featurettes` -- which has no lowercase form at all), and `tag_full` is indexed
with a KeywordAnalyzer, so a stray `Extras/` would yield `tag_full:"Extras"`
and never match a lowercase query. Normalising here rather than renaming on
disk leaves the source tree -- and Jellyfin -- untouched.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT_MOVIES = Path("/media/movies")
ROOT_FARM = Path("/media/filler/interstitials")

# ErsatzTV LocalFolderScanner.VideoFileExtensions, verbatim. Anything outside
# this list is invisible to the scanner, so linking it would only make orphans.
VIDEO_EXTENSIONS = {
    ".avs", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg", ".ogv", ".mp4",
    ".m4p", ".m4v", ".avi", ".wmv", ".mov", ".mkv", ".m2ts", ".ts", ".webm",
}

# Source folder name (lowercased) -> canonical type folder. The singular
# `trailer` is one folder in the library and means the same thing as the
# plural. `specials`, `scenes` and `other` are unused today and are here so a
# newly ripped disc lands somewhere sensible instead of being skipped.
TYPES = {
    "trailers": "trailers",
    "trailer": "trailers",
    "extras": "extras",
    "interviews": "interviews",
    "deleted scenes": "deleted scenes",
    "behind the scenes": "behind the scenes",
    "featurettes": "featurettes",
    "shorts": "shorts",
    "specials": "specials",
    "scenes": "scenes",
    "other": "other",
}

DIR_YEAR = re.compile(r"^(.*?)\s*\((\d{4})\)\s*$")
ARTICLE = re.compile(r"^(.*),\s*(the|a|an)$", re.IGNORECASE)


def film_title_and_year(name: str):
    """('Knight's Tale, A (2001) ') -> ('a knight's tale', 2001).

    Three movie dirs carry trailing whitespace, and the library inverts
    articles for sorting. The tag has to read the way the film's library title
    reads, because play_smart_bumper matches on that title.
    """
    m = DIR_YEAR.match(name.strip())
    if not m:
        return None, None
    title, year = m.group(1).strip(), int(m.group(2))
    a = ARTICLE.match(title)
    if a:
        title = f"{a.group(2)} {a.group(1)}"
    title = re.sub(r"\s+", " ", title).strip().lower()
    return (title or None), year


def walk_type(d: Path, kind: str, prefix: list):
    """Yield (kind, prefix, file) for every video below a matched type dir.

    Disc rips group extras into free-form folders -- `Mission Control`,
    `Outtakes - Day 2`, `Press Timeline - 16 Interviews & Conversations` -- and
    236 files sit three and four levels below the film inside them. A
    depth-limited read drops all of them.

    A nested folder that is itself a known type reclassifies what is under it
    and resets the prefix; anything else is a grouping, so its name is folded
    into the destination filename. That matters: Panic Room ships seven
    same-named files (`B-Roll.mkv`, `Dailies.mkv`, ...) in different grouping
    folders, which would collide the moment the grouping was discarded.
    """
    try:
        entries = sorted(d.iterdir())
    except OSError:
        return
    for e in entries:
        if e.name.startswith("."):
            continue
        if e.is_symlink():
            continue
        if e.is_file():
            if e.suffix.lower() in VIDEO_EXTENSIONS and not e.name.startswith("._"):
                yield kind, prefix, e
        elif e.is_dir():
            # ErsatzTV honours .etvignore in ShouldIncludeFolder; match it.
            if (e / ".etvignore").exists():
                continue
            sub = TYPES.get(e.name.strip().lower())
            if sub:
                yield from walk_type(e, sub, [])
            else:
                yield from walk_type(e, kind, prefix + [e.name.strip()])


def source_files(movie: Path):
    """Yield (kind, prefix, file) for every extra belonging to one film."""
    try:
        children = sorted(movie.iterdir())
    except OSError:
        return
    for child in children:
        if not child.is_dir() or child.name.startswith(".") or child.is_symlink():
            continue
        kind = TYPES.get(child.name.strip().lower())
        if kind:
            yield from walk_type(child, kind, [])


def plan():
    """Build dest -> source. Returns (mapping, skipped_dirs, conflicts)."""
    mapping, conflicts = {}, []
    skipped = []

    for movie in sorted(ROOT_MOVIES.iterdir()):
        if not movie.is_dir() or movie.name.startswith("."):
            continue
        title, year = film_title_and_year(movie.name)
        if not title:
            skipped.append(movie.name)
            continue
        decade = f"{year // 10 * 10}s"

        for kind, prefix, f in source_files(movie):
            name = " - ".join(prefix + [f.name]) if prefix else f.name
            dest = ROOT_FARM / kind / decade / title / name
            if dest in mapping and mapping[dest] != f:
                # Two films share a title inside one decade. Disambiguate on
                # the year rather than silently dropping one.
                dest = dest.with_name(f"{dest.stem} ({year}){dest.suffix}")
                if dest in mapping and mapping[dest] != f:
                    conflicts.append((dest, f))
                    continue
            mapping[dest] = f

    return mapping, skipped, conflicts


def sync(mapping, apply: bool):
    """Create/repair links and prune orphans. Returns a Counter of actions."""
    stats = Counter()

    for dest, src in sorted(mapping.items()):
        try:
            s = src.stat()
        except OSError:
            stats["source vanished"] += 1
            continue

        if dest.exists():
            # Path equality is not enough. A re-ripped disc writes a new inode
            # at the same source path; the old link would keep serving stale
            # content and pin the replaced file's blocks forever.
            if dest.stat().st_ino == s.st_ino:
                stats["ok"] += 1
                continue
            stats["relinked"] += 1
            if apply:
                dest.unlink()
        else:
            stats["linked"] += 1

        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(src, dest)
            except OSError as e:
                print(f"  !! link failed {dest}: {e}")
                stats["failed"] += 1

    # Prune anything in the farm the plan no longer accounts for.
    if ROOT_FARM.is_dir():
        for f in sorted(ROOT_FARM.rglob("*")):
            if f.is_file() and f not in mapping:
                stats["pruned"] += 1
                if apply:
                    f.unlink()
        if apply:
            for d in sorted(ROOT_FARM.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if d.is_dir() and not any(d.iterdir()):
                    d.rmdir()
                    stats["empty dirs removed"] += 1

    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--apply", action="store_true", help="actually create and prune links")
    ap.add_argument("--show", type=int, default=12, help="how many sample links to list")
    args = ap.parse_args()

    if not ROOT_MOVIES.is_dir():
        sys.exit(f"movie library not found: {ROOT_MOVIES}")

    mapping, skipped, conflicts = plan()

    by_type = Counter(d.relative_to(ROOT_FARM).parts[0] for d in mapping)
    print(f"planned links: {len(mapping)}")
    for k, v in sorted(by_type.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<20} {v}")

    if skipped:
        print(f"\nmovie dirs with no (year), skipped: {len(skipped)}")
        for n in skipped[: args.show]:
            print(f"  {n}")
    if conflicts:
        print(f"\nunresolved name conflicts: {len(conflicts)}")
        for dest, src in conflicts[: args.show]:
            print(f"  {dest}  <-  {src}")

    stats = sync(mapping, args.apply)
    print("\n" + ("applied:" if args.apply else "would do (dry run):"))
    for k, v in sorted(stats.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<20} {v}")
    if not args.apply:
        print("\nre-run with --apply to write.")


if __name__ == "__main__":
    main()
