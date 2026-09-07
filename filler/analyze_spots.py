#!/usr/bin/env python3
"""
analyze_spots.py — transcribe and frame each spot so it can actually be gated.

Read-only over the library. Writes only into --out; moves nothing, gates
nothing. `apply_gates.py` is the thing that moves files, and it reads this.

## The problem this solves

`recategorize_commercials.gate()` matches regexes against a *filename*. For the
individually-acquired spots that was weak evidence; for the 3,721 cut out of
off-air reels it is no evidence at all, because every segment of a reel inherits
one name that describes the programme the break was recorded from. That is why
`split_reels.py` files all of them to `uncategorized/`, which no kids or daytime
key draws from.

The same regexes against a **transcript** are a different proposition. A 30-second
spot is 60-80 words and says its own brand name aloud, usually more than once.
Measured on five spots from the 1980-04-18 NBC reel, `base.en` returned "Scope",
"Manor House Coffee ... from Dominick's", "New Del Monte light fruits", "1980
Chevy Camaro", and a promo reading "It's a special two-hour BJ ... Saturday at
8, 7 Central" -- every one of which is the determination the gate needs and none
of which is in any filename.

So this does not invent a new classifier. It gives the existing one something to
read.

## Why frames as well as audio

They fail differently, which is the point. Audio misses a silent title card and
mangles brand names it has never heard ("Matter House" for Manor House). A frame
misses anything stated only in voiceover, and it misses the last two seconds --
which is exactly where the Winston/Flintstones spot hides its determination.
Neither alone is sufficient; §5 of the taxonomy learned that the expensive way.

The frame is sampled at 65% rather than the midpoint because commercials are
built to end on the pack shot and the logo.

## Why the gate is only ever *suggested*

`gate()` returning "kids" from a transcript is still an inference from a
lossy transcript of a noisy tape. This writes it to a `suggested_gate` field and
stops. A suggestion is a queue to review, not a determination -- and the
asymmetry from the taxonomy still holds: a false gate withholds a spot from a
daypart, while the opposite error airs beer in one. Nothing here is allowed to
make the second mistake unattended.

## Cost

`base.en` at int8 on CPU runs a 30-second spot in a few seconds, and the work is
embarrassingly parallel. The transcript is cached per file, so a re-run after a
regex change costs nothing -- which matters, because the regexes *will* change
once the first few hundred transcripts are read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Sibling module in this directory. Python puts the running script's own
# directory on sys.path, so no path manipulation is needed to reach it -- and
# `gate` must come from here rather than be reimplemented, because it is the
# single source of truth for what a gate means.
from recategorize_commercials import gate

# Imported at module scope so a missing dependency fails immediately and
# visibly, rather than after the caller has waited through a decode pass.
try:
    from faster_whisper import WhisperModel
except ImportError:  # reported in main(), where we can name the venv
    WhisperModel = None

FILLER = Path("/media/filler")


def duration(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=60)
        return float(out.stdout.strip() or 0)
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def extract_audio(video: Path, wav: Path) -> bool:
    """16 kHz mono PCM — what the model wants, and it avoids a second decode
    inside the transcriber for every file."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
           "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def extract_frame(video: Path, jpg: Path, secs: float, at: float = 0.65) -> bool:
    """One representative frame from around `at` of the spot."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-ss", f"{max(0.0, secs * at):.2f}", "-i", str(video),
           "-vf", "thumbnail=n=30,scale=320:240:force_original_aspect_ratio=decrease,"
                  "pad=320:240:(ow-iw)/2:(oh-ih)/2:color=black",
           "-frames:v", "1", str(jpg)]
    return subprocess.run(cmd, capture_output=True).returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--glob", default="commercials/us/*/uncategorized/*.mp4",
                    help="pattern under the filler root")
    ap.add_argument("--out", required=True, help="directory for cache and results")
    ap.add_argument("--model", default="base.en",
                    help="faster-whisper model; base.en is the accuracy/speed knee here")
    ap.add_argument("--jobs", type=int, default=6, help="parallel decode workers")
    ap.add_argument("--limit", type=int, default=0, help="0 = all matches")
    ap.add_argument("--no-frames", action="store_true", help="transcripts only")
    args = ap.parse_args()

    if WhisperModel is None:
        sys.exit("faster-whisper is not importable.\n"
                 "Run with the project venv: "
                 "<project>/.venv/bin/python")

    out = Path(args.out)
    (out / "frames").mkdir(parents=True, exist_ok=True)
    (out / "audio").mkdir(parents=True, exist_ok=True)
    # Cache is scoped to the model. Keying on path alone would make a re-run
    # under a different model silently reuse the old one's output -- the exact
    # failure that would make a base.en/small.en comparison meaningless.
    cache_path = out / f"transcripts.{args.model}.json"
    if not cache_path.exists() and args.model == "base.en" and (out / "transcripts.json").exists():
        # Migrate the pre-model-scoped cache rather than re-transcribe 4,075 spots.
        legacy = json.loads((out / "transcripts.json").read_text())
        cache_path.write_text(json.dumps(
            {k: {"text": v, "logprob": None} for k, v in legacy.items()}, indent=1))
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    videos = sorted(FILLER.glob(args.glob))
    if args.limit:
        videos = videos[: args.limit]
    if not videos:
        sys.exit(f"no videos matched {args.glob!r} under {FILLER}")

    todo = [v for v in videos if str(v) not in cache]
    print(f"{len(videos)} spots, {len(todo)} to transcribe "
          f"({len(videos) - len(todo)} cached)")

    # Decode is parallel and IO/CPU bound; transcription is one model, used
    # serially. Splitting them keeps the model off N cores at once, which on
    # int8 CPU is slower rather than faster.
    if todo:
        def prep(v: Path):
            # Stable digest, not hash(): str hashing is salted per process, so
            # an interrupted run would orphan wavs a re-run could never match.
            wav = out / "audio" / f"{hashlib.sha1(str(v).encode()).hexdigest()[:16]}.wav"
            return v, (wav if extract_audio(v, wav) else None)

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            prepared = list(pool.map(prep, todo))

        model = WhisperModel(args.model, device="cpu", compute_type="int8")
        for n, (v, wav) in enumerate(prepared, 1):
            if wav is None:
                cache[str(v)] = {"text": "", "logprob": None}
                continue
            segs, _ = model.transcribe(str(wav), beam_size=1, vad_filter=True)
            segs = list(segs)
            # avg_logprob is the single best trust signal measured so far: on a
            # 24-spot evaluation it flagged both unusable transcripts and
            # nothing else. It is free here and unrecoverable later.
            cache[str(v)] = {
                "text": " ".join(s.text.strip() for s in segs).strip(),
                "logprob": (sum(s.avg_logprob for s in segs) / len(segs)) if segs else None,
            }
            wav.unlink(missing_ok=True)
            if n % 25 == 0 or n == len(prepared):
                print(f"  transcribed {n}/{len(prepared)}")
                cache_path.write_text(json.dumps(cache, indent=1))
        cache_path.write_text(json.dumps(cache, indent=1))

    index, counts = [], Counter()
    for n, v in enumerate(videos):
        entry = cache.get(str(v)) or {}
        text = entry.get("text", "")
        logprob = entry.get("logprob")
        secs = duration(v)
        # The gate reads the transcript, not the filename -- the whole point.
        suggested = gate(text) if text else "uncategorized"
        counts[suggested] += 1
        entry = {"id": n, "path": str(v), "secs": round(secs, 1),
                 "suggested_gate": suggested, "transcript": text,
                 "logprob": logprob, "model": args.model}
        if not args.no_frames:
            jpg = out / "frames" / f"{n:05d}.jpg"
            if not jpg.exists():
                extract_frame(v, jpg, secs)
            entry["frame"] = str(jpg)
        index.append(entry)

    index_path = out / f"index.{args.model}.json"
    index_path.write_text(json.dumps(index, indent=1))

    print(f"\nsuggested gates over {len(index)} spots:")
    for k, v in counts.most_common():
        print(f"  {k:<16} {v}")
    print(f"\nwrote {index_path}")
    print("nothing was moved. Review, then use apply_gates.py.")


if __name__ == "__main__":
    main()
