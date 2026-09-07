#!/usr/bin/env python3
"""
generate_filler_nfo.py — compile NFO sidecars for the filler tree.

Dry-run by default. Nothing is written unless --apply is passed.

## The fact this tool exists to survive

ErsatzTV's folder-derived tags and NFO sidecars are **mutually exclusive**, not
additive. Verified at source on 2026-09-05:

`FallbackMetadataProvider.GetOtherVideoMetadata` builds tags by splitting the
path and then *assigns* them, clearing the neighbouring collections outright:

    metadata.Tags    = tags;
    metadata.Genres  = [];
    metadata.Actors  = [];
    metadata.Studios = [];

and `OtherVideoFolderScanner.UpdateMetadata` treats an NFO as a different
`MetadataKind` — it refreshes sidecar metadata when the present kind is
`Fallback`. So the instant a filler file gains an NFO, its folder tags stop
existing, and every `filler_source()` key in `library/sources.py` that ANDs
`tag_full:"commercials" AND tag_full:"us" AND tag_full:"90s"` silently stops
matching it.

**That makes this a compiler, not an editor.** The NFO must re-declare every tag
the folder path would have produced, or the registry breaks. Everything else it
adds is a bonus on top of that floor. `--verify` exists to prove the floor holds
and is the only check that matters here.

## Why NFO at all, given that risk

Folders can only express single-valued facets. The taxonomy already refused a
genre level for exactly this reason -- "hardlinking a multi-genre film's trailer
into several folders registers as several items and skews shuffle". Duplication
is how a folder tree spells "and", and duplication corrupts shuffle.

The corpus now has several genuinely multi-valued facets -- brand, promo claim
type, break position, era -- and `us/90s/uncategorized/promo/dated/beer/` is not
a tree anyone can maintain. `OtherVideoNfoReader` accepts repeated `<tag>`, so
NFO spells "and" for free.

Folders therefore keep the single-valued navigation spine (country, decade,
gate) and stay the source of truth. This compiles that spine into the sidecar
and appends what the spine cannot hold.

## Why tags are forced lowercase

`tag_full` is indexed with a KeywordAnalyzer and is case-sensitive (taxonomy
§1), and every query in `sources.py` is written lowercase because folder names
on disk are lowercase. A stray `<tag>Commercials</tag>` would index as
`tag_full:"Commercials"` and never match anything, while looking perfectly
correct in the file. Casing is not cosmetic here.

## Why the library root is a parameter

Tags come from `Path.GetRelativePath(parent_of_library_root, folder)`, so the
root determines whether the first tag is `filler` or `media`. **Confirmed
2026-09-05:** the library is local, rooted at `/media/filler` in the container
(the host library mounts to `/media:ro`), added as Other
Videos. The default is therefore correct and every item carries `filler` first.
The parameter stays because a second library over a different root would need
it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

from scripts import config

FILLER = config.FILLER_ROOT
VIDEO = {".mp4", ".mkv", ".avi", ".mpg", ".mpeg", ".m4v", ".webm", ".mov", ".ts"}

LEADING_YEAR = re.compile(r"(19|20)\d{2}")

# Promo classification is NOT redefined here. `split_promos.py` owns it, and an
# earlier copy of the rules in this file drifted: it tagged 557 spots in the
# commercial tree as `promo` that split_promos had already judged were not,
# because the copy lacked the PROGRAMME/RETAIL gate that cut the count from 857
# to 325. Two classifiers over one question is one too many.
#
# This module lives in `filler/` rather than `nfo/` because that is where its
# dependency is. `nfo/` is movie-library tooling (normalize_tag_case.py operates
# on the movie root); this compiles sidecars for the filler tree.
from scripts.filler.split_promos import claim as promo_claim


def folder_tags(video: Path, library_root: Path) -> list:
    """Reproduce exactly what GetOtherVideoMetadata would derive.

    The C# splits `GetRelativePath(parent_of_library_root, folder)` on the
    separator. This mirrors it against the file's *parent* directory, because
    the C# passes the folder, not the file.
    """
    parent_of_root = library_root.parent
    try:
        rel = video.parent.relative_to(parent_of_root)
    except ValueError:
        return []
    return [p.lower() for p in rel.parts if p]


def claim_tags(transcript: str) -> list:
    """Promo claim type, as tags. Empty when the spot is not a promo.

    Both `promo` and the specific claim are emitted, so a query can ask for all
    promos or only the safe ones without enumerating the vocabulary. The
    determination itself comes from split_promos, which is the only place the
    rules live.
    """
    c = promo_claim(transcript or "")
    return ["promo", c] if c else []


def year_for(video: Path, tags: list):
    """Year from the filename, else the decade folder's midpoint is NOT used.

    A decade folder cannot yield a year, and inventing one would put a false
    `<year>` in the guide. Absent is better than wrong.
    """
    m = LEADING_YEAR.search(video.name)
    return m.group(0) if m else None


def build(video: Path, library_root: Path, meta: dict, want_title: bool) -> tuple:
    """Return (xml_text, tags). Tags are returned so --verify can check them."""
    tags = folder_tags(video, library_root)
    transcript = (meta or {}).get("transcript", "")
    tags = tags + [t for t in claim_tags(transcript) if t not in tags]

    lines = ['<?xml version="1.0" encoding="utf-8" standalone="yes"?>', "<movie>"]
    title = (meta or {}).get("title") if want_title else None
    if title:
        lines.append(f"  <title>{escape(title)}</title>")
    year = year_for(video, tags)
    if year:
        lines.append(f"  <year>{year}</year>")
    if transcript:
        # The transcript is the only description this material will ever have,
        # and it is what makes a spot findable by what it actually says.
        lines.append(f"  <plot>{escape(transcript)}</plot>")
    lines += [f"  <tag>{escape(t)}</tag>" for t in tags]
    lines.append("</movie>")
    return "\n".join(lines) + "\n", tags


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--glob", default="commercials/us/*/*/*.mp4",
                    help="pattern under the filler root")
    ap.add_argument("--library-root", default=str(FILLER),
                    help="ErsatzTV Other Videos library root — open question 7")
    ap.add_argument("--analysis", help="index.json from analyze_spots.py")
    ap.add_argument("--titles", action="store_true",
                    help="write <title> from the analysis. Off by default: whisper "
                         "mis-hears brands ('Matter House' for Manor House), and a "
                         "wrong title is worse in a guide than none")
    ap.add_argument("--verify", action="store_true",
                    help="check every emitted NFO re-declares its folder tags, "
                         "then exit. This is the check that matters")
    ap.add_argument("--apply", action="store_true", help="write the .nfo files")
    args = ap.parse_args()

    library_root = Path(args.library_root)
    videos = sorted(FILLER.glob(args.glob))
    if not videos:
        sys.exit(f"no videos matched {args.glob!r} under {FILLER}")

    by_path = {}
    if args.analysis:
        for e in json.loads(Path(args.analysis).read_text()):
            by_path[e["path"]] = e

    if args.verify:
        bad = 0
        for v in videos:
            _, tags = build(v, library_root, by_path.get(str(v)), args.titles)
            expected = folder_tags(v, library_root)
            missing = [t for t in expected if t not in tags]
            wrong_case = [t for t in tags if t != t.lower()]
            if missing or wrong_case:
                bad += 1
                if bad <= 10:
                    print(f"  {v.name}: missing={missing} wrong_case={wrong_case}")
        print(f"\n{len(videos)} checked, {bad} would lose or miscase a folder tag")
        sys.exit(1 if bad else 0)

    stats, sample = Counter(), []
    for v in videos:
        xml, tags = build(v, library_root, by_path.get(str(v)), args.titles)
        stats["nfo"] += 1
        stats["with plot"] += 1 if "<plot>" in xml else 0
        stats["with title"] += 1 if "<title>" in xml else 0
        stats["promo tagged"] += 1 if "<tag>promo</tag>" in xml else 0
        if len(sample) < 1:
            sample.append((v, xml))
        if args.apply:
            v.with_suffix(".nfo").write_text(xml, encoding="utf-8")

    print(f"tree: {FILLER}   library root: {library_root}")
    print(f"tags derived relative to: {library_root.parent}\n")
    for k, n in stats.most_common():
        print(f"  {k:<14} {n}")
    if sample:
        v, xml = sample[0]
        print(f"\nsample — {v.name}\n")
        print("\n".join("    " + ln for ln in xml.splitlines()[:14]))

    if not args.apply:
        print("\nre-run with --apply to write. Run --verify first.")
    else:
        print(f"\nwrote {stats['nfo']} .nfo files. "
              "ErsatzTV must rescan, and the scan will REPLACE folder tags "
              "with these.")


if __name__ == "__main__":
    main()
