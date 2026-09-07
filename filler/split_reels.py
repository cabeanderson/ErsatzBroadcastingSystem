#!/usr/bin/env python3
"""
split_reels.py — cut the staged off-air reels into individual spots.

Dry-run by default. Nothing is written unless --apply is passed.

`file_us_commercials.py` deliberately leaves 56 files staged: anything over
seven minutes is an off-air recording, not an interstitial. Together they are
12 GB and 30.4 hours, and §8 of interstitial-policy.md ranks splitting them
first among every acquisition line, on the grounds that it is the only one that
costs no acquisition at all. This is that split.

## Why two phases

Detection decodes all 30 hours. That is the expensive half and it is pure
observation, so it is cached to JSON under `.reelcuts/` and never repeated. The
planning and cutting halves read the cache, which makes re-running with
different thresholds free -- and the thresholds *will* be retuned, because the
right minimum segment length is not knowable until the first histogram exists.

Cache keys include the detector settings. Changing a threshold invalidates the
entry rather than silently reusing measurements taken under the old one.

## Why black and silence, and not either alone

Calibrated against `1970s TV Commercials.mp4`, which is a clean 30-second reel
and therefore has a knowable right answer -- 14 spots at 30-second spacing.

`blackdetect` alone finds 13 of the 14 boundaries but misses the one at 211.9s,
where the tape cuts between two spots with no black field. `silencedetect`
alone finds that one and misses several the other way, because a spot ending on
a jingle holds audio through the cut. Neither is sufficient; the union is.

They are not equal, though, so they are not merged as equals. A black interval
is a *frame-accurate* boundary and the cut is placed at its midpoint, which
keeps black frames out of both neighbours. A silence interval is only evidence
that a boundary is somewhere nearby, so it contributes a cut solely when no
black interval already covers it.

## Why segments are dropped on length

A US spot is 15, 30 or 60 seconds. Segments far outside that are not spots:
below `MIN_SECONDS` they are fragments left by a double-detected boundary, and
above `MAX_SECONDS` they are almost always two spots with an undetected
boundary between them, or program content that survived the capture. Both are
worse than nothing in a break -- §4 of the policy budgets a break in seconds --
so they are dropped rather than filed and dealt with later.

Dropped segments are *reported*, not deleted: the reels stay staged, so a
retune and a re-run recovers anything this pass gives up on.

## Why there is a flat mode

The default destination is `commercials/us/<decade>/<gate>/`, which is the
commercial tree's shape and encodes two determinations -- when it aired and who
may see it. Neither applies to a bumper. A network ident has no audience gate
(it advertises nothing) and its decade is a property of the *branding era*, not
of the file, which the folder name already carries: `cartoon network/general`
means what it means regardless of year.

So `--flat` files segments straight into `--dest` with no derived levels, and
drops the leading-year requirement with them. It exists because the alternative
-- inventing a decade folder for bumpers -- would add a tag that lies, and flat
tags mean a lie at any depth is visible to every query.

## Why everything lands in `uncategorized/`

A gate is a positive determination (`recategorize_commercials.py`). A segment
cut out of the middle of a reel has no filename at all -- it inherits the
reel's, which names the *program the break was recorded from* and says nothing
about the product on screen. There is no weaker evidence available, so no gate
can be asserted, and `uncategorized/` is exactly where the policy puts material
whose category is not clear. `commercials_us_spot` and the decade keys still
reach it; no kids or daytime key does.

The decade *is* knowable -- it is the leading year in the reel filename, which
is the same rule `file_us_commercials.decade` already applies to the spots that
were filed individually.

## Why the twin containers are skipped

Four reels are staged twice, once as `.ia.mp4` and once as `.mkv`, with
identical durations and sizes within a rounding error -- the archive.org
derivative alongside its source. Splitting both would double every spot in
them. The `.mp4` is kept because the rest of the tree is `.mp4`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scripts import config

STAGE = config.STAGE_US_COMMERCIALS
CACHE = config.REEL_CUT_CACHE
DEST = config.COMMERCIALS_US

# Detector settings. Part of the cache key -- see the module docstring.
BLACK_MIN_DURATION = 0.04   # one frame at 25fps, so a single black frame counts
BLACK_PICTURE_RATIO = 0.98  # fraction of the frame that must be below pix_th
BLACK_PIXEL_THRESHOLD = 0.10
SILENCE_NOISE_DB = -50
SILENCE_MIN_DURATION = 0.20

# A silence boundary is ignored when a black boundary already sits this close.
# Wider than the longest black interval seen in calibration (4.4s) would merge
# genuinely distinct cuts, narrower than ~2s double-counts the common case of
# silence starting partway into a black field.
SILENCE_MERGE_WINDOW = 2.5

MIN_SECONDS = 8.0    # below this it is a fragment, not a spot
MAX_SECONDS = 125.0  # above this it is two spots or program content

VIDEO = {".mp4", ".mkv", ".avi", ".mpg", ".mpeg", ".m4v", ".webm", ".mov", ".ts"}

BLACK_RE = re.compile(r"black_start:(\d+(?:\.\d+)?)\s+black_end:(\d+(?:\.\d+)?)")
SILENCE_START_RE = re.compile(r"silence_start:\s*(-?\d+(?:\.\d+)?)")
SILENCE_END_RE = re.compile(r"silence_end:\s*(\d+(?:\.\d+)?)")


def detector_signature() -> str:
    """Settings fingerprint, so a retune invalidates the cache."""
    return (f"b{BLACK_MIN_DURATION}_{BLACK_PICTURE_RATIO}_{BLACK_PIXEL_THRESHOLD}"
            f"_s{SILENCE_NOISE_DB}_{SILENCE_MIN_DURATION}")


def duration(path: Path) -> float:
    """Seconds, or 0.0 if ffprobe cannot read the file."""
    try:
        out = subprocess.run(
            [config.FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=120)
        return float(out.stdout.strip() or 0)
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def detect(path: Path) -> dict:
    """Run one decoding pass and return {'black': [...], 'silence': [...]}.

    Both filters run in the same pass because the decode -- not the filtering --
    is what costs, and running them separately would double 30 hours of it.
    ffmpeg writes filter output to stderr interleaved, so the two are parsed
    from one stream.

    silence_start with no matching silence_end means the file ended mid-silence;
    it is closed at the file duration rather than dropped, because a reel whose
    tail is silent still has a real boundary there.
    """
    cmd = [
        config.FFMPEG, "-hide_banner", "-nostats", "-i", str(path),
        "-vf", (f"blackdetect=d={BLACK_MIN_DURATION}"
                f":pic_th={BLACK_PICTURE_RATIO}"
                f":pix_th={BLACK_PIXEL_THRESHOLD}"),
        "-af", f"silencedetect=n={SILENCE_NOISE_DB}dB:d={SILENCE_MIN_DURATION}",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr.strip().splitlines()[-1:] or ["ffmpeg failed"]}

    black, silence, open_silence = [], [], None
    for line in proc.stderr.splitlines():
        m = BLACK_RE.search(line)
        if m:
            black.append([float(m.group(1)), float(m.group(2))])
            continue
        m = SILENCE_START_RE.search(line)
        if m:
            open_silence = max(0.0, float(m.group(1)))
            continue
        m = SILENCE_END_RE.search(line)
        if m and open_silence is not None:
            silence.append([open_silence, float(m.group(1))])
            open_silence = None

    total = duration(path)
    if open_silence is not None and total > open_silence:
        silence.append([open_silence, total])

    return {"black": black, "silence": silence, "duration": total}


def cache_path(reel: Path) -> Path:
    return CACHE / f"{reel.stem}.{detector_signature()}.json"


def load_or_detect(reel: Path, refresh: bool) -> dict:
    """Read the cached detection for one reel, running it if absent."""
    cp = cache_path(reel)
    if cp.exists() and not refresh:
        try:
            return json.loads(cp.read_text())
        except (OSError, ValueError):
            pass  # unreadable cache is re-detected, not fatal
    data = detect(reel)
    CACHE.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(data))
    return data


def cuts_from(data: dict) -> list:
    """Merge black and silence intervals into a sorted list of cut points.

    Black contributes its midpoint. Silence contributes its midpoint only when
    no black cut already sits within SILENCE_MERGE_WINDOW -- see the docstring
    on why the two are not equal evidence.
    """
    points = sorted((a + b) / 2 for a, b in data.get("black", []))
    for a, b in data.get("silence", []):
        mid = (a + b) / 2
        if not any(abs(mid - p) <= SILENCE_MERGE_WINDOW for p in points):
            points.append(mid)
    return sorted(points)


def segments_for(reel: Path, data: dict,
                 min_seconds: float = MIN_SECONDS,
                 max_seconds: float = MAX_SECONDS) -> tuple:
    """Return (kept, dropped) segments as (start, end) second pairs.

    The head and tail of the reel are segments too: a capture that starts on a
    spot already in progress is dropped by the length filter like any other bad
    segment, and one that starts cleanly is a spot like any other.
    """
    total = data.get("duration") or 0.0
    if total <= 0:
        return [], []

    bounds = [0.0] + cuts_from(data) + [total]
    kept, dropped = [], []
    for start, end in zip(bounds, bounds[1:]):
        length = end - start
        if length < min_seconds or length > max_seconds:
            if length > 0.5:  # sub-half-second slivers are noise, not findings
                dropped.append((start, end))
            continue
        kept.append((start, end))
    return kept, dropped


def decade(name: str):
    """Leading year in the reel filename -> '90s'. Same rule as the filer."""
    m = re.match(r"^(19|20)(\d)", name)
    return f"{m.group(2)}0s" if m else None


def reels(stage: Path) -> list:
    """Staged reels worth splitting, twin containers resolved to one.

    Twins are matched on duration and size rather than on the `.ia` suffix, so
    a future pair staged under different names is caught too. Size is compared
    with a tolerance, not for equality: the four known pairs are the same
    recording in two containers and differ by 0.3-0.5% of muxing overhead, so
    an exact -- or megabyte-rounded -- comparison misses three of the four.
    Duration carries the real weight here; size only guards against two
    genuinely different reels that happen to run the same length.
    """
    candidates = [p for p in sorted(stage.iterdir())
                  if p.is_file() and p.suffix.lower() in VIDEO]
    measured = {p: (duration(p), p.stat().st_size) for p in candidates}

    chosen = []
    for p in candidates:
        secs, size = measured[p]
        twin = next(
            (q for q in chosen
             if abs(measured[q][0] - secs) < 0.5
             and abs(measured[q][1] - size) <= 0.02 * max(size, 1)),
            None)
        if twin is None:
            chosen.append(p)
        elif p.suffix.lower() == ".mp4" and twin.suffix.lower() != ".mp4":
            # Prefer .mp4; the rest of the tree is .mp4.
            chosen[chosen.index(twin)] = p
    return chosen


def cut(src: Path, start: float, end: float, dest: Path, threads: int) -> bool:
    """Re-encode one segment. Returns True on success.

    Stream copy is not an option: it can only cut on keyframes, and these
    captures run 250-frame GOPs, so every boundary would drift by up to eight
    seconds and take the neighbouring spot's head with it. The sources are all
    SD (960x720 at the largest), so a re-encode is cheap and CRF 20 is visually
    transparent against tape-sourced material.

    `-ss` before `-i` seeks by index and is the fast form; with a re-encode
    following it, it is also frame-accurate.

    `-threads` is set explicitly because libx264 otherwise sizes its pool to
    the whole machine. With one job that is right and with twelve it is
    catastrophic -- the first run of this drove a 16-core box to a load average
    of 84 and cut roughly ten spots a minute. Threads times jobs is the budget.

    The write goes to a `.partial` sibling and is renamed only on success, so
    an interrupted run leaves nothing behind that the `dest.exists()` skip in
    `main` would later mistake for finished work. Rename within a directory is
    atomic, so a segment is either absent or complete.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".partial.mp4")
    cmd = [
        config.FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{start:.3f}", "-i", str(src), "-t", f"{end - start:.3f}",
        "-threads", str(threads),
        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-f", "mp4", str(tmp),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tmp.unlink(missing_ok=True)
        print(f"  !! cut failed {dest.name}: {proc.stderr.strip().splitlines()[-1:]}")
        return False
    tmp.rename(dest)
    return True


def histogram(lengths: list) -> list:
    """Segment lengths bucketed against the shapes a US spot actually comes in."""
    buckets = [(0, 10, "<10s"), (10, 20, "10-20s (ident/15s)"),
               (20, 40, "20-40s (the 30s spot)"), (40, 70, "40-70s (the 60s spot)"),
               (70, 125, "70-125s (promo/block)")]
    return [(label, sum(1 for x in lengths if lo <= x < hi))
            for lo, hi, label in buckets]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--apply", action="store_true", help="actually write the segments")
    ap.add_argument("--refresh", action="store_true", help="re-run detection, ignoring cache")
    ap.add_argument("--jobs", type=int, default=8, help="parallel ffmpeg processes")
    ap.add_argument("--threads", type=int, default=2,
                    help="encoder threads per job; jobs*threads should not exceed cores")
    ap.add_argument("--only", help="substring filter on reel filename")
    ap.add_argument("--min-seconds", type=float, default=MIN_SECONDS,
                    help="shorter segments are fragments. Commercials 8; bumpers run 3-10, "
                         "so a bumper pass wants ~3")
    ap.add_argument("--max-seconds", type=float, default=MAX_SECONDS,
                    help="longer segments are two spots or programme content")
    ap.add_argument("--stage", default=str(STAGE), help="directory of reels to split")
    ap.add_argument("--dest", default=str(DEST), help="destination root")
    ap.add_argument("--flat", action="store_true",
                    help="file straight into --dest with no <decade>/<gate> levels, "
                         "and no leading-year requirement (bumpers, idents)")
    args = ap.parse_args()

    stage = Path(args.stage)
    dest_root = Path(args.dest)
    if not stage.is_dir():
        sys.exit(f"staging not found: {stage}")

    todo = reels(stage)
    if args.only:
        todo = [p for p in todo if args.only.lower() in p.name.lower()]
    if not todo:
        sys.exit("no reels matched")

    print(f"reels: {len(todo)}  (detector {detector_signature()})")
    uncached = [p for p in todo if not cache_path(p).exists() or args.refresh]
    if uncached:
        print(f"detecting {len(uncached)} (this decodes them in full)...")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        detections = list(pool.map(lambda p: load_or_detect(p, args.refresh), todo))

    plan, stats, lengths, failed = [], Counter(), [], []
    for reel, data in zip(todo, detections):
        if "error" in data:
            failed.append((reel, data["error"]))
            continue
        dec = None
        if not args.flat:
            dec = decade(reel.name)
            if dec is None:
                stats["reels skipped (undated)"] += 1
                continue
        kept, dropped = segments_for(reel, data, args.min_seconds, args.max_seconds)
        stats["segments kept"] += len(kept)
        stats["segments dropped"] += len(dropped)
        for i, (start, end) in enumerate(kept, 1):
            lengths.append(end - start)
            name = f"{reel.stem} - {i:03d}.mp4"
            out = dest_root / name if args.flat else dest_root / dec / "uncategorized" / name
            plan.append((reel, start, end, out))

    by_decade = Counter("flat" if args.flat else d.parent.parent.name
                        for _, _, _, d in plan)
    kept_hours = sum(lengths) / 3600

    print(f"\nspots: {len(plan)}   ({kept_hours:.1f}h kept of "
          f"{sum(d.get('duration', 0) for d in detections) / 3600:.1f}h staged)")
    print("\nby decade:")
    for k in sorted(by_decade):
        print(f"  {k:<8} {by_decade[k]}")
    print("\nlengths:")
    for label, n in histogram(lengths):
        print(f"  {label:<22} {n}")
    print("\ntotals:")
    for k, v in stats.most_common():
        print(f"  {k:<24} {v}")
    if failed:
        print(f"\ndetection failed on {len(failed)}:")
        for reel, err in failed:
            print(f"  {reel.name}: {err}")

    if not args.apply:
        print("\nre-run with --apply to write the segments.")
        return

    done = Counter()

    def write(item):
        reel, start, end, dest = item
        if dest.exists():
            return "already there"
        return "written" if cut(reel, start, end, dest, args.threads) else "failed"

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for result in pool.map(write, plan):
            done[result] += 1

    print("\napplied:")
    for k, v in done.most_common():
        print(f"  {k:<14} {v}")


if __name__ == "__main__":
    main()
