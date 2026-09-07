#!/usr/bin/env python3
"""
fetch_archive.py — download one archive.org item into staging, ready to split.

Dry-run by default. Nothing is written unless --apply is passed.

`scout_archive.py` finds items; this fetches one. The two are separate because
finding is cheap and repeatable and fetching is neither -- the material is
stored at archival bitrates and the pool has finite room, so the download stays
a deliberate, one-item-at-a-time act. §4 of interstitial-acquisition.md sets the
cycle: fetch, split, keep the spots, delete the source.

## Why it picks a derivative rather than the item

An item's advertised size is everything in it -- the original upload, every
derivative, the torrent, the thumbnails. The useful file is usually a fraction
of that: `Televisi1960` lists at 1.8 GB and its h.264 derivative is 151 MB, and
the Disney Afternoon rip lists at 3.0 GB against 536 MB of h.264. Downloading
"the item" therefore costs an order of magnitude more than downloading what you
came for.

The preference order is the smallest format that is still a full-resolution
copy. `h.264` and `MPEG4` are the normal derivatives; `Ogg Video` and
`512Kb MPEG4` are deliberately excluded despite being smaller, because they are
transcodes of a transcode and this material is already tape-sourced.

## Why multi-part items are kept as parts

DVD rips arrive as `VIDEO_TS/VTS_01_1.mp4`, `VTS_01_2.mp4` and so on -- one
recording cut at DVD chapter boundaries. They are downloaded as separate files
and *not* concatenated, because `split_reels.py` finds its own boundaries and a
part boundary is simply one more cut it does not have to make. Concatenating
would mean re-encoding two hours to save nothing.

## Why the destination filename leads with a year

`split_reels.decade()` reads the leading year of the filename and nothing else,
and skips any file that has none rather than guessing. So the name is not
cosmetic -- it is the only metadata that survives into the filed spot. `--name`
is required for that reason, and it is checked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

STAGING = Path("/media/.staging/downloads")
METADATA = "https://archive.org/metadata"
DOWNLOAD = "https://archive.org/download"

# Best first. Anything not listed is ignored -- see the docstring on why the
# low-bitrate derivatives are excluded rather than preferred.
FORMAT_RANK = ["h.264", "MPEG4", "HiRes MPEG4", "MPEG2", "Matroska"]

VIDEO_SUFFIX = (".mp4", ".mkv", ".avi", ".mpg", ".mpeg", ".mov", ".m4v", ".ts")

# A DVD menu stub is a few hundred KB; the shortest real capture here is tens of MB.
MENU_STUB_BYTES = 4_000_000
LEADING_YEAR = re.compile(r"^(19|20)\d{2}")


def metadata(identifier: str) -> dict:
    url = f"{METADATA}/{urllib.parse.quote(identifier)}"
    req = urllib.request.Request(url, headers={"User-Agent": "scripted-schedules/fetch"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.load(fh)


def twin_key(name: str) -> str:
    """Normalise `X.ia.mp4` and `X.mp4` to the same key.

    archive.org stores its own derivative beside the uploader's original, and
    for a 320-file item that doubles the download. `split_reels` already
    de-duplicates twins by duration and size, but only after they are on disk;
    catching them here saves the bytes.
    """
    stem = Path(name).stem
    return (stem[:-3] if stem.lower().endswith(".ia") else stem).lower()


def choose_matching(files: list, pattern) -> list:
    """Files whose name matches `pattern`, twins collapsed to one.

    Used instead of `choose` when a caller filters by name, because a mixed
    item -- an uploader's originals beside archive.org derivatives -- has no
    single format that covers everything wanted. Format grouping is right for a
    uniform item and wrong for a grab-bag.
    """
    vids = [f for f in files
            if f["name"].lower().endswith(VIDEO_SUFFIX)
            and int(f.get("size", 0)) > MENU_STUB_BYTES
            and pattern.search(f["name"])]
    best = {}
    for f in vids:
        k = twin_key(f["name"])
        # Prefer the uploader's original over the `.ia` derivative.
        if k not in best or (".ia." in best[k]["name"].lower()
                             and ".ia." not in f["name"].lower()):
            best[k] = f
    return sorted(best.values(), key=lambda f: f["name"])


def choose(files: list) -> list:
    """Pick the best-ranked format present, and return all its parts in order.

    Selecting a *format* rather than the largest files matters for multi-part
    items: the parts of one recording must all come from the same derivative,
    or the halves of an evening arrive at different resolutions.
    """
    videos = [f for f in files if f["name"].lower().endswith(VIDEO_SUFFIX)
              and int(f.get("size", 0)) > 0]
    for fmt in FORMAT_RANK:
        group = [f for f in videos if f.get("format") == fmt]
        if not group:
            continue
        # DVD rips ship a `VIDEO_TS/VIDEO_TS.mp4` menu stub alongside the real
        # titles. It is a valid video of the disc menu, so no format or suffix
        # test excludes it; size does. Only prune when something larger exists,
        # so a genuinely short item is never emptied out.
        largest = max(int(f.get("size", 0)) for f in group)
        if largest > MENU_STUB_BYTES:
            group = [f for f in group if int(f.get("size", 0)) > MENU_STUB_BYTES]
        return sorted(group, key=lambda f: f["name"])
    return []


def fetch(identifier: str, remote: str, dest: Path) -> bool:
    url = f"{DOWNLOAD}/{urllib.parse.quote(identifier)}/{urllib.parse.quote(remote)}"
    tmp = dest.with_suffix(dest.suffix + ".partial")
    req = urllib.request.Request(url, headers={"User-Agent": "scripted-schedules/fetch"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as out:
            while chunk := r.read(1 << 20):
                out.write(chunk)
    except (urllib.error.URLError, OSError) as e:
        tmp.unlink(missing_ok=True)
        print(f"  !! {dest.name}: {e}")
        return False
    tmp.rename(dest)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("identifier", help="archive.org item identifier")
    ap.add_argument("--name", required=True,
                    help='destination stem, MUST lead with the year, e.g. '
                         '"1993-08-21 ABC Saturday Morning Cartoons"')
    ap.add_argument("--dest", default=str(STAGING), help="staging directory")
    ap.add_argument("--match",
                    help="regex over filenames; selects individual files instead of a "
                         "whole format group. For grab-bag items that mix continuity "
                         "with programmes")
    ap.add_argument("--apply", action="store_true", help="actually download")
    args = ap.parse_args()

    if not LEADING_YEAR.match(args.name):
        sys.exit(f"--name must start with a 4-digit year; got {args.name!r}.\n"
                 "split_reels.decade() reads that and nothing else, and skips "
                 "files without it.")

    try:
        meta = metadata(args.identifier)
    except (urllib.error.URLError, ValueError) as e:
        sys.exit(f"metadata lookup failed for {args.identifier}: {e}")
    if not meta or not meta.get("files"):
        sys.exit(f"no files listed for {args.identifier} -- check the identifier")

    if args.match:
        parts = choose_matching(meta["files"], re.compile(args.match, re.I))
    else:
        parts = choose(meta["files"])
    if not parts:
        sys.exit(f"no usable video derivative in {args.identifier}; "
                 f"formats present: {sorted({f.get('format', '?') for f in meta['files']})}")

    dest_dir = Path(args.dest)
    total = sum(int(p.get("size", 0)) for p in parts)
    print(f"{args.identifier}")
    print(f"  title  : {meta.get('metadata', {}).get('title', '?')}")
    print(f"  format : {parts[0].get('format')}   parts: {len(parts)}   "
          f"total: {total / 1e6:.0f} MB"
          + ("   (name-matched, twins collapsed)" if args.match else ""))

    plan = []
    for n, p in enumerate(parts, 1):
        suffix = Path(p["name"]).suffix
        if args.match:
            stem = f"{args.name} - {Path(p['name']).stem[:80]}"
        else:
            stem = args.name if len(parts) == 1 else f"{args.name} pt{n:02d}"
        plan.append((p["name"], dest_dir / f"{stem}{suffix}"))
    for remote, dest in plan:
        print(f"    {remote[:56]:<56} -> {dest.name}")

    if not args.apply:
        print("\nre-run with --apply to download.")
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    done = 0
    for remote, dest in plan:
        if dest.exists():
            print(f"  already there: {dest.name}")
            done += 1
            continue
        print(f"  fetching {dest.name} ...")
        if fetch(args.identifier, remote, dest):
            done += 1
    print(f"\n{done}/{len(plan)} files in {dest_dir}")


if __name__ == "__main__":
    main()
