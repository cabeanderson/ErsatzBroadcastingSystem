#!/usr/bin/env python3
"""
transcript_gate.py — assign audience gates from transcripts, not filenames.

Dry-run by default. Nothing moves unless --apply is passed.

`recategorize_commercials.gate()` is left untouched. It reads filenames, it is
the single source of truth for the filename path, and re-running that filer
after widening its vocabulary could re-gate spots already filed. This is a
second, independent classifier over a second, much richer input.

It classified 6% of the reel corpus (243 of 4,075) precisely because a segment
cut from a reel inherits a filename describing the programme the break came
from. The transcript says what the advert actually says.

## The asymmetry that shapes everything here

The two directions of error are not comparable:

- **Gating a spot too tightly** withholds it from a daypart. The spot still
  exists, and something else fills the break. Cost: near zero.
- **Gating a spot too loosely** puts beer or a cigarette in a children's block.
  Cost: the thing the gate exists to prevent.

So the two directions get different rules, and this is the whole design:

| Direction | Rule |
|---|---|
| Into `alcohol` / `tobacco` (restrictive) | **auto-applied.** A false positive only withholds a spot from `commercials_family_safe_spot`, which is harmless |
| Into `kids` / `general` (permissive) | **never auto-applied.** These widen where a spot may air, so they are emitted as a review queue with evidence and nothing else |

`--apply` therefore moves *only* restrictive gates. Widening a gate stays a
human act, which is the same position `recategorize_commercials` took when it
made a gate a positive determination rather than a residue.

## Why evidence is recorded

Every suggestion carries the matched phrase. A reviewer needs to see *why* a
spot was nominated, and a gate assigned by a regex nobody can interrogate is the
"nothing matched, so it must be safe" mistake wearing a different hat.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path

FILLER = Path("/media/filler")

# Restrictive vocabularies. Tuned for recall -- a false positive costs a spot
# one daypart, a false negative is the failure mode the gate exists for.
ALCOHOL = re.compile(r"""
    \b(budweiser|bud light|miller (lite|genuine|high life)|coors|michelob|heineken
  | corona (extra|light)|molson|labatt|stroh|schlitz|pabst|old milwaukee|busch
  | beck.s|amstel|guinness|killian|rolling rock|natural light|keystone
  | smirnoff|bacardi|jack daniel|jim beam|seagram|absolut|captain morgan
  | jose cuervo|tanqueray|crown royal|canadian club|johnnie walker
  | bartles|wine cooler|zima|boone.s farm
  | \bbeer\b|\bbrewing\b|\bbrewery\b|\blager\b|\bale\b|light beer
  | \bvodka\b|\bwhiskey\b|\bwhisky\b|\brum\b|\btequila\b|\bbourbon\b|\bgin\b
  | \bliqueur\b|\bschnapps\b|\bchampagne\b|\bmerlot\b|\bchardonnay\b
  | drink responsibly|please drink|designated driver)\b
""", re.I | re.X)

TOBACCO = re.compile(r"""
    \b(winston|marlboro|camel (lights|filters)?|salem|newport|kool|virginia slims
  | benson . hedges|pall mall|lucky strike|chesterfield|tareyton|parliament
  | merit|vantage|carlton|more menthol|now cigarette
  | \bcigarettes?\b|\bsmoking\b|\bsmokers?\b|\btobacco\b|\bmenthol\b
  | surgeon general|low tar|filter cigarette)\b
""", re.I | re.X)

# Permissive vocabularies. These only ever produce a review queue.
KIDS = re.compile(r"""
    \b(barbie|lego|nintendo|sega|game boy|hot wheels|my little pony|transformers
  | cabbage patch|teddy ruxpin|nerf|play.doh|easy.bake|tonka|matchbox
  | happy meal|chuck e cheese|fruity pebbles|cocoa puffs|lucky charms|trix
  | frosted flakes|cap.n crunch|kix|cheerios|pop.tarts|kool.aid|capri sun
  | saturday morning|kids wb|one saturday morning|toys r us
  | \btoy\b|\btoys\b|action figure|collect them all|ask your parents)\b
""", re.I | re.X)

CHRISTMAS = re.compile(r"""
    \b(christmas|santa|st\.? nick|reindeer|mistletoe|jingle bell|silent night
  | holiday season|deck the halls|merry christmas|christmas eve)\b
""", re.I | re.X)

# Brand-level evidence. A named brand is a determination; a category word is
# not. This split exists because the first pass auto-applied on category words
# and nominated an anti-smoking PSA ("quit smoking today and your heart will
# thank you") as tobacco, and a Despicable Me trailer ("vodka diva, vodka!") as
# alcohol. Both are the inverse of what the gate means.
ALCOHOL_BRAND = re.compile(r"""
    \b(budweiser|bud light|miller (lite|genuine|high life)|coors|michelob|heineken
  | corona (extra|light)|molson|labatt|stroh|schlitz|pabst|old milwaukee|busch
  | beck.s|amstel|guinness|rolling rock|natural light|keystone
  | smirnoff|bacardi|jack daniel|jim beam|seagram|absolut|captain morgan
  | jose cuervo|tanqueray|crown royal|canadian club|johnnie walker
  | bartles|wine cooler|zima|boone.s farm|apple ale
  | killian.s (irish )?red
  | drink responsibly|please drink|designated driver)\b
""", re.I | re.X)

TOBACCO_BRAND = re.compile(r"""
    \b(winston|marlboro|camel (lights|filters)|salem|newport|virginia slims
  | kool(?!\s*-?\s*aid)(?!\s*aid)
  | benson . hedges|pall mall|lucky strike|chesterfield|tareyton|parliament
  | surgeon general|low tar|filter cigarette)\b
""", re.I | re.X)

# A PSA is not an advert for the thing it names. Vetoes a category-word match.
COUNTER_ADVERT = re.compile(
    r"\b(quit smoking|stop smoking|second.?hand smoke|truth\.com|above the influence"
    r"|don.t drink and drive|drunk driving|underage drinking|say no to"
    r"|partnership for a drug.free|this is your brain)\b", re.I)

RESTRICTIVE = {"alcohol": ALCOHOL_BRAND, "tobacco": TOBACCO_BRAND}
# Category words nominate for review rather than determine.
REVIEW_ONLY = {"alcohol?": ALCOHOL, "tobacco?": TOBACCO,
               "kids": KIDS, "christmas": CHRISTMAS}
PERMISSIVE = REVIEW_ONLY


def classify(text: str):
    """Return (gate, evidence) or (None, None).

    Restrictive gates are tested first and win outright: a beer advert that also
    says "christmas" is an alcohol advert, and the whole point of the gate is
    that the restrictive reading governs.
    """
    if not text.strip():
        return None, None
    # A public-service announcement names the thing it argues against, so it
    # must be excluded before any vocabulary is consulted.
    if COUNTER_ADVERT.search(text):
        return "psa?", COUNTER_ADVERT.search(text).group(0)
    for name, pat in RESTRICTIVE.items():
        m = pat.search(text)
        if m:
            return name, m.group(0)
    for name, pat in REVIEW_ONLY.items():
        m = pat.search(text)
        if m:
            return name, m.group(0)
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--analysis", required=True, help="index.<model>.json")
    ap.add_argument("--out", help="write the review queue here as JSON")
    ap.add_argument("--apply-reviewed", metavar="QUEUE",
                    help="move files listed in a reviewed queue JSON. The queue must "
                         "have been checked by a human: brand-level evidence alone "
                         "mislabelled Kool-Aid as tobacco and a character named "
                         "Killian as beer")
    ap.add_argument("--show", type=int, default=4)
    args = ap.parse_args()

    index = json.loads(Path(args.analysis).read_text())
    stats, examples, moves, queue = Counter(), {}, [], []

    for e in index:
        src = Path(e["path"])
        # Only re-gate what is currently undetermined; a spot already gated by
        # frame evidence or filename is better evidence than this.
        if src.parent.name != "uncategorized" or not src.exists():
            continue
        gate, why = classify(e.get("transcript", ""))
        if gate is None:
            stats["no determination"] += 1
            continue
        stats[gate] += 1
        examples.setdefault(gate, []).append((why, e.get("transcript", "")[:80]))
        row = {"path": str(src), "gate": gate, "evidence": why,
               "transcript": e.get("transcript", "")}
        # Everything is a nomination. Nothing here is a determination.
        queue.append(row)

    print(f"{stats['no determination'] + sum(stats[g] for g in list(RESTRICTIVE) + list(REVIEW_ONLY) + ['psa?'])}"
          f" uncategorized spots examined\n")
    print("RESTRICTIVE — auto-applied with --apply (safe direction):")
    for g in RESTRICTIVE:
        print(f"  {g:<12} {stats[g]}")
        for why, t in examples.get(g, [])[: args.show]:
            print(f"        [{why}]  {t}")
    print("\nREVIEW ONLY — never auto-applied (category words, PSAs, permissive gates):")
    for g in list(REVIEW_ONLY) + ["psa?"]:
        print(f"  {g:<12} {stats[g]}")
        for why, t in examples.get(g, [])[: args.show]:
            print(f"        [{why}]  {t}")
    print(f"\n  no determination  {stats['no determination']}")

    if args.out:
        Path(args.out).write_text(json.dumps(queue, indent=1))
        print(f"\nreview queue ({len(queue)}) -> {args.out}")

    if not args.apply_reviewed:
        print("\nNothing is auto-applied. Review the queue, delete the wrong rows,")
        print("then: --apply-reviewed <queue.json>")
        return

    reviewed = json.loads(Path(args.apply_reviewed).read_text())
    done = Counter()
    manifest = {}
    for row in reviewed:
        src = Path(row["path"])
        gate = row["gate"]
        if not src.exists() or gate not in (list(RESTRICTIVE) + ["kids", "christmas"]):
            done["skipped"] += 1
            continue
        dst = src.parent.parent / gate / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            done["already there"] += 1
            continue
        shutil.move(str(src), str(dst))
        manifest[str(dst)] = str(src)
        old = src.with_suffix(".nfo")
        if old.exists():
            old.unlink()
            done["stale nfo removed"] += 1
        done[f"moved -> {gate}"] += 1
    if manifest:
        (FILLER / "commercials" / "_regated_from.json").write_text(
            json.dumps(manifest, indent=1))
    print("\napplied:")
    for k, v in done.most_common():
        print(f"  {k:<22} {v}")


if __name__ == "__main__":
    main()
