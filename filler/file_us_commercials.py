#!/usr/bin/env python3
"""
file_us_commercials.py — move staged US spots into commercials/us/<decade>/<gate>/.

Dry-run by default. Nothing moves unless --apply is passed.

Two staged sets, both from archive.org, land in the tree §5 of
filler-taxonomy.md defines: country / decade / audience-gate. The gate level is
the one that drives scheduling, and it is assigned conservatively, on that
section's own rule -- a false gate only withholds a spot from a kids daypart,
while the opposite error airs the wrong thing in one.

Gate assignment lives in `recategorize_commercials.gate`, which is the single
source of truth for it -- this module only decides *what to file at all* and
where the decade folder is. A gate is a positive determination: a spot is
categorized only when the category is clear, and everything else goes to
`uncategorized/`, which no daytime or kids key draws from.

The 56 reels over seven minutes are deliberately NOT filed. They are off-air
recordings up to 131 minutes long -- archive material, not interstitials -- and
they stay staged until someone decides whether splitting them is worth doing.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recategorize_commercials import gate  # noqa: E402  single source of truth

STAGE_US = Path("/media/.staging/us_commercials")
STAGE_CTVC = Path("/media/.staging/ctvc")
DEST = Path("/media/filler/commercials/us")
REEL_SECONDS = 420  # over seven minutes is an off-air recording, not a spot

VIDEO = {".mp4", ".mkv", ".avi", ".mpg", ".mpeg", ".m4v", ".webm", ".mov", ".ts"}

# Verified from closing frames, not filenames -- see the module docstring.
CTVC_TOBACCO = {"CHESTER", "FLINT", "LNM", "LNM02", "MORRIS", "ROYTAN"}
CTVC_KIDS = {"RICECRPS", "GRAPENUT", "KAISER", "ZORRO"}


def duration(path: Path) -> float:
    """Seconds, or 0.0 if ffprobe cannot read the file.

    Probed here rather than read from a sidecar so the script stays runnable on
    its own for the next acquisition.
    """
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip() or 0)
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def decade(name: str):
    m = re.match(r"^(19|20)(\d)", name)
    return f"{m.group(2)}0s" if m else None



def plan():
    """Return (moves, reels) where moves is [(src, dest, note)]."""
    moves, reels = [], []

    for src in sorted(STAGE_US.iterdir()):
        if not src.is_file() or src.suffix.lower() not in VIDEO:
            continue
        name = src.name
        secs = duration(src)
        if secs > REEL_SECONDS:
            reels.append((src, secs))
            continue
        dec = decade(name)
        if dec is None:
            reels.append((src, secs))       # undated; do not guess
            continue
        g = gate(name)
        moves.append((src, DEST / dec / g / name, g))

    # ctvc: verified 1950s-early 60s from frames; filed as one decade.
    for src in sorted(STAGE_CTVC.iterdir()):
        if not src.is_file():
            continue
        g = gate(src.name)
        moves.append((src, DEST / "50s" / g / src.name, g))

    return moves, reels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually move files")
    ap.add_argument("--show", type=int, default=0, help="list N assignments per gate")
    args = ap.parse_args()

    for p in (STAGE_US, STAGE_CTVC):
        if not p.exists():
            sys.exit(f"missing: {p}")

    moves, reels = plan()

    by_gate = Counter(g for _, _, g in moves)
    by_dec = Counter(d.parent.parent.name for _, d, _ in moves)
    print(f"to file: {len(moves)}     left staged (reels): {len(reels)}")
    print("\nby gate:")
    for k, v in by_gate.most_common():
        print(f"  {k:<12} {v}")
    print("\nby decade:")
    for k in sorted(by_dec):
        print(f"  {k:<12} {by_dec[k]}")

    if args.show:
        for gate_name in ("tobacco", "kids", "uncategorized"):
            sel = [d.name for _, d, g in moves if g == gate_name][: args.show]
            print(f"\n{gate_name}:")
            for n in sel:
                print(f"  {n[:72]}")

    if not args.apply:
        print("\nre-run with --apply to move.")
        return

    done = Counter()
    for src, dest, _ in moves:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            done["already there"] += 1
            continue
        shutil.move(str(src), str(dest))
        done["moved"] += 1
    print("\napplied:")
    for k, v in done.items():
        print(f"  {k:<14} {v}")


if __name__ == "__main__":
    main()
