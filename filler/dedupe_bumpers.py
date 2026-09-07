#!/usr/bin/env python3
"""
dedupe_bumpers.py — file new bumper segments, skipping ones already owned.

Dry-run by default. Nothing moves unless --apply is passed.

The Toonami tree holds 1,251 files. The four 2001 compilations split into 153
segments almost certainly restate some of them, and filing blind would put
duplicates into a shuffle pool -- which the taxonomy already identifies as the
specific harm to avoid, since a duplicated item is drawn twice as often.

## Why perceptual hashing and not size or duration

These are re-encodes of a compilation, not copies. The same 10-second bumper
arrives at a different resolution, bitrate, container and byte length than the
copy already on disk, so every exact-identity test -- checksum, size, even
duration to the frame -- reports "different" for files that are the same
content. `split_reels` de-duplicates its twin containers on duration and size
because those really are the same encode twice; that test is wrong here.

A difference hash over a downscaled greyscale frame survives re-encoding, which
is exactly the property needed. Frames are taken at 50% rather than the 65% used
for commercials: a bumper has no pack shot to end on, and its midpoint is the
most stable thing about it.

## Why the threshold is conservative

Hamming distance <= 6 over a 64-bit dHash. Bumpers from one network are *meant*
to look alike -- same logo, same palette, same motion -- so a loose threshold
collapses genuinely distinct bumpers. The failure this guards against is a
duplicate entering the pool; a missed duplicate is one extra file among 1,251
and costs nothing measurable. Tight beats loose here, which is the opposite of
the gate rule in transcript_gate.py, and for the opposite reason.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image

from scripts import config

HASH_SIDE = 9  # dHash compares adjacent pixels, so 9x8 yields 64 bits
MAX_DISTANCE = 6


def duration(path: Path) -> float:
    try:
        out = subprocess.run(
            [config.FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip() or 0)
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def dhash(video: Path, tmp: Path) -> int | None:
    """64-bit difference hash of the frame at the midpoint, or None."""
    secs = duration(video)
    if secs <= 0:
        return None
    cmd = [config.FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-ss", f"{secs * 0.5:.2f}", "-i", str(video),
           "-vf", f"scale={HASH_SIDE}:{HASH_SIDE - 1},format=gray",
           "-frames:v", "1", str(tmp)]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        return None
    try:
        with Image.open(tmp) as im:
            px = list(im.convert("L").get_flattened_data() if hasattr(im, "get_flattened_data") else im.convert("L").getdata())
    except (OSError, ValueError):
        return None
    if len(px) < HASH_SIDE * (HASH_SIDE - 1):
        return None
    bits = 0
    for row in range(HASH_SIDE - 1):
        for col in range(HASH_SIDE - 1):
            i = row * HASH_SIDE + col
            bits = (bits << 1) | (1 if px[i] < px[i + 1] else 0)
    return bits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--new", required=True, help="directory of candidate segments")
    ap.add_argument("--against", required=True, help="existing tree to compare with")
    ap.add_argument("--dest", required=True, help="where accepted files go")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    new_dir, existing_dir, dest = Path(args.new), Path(args.against), Path(args.dest)
    tmp = Path("/tmp/_dedupe_frame.png")

    existing = [p for p in sorted(existing_dir.rglob("*")) if p.suffix.lower() == ".mp4"]
    candidates = [p for p in sorted(new_dir.glob("*.mp4"))]
    print(f"hashing {len(existing)} existing and {len(candidates)} candidates "
          f"(one decode each)...")

    seen = {}
    for p in existing:
        h = dhash(p, tmp)
        if h is not None:
            seen.setdefault(h, p)

    stats, accept = Counter(), []
    for p in candidates:
        h = dhash(p, tmp)
        if h is None:
            stats["unreadable"] += 1
            continue
        dup = next((q for k, q in seen.items()
                    if bin(k ^ h).count("1") <= MAX_DISTANCE), None)
        if dup is not None:
            stats["duplicate"] += 1
            continue
        seen[h] = p          # also guards against duplicates within the new set
        accept.append(p)
        stats["new"] += 1

    print(f"\n  already owned  {stats['duplicate']}")
    print(f"  new            {stats['new']}")
    if stats["unreadable"]:
        print(f"  unreadable     {stats['unreadable']}")

    if not args.apply:
        print(f"\nwould file {len(accept)} into {dest}")
        print("re-run with --apply to move.")
        return

    dest.mkdir(parents=True, exist_ok=True)
    moved = 0
    for p in accept:
        target = dest / p.name
        if target.exists():
            continue
        shutil.move(str(p), str(target))
        moved += 1
    print(f"\nfiled {moved} into {dest}")


if __name__ == "__main__":
    main()
