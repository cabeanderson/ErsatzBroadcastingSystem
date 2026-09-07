#!/usr/bin/env python3
"""
contact_sheet.py — tile spots into numbered grids for visual gating.

Writes PNG sheets and a JSON index. Reads nothing, moves nothing.

The gate problem is that a filename says almost nothing about what is in a
commercial -- `recategorize_commercials.py` exists because a first pass treated
"no keyword matched" as evidence of safety, and the Winston-cigarette
Flintstones spot is the standing reminder. The 1950s set was eventually gated
from extracted closing frames, which is the only method here that has actually
worked. This industrialises that method.

The output is a grid of representative frames, each tile stamped with an index
that keys back into the JSON. A reviewer -- human or model -- names the indices
that are tobacco, alcohol, kids or christmas, and `apply_gates.py` moves them.
Nothing is inferred from the picture automatically; this tool only makes 3,721
spots reviewable in a few dozen images instead of 30 hours of playback.

## Why one frame per spot, and which one

`thumbnail` picks the most representative frame from a window rather than a
fixed timestamp. A fixed `-ss 50%` lands on a cut or a motion blur often enough
to matter, and on a 15-second spot the midpoint is frequently the product shot's
approach rather than the product shot. Representative beats punctual here.

The frame is taken from the back half by default. Commercials are structured to
end on the logo and the pack shot -- which is exactly the frame that identifies
a brand -- while the first seconds are deliberately ambiguous.

## Why the index is stamped into the pixels

A grid position is only meaningful if the reviewer and the mover agree on it,
and "row 3, column 4" does not survive a crop, a rescale, or a model that reads
the image at a different resolution. Burning the index into the tile makes the
mapping self-describing: whatever the reviewer is looking at carries its own
key.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

DEST = Path("/media/filler/commercials/us")

TILE_W, TILE_H = 320, 240
LABEL_H = 18
BG = (16, 16, 18)
LABEL_BG = (236, 72, 72)
LABEL_FG = (255, 255, 255)


def frame(video: Path, out: Path, at_fraction: float, duration: float) -> bool:
    """Extract one representative frame from around `at_fraction` of the spot.

    The `thumbnail` filter scores a window of frames and returns the most
    representative, so the seek only has to land in the right neighbourhood.
    """
    start = max(0.0, duration * at_fraction)
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.2f}", "-i", str(video),
        "-vf", f"thumbnail=n=30,scale={TILE_W}:{TILE_H}:force_original_aspect_ratio=decrease,"
               f"pad={TILE_W}:{TILE_H}:(ow-iw)/2:(oh-ih)/2:color=black",
        "-frames:v", "1", str(out),
    ]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def duration(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip() or 0)
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def build_sheet(items: list, out_png: Path, cols: int) -> None:
    """Tile extracted frames into one labelled grid."""
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * TILE_W, rows * (TILE_H + LABEL_H)), BG)
    draw = ImageDraw.Draw(sheet)

    for n, item in enumerate(items):
        x = (n % cols) * TILE_W
        y = (n // cols) * (TILE_H + LABEL_H)
        try:
            with Image.open(item["frame"]) as tile:
                sheet.paste(tile.convert("RGB"), (x, y + LABEL_H))
        except (OSError, ValueError):
            draw.rectangle([x, y + LABEL_H, x + TILE_W, y + TILE_H + LABEL_H],
                           fill=(60, 20, 20))
        draw.rectangle([x, y, x + TILE_W, y + LABEL_H], fill=LABEL_BG)
        draw.text((x + 5, y + 4), f"{item['id']}   {item['secs']:.0f}s",
                  fill=LABEL_FG)

    sheet.save(out_png)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--glob", default="*/uncategorized/*.mp4",
                    help="pattern under the US commercial tree")
    ap.add_argument("--out", required=True, help="directory for sheets and index")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--per-sheet", type=int, default=30)
    ap.add_argument("--limit", type=int, default=0, help="0 = all matches")
    ap.add_argument("--at", type=float, default=0.65,
                    help="fraction into the spot to sample; the pack shot is late")
    args = ap.parse_args()

    out = Path(args.out)
    frames_dir = out / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    videos = sorted(DEST.glob(args.glob))
    if args.limit:
        videos = videos[: args.limit]
    if not videos:
        sys.exit(f"no videos matched {args.glob!r} under {DEST}")

    print(f"{len(videos)} spots -> {(len(videos) + args.per_sheet - 1) // args.per_sheet} sheets")

    index, ok = [], 0
    for n, v in enumerate(videos):
        secs = duration(v)
        fp = frames_dir / f"{n:05d}.jpg"
        if frame(v, fp, args.at, secs):
            ok += 1
        index.append({"id": n, "path": str(v), "secs": secs, "frame": str(fp)})

    print(f"frames extracted: {ok}/{len(videos)}")

    sheets = []
    for start in range(0, len(index), args.per_sheet):
        chunk = index[start: start + args.per_sheet]
        png = out / f"sheet_{start // args.per_sheet:03d}.png"
        build_sheet(chunk, png, args.cols)
        sheets.append(str(png))

    (out / "index.json").write_text(json.dumps(index, indent=1))
    print(f"wrote {len(sheets)} sheets and index.json to {out}")


if __name__ == "__main__":
    main()
