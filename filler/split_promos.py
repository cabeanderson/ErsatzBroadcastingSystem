#!/usr/bin/env python3
"""
split_promos.py — move promos out of the commercial tree into promos/.

Dry-run by default. Nothing moves unless --apply is passed.

## Why promos are not commercials

§6 of interstitial-policy.md draws the distinction on truth conditions. A bumper
("you're watching Toonami") and a commercial ("buy Rice Krispies") cannot be
false. A promo ("30 Rock, Thursdays at 8") **claims a future airing**, and that
claim can be wrong. Filing one as a commercial is already a mislabel; the reel
split produced hundreds of them sitting in `commercials/us/`.

§6 argued *against* moving the Toonami `next` files to a promos tree, and that
reasoning does not transfer. Those files sit correctly inside a network's bumper
tree and would lose the `bumpers` tag `play_smart_bumper` needs. These sit in
the commercial tree wearing the wrong label already.

## Why the claim type is a folder level

The four claims want different scheduling, so each must be addressable alone:

| Claim | Truth condition | Where it can air |
|---|---|---|
| `relative` | true **by placement** — "coming up next" | before the thing it names |
| `day` | satisfiable — "Thursday nights" | on that weekday |
| `dated` | falsifiable — "Saturday at 8" | only where the grid agrees |
| `untimed` | no claim at all | anywhere |

Only `dated` can be wrong, and it is **37 files of 325**. Making it one folder
means the decision to keep or discard it is one `rm -r`, taken later, on
evidence — rather than a policy argument taken now.

## Why the decade level is kept

`promos/us/<decade>/<claim>/`, not `promos/<claim>/`. A promo's era is the whole
point of it — a 1980 NBC promo is period signal for Good Times and noise
anywhere else — and the decade is already known from the source reel. Dropping
the level would throw away the one fact that makes these schedulable.

## Why programme evidence is required, not just a time word

A first pass classified on time words alone and returned 857 spots, of which 646
were `day`. That was mostly wrong: "All week long, Kohl's is offering great
savings ... this Thursday" is a retail ad naming a sale date, and "our newest
summer attraction ... all new" is a car dealership. A promo advertises a
*programme*, so `PROGRAMME` evidence is now a gate and `RETAIL` language vetoes a
weak match. The count fell to 325, and `day` from 646 to 213.

## The NFO consequence

Tags are derived from the path, so a moved file's NFO is stale the moment it
moves: it would still claim `commercials` and its old gate. This deletes the old
sidecar and re-runs the generator over the new tree, rather than trying to
rewrite XML in place.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

FILLER = Path("/media/filler")
DEST = FILLER / "promos"

DAY = re.compile(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday'
                 r'|weeknights?|weekdays?)\b', re.I)
CLOCK = re.compile(r'\b\d{1,2}(:\d{2})?\s*(o.clock\s*)?(am|pm|central|eastern'
                   r'|pacific|mountain)\b', re.I)
RELATIVE = re.compile(r'\b(coming up next|up next|next on|right after this'
                      r'|stay tuned|tonight on|later on)\b', re.I)
TUNE_IN = re.compile(r'\b(tune in|premieres?|series premiere|don.t miss)\b', re.I)

# A time word alone does not make a promo. "All week long, Kohl's is offering
# great savings ... this Thursday" is a retail ad that names a weekday, and a
# first pass classified 646 spots as `day` promos largely on that basis. A promo
# advertises a *programme*, so it must carry programme evidence as well as a
# time claim.
PROGRAMME = re.compile(
    r'\b(on (abc|cbs|nbc|fox|the wb|upn|pbs|tnt|tbs|hbo|showtime|mtv|nickelodeon)'
    r'|(abc|cbs|nbc|fox|the wb|upn) (monday|tuesday|wednesday|thursday|friday|saturday|sunday|night)'
    r'|all new episode|new episode|season (premiere|finale)|series (premiere|finale)'
    r'|episode|mini.?series|the season|this season|next week on|tonight on|next on'
    r'|coming up next|up next|stay tuned|watch .{0,20}(tonight|tomorrow)'
    r'|movie of the week|world premiere|only on)\b', re.I)

# Retail and dealership language. Present without programme evidence, a time
# word is a sale date, not an airtime.
RETAIL = re.compile(
    r'\b(sale|save|savings|% off|percent off|dealer|dealership|store|stores'
    r'|prices?|coupon|rebate|clearance|financing|lease|limited time offer)\b', re.I)


def claim(transcript: str):
    """The strongest claim the transcript makes, or None.

    Order matters and is by falsifiability, not by regex convenience: a spot
    saying "Saturday at 8" is `dated` even though it also matches `day`,
    because the tighter claim is the one that can be wrong.
    """
    if not transcript.strip():
        return None
    # Programme evidence is the gate. Without it a time word is a sale date.
    if not PROGRAMME.search(transcript):
        return None
    # Retail language outranks a weak programme match: "only on" and "episode"
    # both appear in car ads often enough to matter.
    if RETAIL.search(transcript) and not re.search(
            r'\b(tonight on|next on|coming up next|up next|all new episode'
            r'|season (premiere|finale)|series (premiere|finale))\b',
            transcript, re.I):
        return None
    day, clock = bool(DAY.search(transcript)), bool(CLOCK.search(transcript))
    if day and clock:
        return "dated"
    if day:
        return "day"
    if clock:
        return "clock"
    if RELATIVE.search(transcript):
        return "relative"
    if TUNE_IN.search(transcript):
        return "untimed"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--analysis", required=True, help="index.<model>.json")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=3, help="examples per claim")
    args = ap.parse_args()

    index = json.loads(Path(args.analysis).read_text())
    plan, stats, examples = [], Counter(), {}

    for e in index:
        src = Path(e["path"])
        c = claim(e.get("transcript", ""))
        if c is None:
            stats["stays a commercial"] += 1
            continue
        if not src.exists():
            stats["source missing"] += 1
            continue
        # commercials/us/<decade>/<gate>/file -> promos/us/<decade>/<claim>/file
        try:
            country, decade = src.parts[-4], src.parts[-3]
        except IndexError:
            stats["unexpected path"] += 1
            continue
        plan.append((src, DEST / country / decade / c / src.name))
        stats[c] += 1
        examples.setdefault(c, []).append(e.get("transcript", "")[:96])

    print(f"{len(index)} spots examined, {len(plan)} would move\n")
    for k in ("relative", "day", "dated", "clock", "untimed"):
        if not stats[k]:
            continue
        print(f"  {k:<10} {stats[k]:>5}")
        for s in examples.get(k, [])[: args.show]:
            print(f"        … {s}")
    print(f"\n  {'stays put':<10} {stats['stays a commercial']:>5}")
    for k in ("source missing", "unexpected path"):
        if stats[k]:
            print(f"  {k:<16} {stats[k]}")

    if not args.apply:
        print("\nre-run with --apply to move.")
        return

    # An undo/remap manifest. The in-flight small.en index keys transcripts by
    # path, so a move silently orphans them; this makes the remap possible
    # without re-transcribing, and makes the move reversible.
    manifest = DEST / "_moved_from.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(
        {str(dst): str(src) for src, dst in plan}, indent=1))

    done = Counter()
    for src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            done["already there"] += 1
            continue
        shutil.move(str(src), str(dst))
        # The sidecar encodes the old path's tags; it cannot be carried over.
        old_nfo = src.with_suffix(".nfo")
        if old_nfo.exists():
            old_nfo.unlink()
            done["stale nfo removed"] += 1
        done["moved"] += 1
    print("\napplied:")
    for k, v in done.most_common():
        print(f"  {k:<20} {v}")
    print("\nNow regenerate sidecars over the new tree:")
    print('  python3 filler/generate_filler_nfo.py --glob "promos/*/*/*/*.mp4" --verify')


if __name__ == "__main__":
    main()
