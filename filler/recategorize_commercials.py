#!/usr/bin/env python3
"""
recategorize_commercials.py — re-gate US spots on a positive test.

Dry-run by default. Nothing moves unless --apply is passed.

The first pass filed anything that matched no kids or mature keyword into
`general/`, which made that gate a *residual* rather than a determination. That
is the error the Winston/Flintstones spot exists to warn about: a filename tells
you almost nothing about what is in a commercial, so "nothing matched" is not
evidence of anything.

The rule here is the inverse. A spot is categorized only when the category is
clear -- a named consumer brand, a named children's property -- and everything
else goes to `uncategorized/`, which no daytime or kids key draws from. Channels
that want the whole reel ask for it explicitly.

This moves roughly half of `general/` out, because the collection is not what it
says on the tin: a large share is network promos (Dolly, Wings, Sister Sister),
movie TV spots (The Wiz, Mystic Pizza) and PSAs. None of those is a commercial
with a category, and a promo tells you nothing about the rated content it
advertises.

`unverified/` is folded into `uncategorized/`. Two names for "we do not know"
is one too many.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

from scripts import config

DEST = config.COMMERCIALS_US

# Structural markers. A promo advertises something whose content we cannot see,
# so it is not categorized -- unless it names an unambiguous children's property,
# which is itself the determination.
PROMO = re.compile(r"promo|tv\s*spot|trailer|\bpsa\b|bumpers|preview|miniseries", re.I)

# The public-domain set was classified from extracted frames, which is stronger
# evidence than any filename gives. `ctvc_RICECRPS` and `ctvc_KAISER` are Rice
# Krispies and a Maverick mail-in premium; no regex over those names would say
# so. Keep the determinations explicitly rather than re-deriving them badly.
CTVC = {
    "CHESTER": "tobacco", "FLINT": "tobacco", "LNM": "tobacco",
    "LNM02": "tobacco", "MORRIS": "tobacco", "ROYTAN": "tobacco",
    "RICECRPS": "kids", "KAISER": "kids", "ZORRO": "kids",
    "BAYER": "general", "DESOTO": "general", "FOAMY": "general",
    "GENERL01": "general", "GENERL02": "general", "GLO": "general",
    "GRAPENUT": "general", "HALO": "general", "JELLO": "general",
    "JOE": "general", "LIPTON": "general", "MILKOMAG": "general",
    "PET01": "general", "PET02": "general", "PLAYTEX": "general",
    "PROM": "general", "PUSS": "general", "SHOE": "general",
    "SOFTIQUE": "general", "TEXACO": "general", "TORNADO": "general",
    "VWBUG": "general", "Vitalis": "general", "ZENITH": "general",
    # Product never identifiable from the frames.
    "COPE": "uncategorized", "KEATON": "uncategorized",
    "LUSTER": "uncategorized", "STOOGIES": "uncategorized",
}

# Hard override, ahead of every brand match. "Pepsi Cool Sex Cans" carries a
# brand this file would otherwise pass into daytime.
MATURE = re.compile(r"""
    1-900 | 1\s*900 | \bsex\b | abortion | harassment | \bayds\b | underwear
  | sheer\s*indulgence | without\s*his\s*pants | \bdrug\b | \bbadd\b
  | cancer\s*society | prevent\s*crime | ghosts\s*of\s*fear | \bcarrie\b
  | oh\s*god\s*you\s*devil | stephen\s*king | \bg\s*vs\s*e\b | outrage
  | baby\s*jane | dial\s*an\s*insult
""", re.I | re.X)

BREAK = re.compile(r"commercials?\s*\(\s*from|\bfrom\s+(abc|cbs|nbc|fox|the\s+wb)\b", re.I)

CHRISTMAS = re.compile(r"christmas|santa|holiday\s*season", re.I)

# Named children's properties. Unambiguous enough to survive a promo marker: a
# Bugs Bunny / Garfield / Charlie Brown promo is Saturday morning either way.
KIDS = re.compile(r"""
    barbie | nintendo | gameboy | game\s*genie | gargoyles\s*action | fruity\s*pebbles
  | happy\s*meal | small\s*soldiers | superfriends | mac\s*and\s*cheese | kids\s*wb
  | one\s*saturday\s*morning | muppets | scooby | lilo\s*and\s*stitch | pufnstuf
  | flintstone\s*kids | crispy\s*wheats | tobor | bugs\s*bunny | garfield
  | charlie\s*brown | jim\s*hensons? | animal\s*show | dog\s*city | brady\s*bunch
  | partridge | beauty\s*and\s*the\s*beast
""", re.I | re.X)

# Named consumer brands. Explicit by design: "clear" means the product can be
# named, so the list is the definition of the gate rather than a heuristic.
BRANDS = re.compile(r"""
    coca\s*cola | new\s*coke | diet\s*pepsi | pepsi | canada\s*dry | carnation
  | \btide\b | duncan\s*hines | campbells | folgers | head\s*and\s*shoulders
  | maxell | jc\s*penney | reisen | amiga | kodak | jack\s*in\s*the\s*box
  | kibbles | \bpert\b | target | volkswagon | volkswagen | m&ms | mcdonalds
  | burger\s*king | krafft | kraft | \bmilk\b | yamaha
""", re.I | re.X)


def gate(name: str) -> str:
    stem = re.sub(r"\.(mp4|mkv|avi)$", "", name, flags=re.I)
    stem = re.sub(r"\.ia$", "", stem, flags=re.I)

    if stem.startswith("ctvc_"):
        return CTVC.get(stem[5:], "uncategorized")
    # An off-air break recorded during a show carries whatever the network aired
    # that night, so the show's name says nothing about the contents. Without
    # this, "Commercials (from ABC's Brady Bunch Hour)" -- 28 minutes of 1977
    # advertising -- would gate as children's content on the title alone.
    if BREAK.search(stem):
        return "uncategorized"
    if MATURE.search(stem):
        return "uncategorized"
    if CHRISTMAS.search(stem):
        return "christmas"
    if KIDS.search(stem):
        return "kids"
    if PROMO.search(stem):
        return "uncategorized"
    if BRANDS.search(stem):
        return "general"
    return "uncategorized"


def plan():
    moves = []
    for f in sorted(DEST.rglob("*")):
        if not f.is_file():
            continue
        decade = f.relative_to(DEST).parts[0]
        current = f.parent.name
        # Never re-gate the one hand-placed alcohol spot.
        if "alcohol" in f.relative_to(DEST).parts:
            continue
        want = gate(f.name)
        if current != want:
            moves.append((f, DEST / decade / want / f.name, current, want))
    return moves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=0)
    args = ap.parse_args()
    if not DEST.is_dir():
        sys.exit(f"missing: {DEST}")

    moves = plan()
    flow = Counter(f"{c} -> {w}" for _, _, c, w in moves)
    print(f"re-gating {len(moves)} files\n")
    for k, v in flow.most_common():
        print(f"  {k:<28} {v}")

    if args.show:
        for k in flow:
            print(f"\n{k}:")
            for src, _, c, w in moves:
                if f"{c} -> {w}" == k:
                    print(f"  {src.name[:70]}")
                    args.show -= 1
                    if args.show <= 0:
                        break
            break

    if not args.apply:
        print("\nre-run with --apply to move.")
        return

    done = Counter()
    for src, dst, _, _ in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        done["moved"] += 1
    # drop the dirs the re-gate emptied
    for d in sorted(DEST.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            done["empty dirs removed"] += 1
    print("\napplied:")
    for k, v in done.items():
        print(f"  {k:<20} {v}")


if __name__ == "__main__":
    main()
