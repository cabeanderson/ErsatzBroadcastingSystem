#!/usr/bin/env python3
"""
normalize_tag_case.py — collapse tags that exist in more than one casing.

Dry-run by default. Nothing is written unless --apply is passed.

The library holds two overlapping tag vocabularies: a curated Title Case layer
(Paranoia, Nonlinear Timeline, Black and White) and the raw lowercase TMDB
keyword dump (bunker, shrew, persidangan). 59% of films carry both at once.
They collide on ~183 terms, where the same concept is spelled two ways.

Canonical casing is the most frequent spelling of that term across the whole
library, which preserves the curated layer's Title Case rather than flattening
everything to lowercase. Ties break toward the capitalised form.

Writes are a single surgical text substitution per tag, never an XML
re-serialisation: the library holds three different XML declarations and two
spellings of an empty tag, all of which a full lxml round-trip would rewrite.
"""

from __future__ import annotations

import argparse
import collections
import re
import shutil
import sys
from pathlib import Path
from xml.sax.saxutils import escape, unescape

from lxml import etree

ROOT = Path("/media/movies")


def movie_dirs():
    for d in sorted(ROOT.iterdir()):
        if d.is_dir() and not d.name.startswith("."):
            yield d


def nfo_files():
    for d in movie_dirs():
        for n in sorted(d.glob("*.nfo")):
            yield n


def read_tags(nfo: Path):
    """Return the tag strings of an NFO, or None if it will not parse."""
    try:
        root = etree.parse(str(nfo)).getroot()
    except etree.XMLSyntaxError:
        return None
    return [t.text.strip() for t in root.findall("tag") if t.text and t.text.strip()]


def build_canonical():
    """Map lowercased term -> the casing that should win."""
    counts = collections.defaultdict(collections.Counter)
    for nfo in nfo_files():
        tags = read_tags(nfo)
        if tags is None:
            continue
        for t in tags:
            counts[t.lower()][t] += 1

    canon, collisions = {}, {}
    for key, spellings in counts.items():
        if len(spellings) < 2:
            continue
        # most frequent wins; ties break toward the capitalised spelling
        best = max(spellings.items(), key=lambda kv: (kv[1], kv[0][:1].isupper()))[0]
        canon[key] = best
        collisions[key] = spellings
    return canon, collisions


def plan_file(nfo: Path, canon: dict):
    """Return (substitutions, dropped_duplicates) for one NFO."""
    tags = read_tags(nfo)
    if tags is None:
        return None, None

    subs, seen, dropped = [], set(), []
    for t in tags:
        target = canon.get(t.lower())
        if target is None:
            seen.add(t.lower())
            continue
        if t.lower() in seen:
            dropped.append(t)          # same concept already present in this film
            continue
        seen.add(t.lower())
        if t != target:
            subs.append((t, target))
    return subs, dropped


def apply_file(nfo: Path, subs, dropped) -> bool:
    raw = nfo.read_text(encoding="utf-8")
    out = raw

    for old, new in subs:
        pat = re.compile(r"<tag>\s*" + re.escape(escape(old)) + r"\s*</tag>")
        if len(pat.findall(out)) != 1:
            print(f"    !! ambiguous <tag>{old}</tag> in {nfo.name}, file skipped")
            return False
        out = pat.sub(f"<tag>{escape(new)}</tag>", out, count=1)

    for dup in dropped:
        pat = re.compile(r"[ \t]*<tag>\s*" + re.escape(escape(dup)) + r"\s*</tag>\n")
        if len(pat.findall(out)) != 1:
            print(f"    !! ambiguous duplicate <tag>{dup}</tag> in {nfo.name}, file skipped")
            return False
        out = pat.sub("", out, count=1)

    if out == raw:
        return False

    # never write something that will not parse
    try:
        etree.fromstring(out.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        print(f"    !! would produce invalid XML in {nfo.name}: {e}")
        return False

    shutil.copy2(nfo, nfo.with_suffix(".nfo.bak"))
    nfo.write_text(out, encoding="utf-8")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually write changes")
    ap.add_argument("--limit", type=int, help="only touch the first N files (for a test run)")
    ap.add_argument("--show", type=int, default=25, help="how many collisions to list")
    args = ap.parse_args()

    if not ROOT.is_dir():
        sys.exit(f"library not found: {ROOT}")

    print("APPLY — writing changes" if args.apply else "DRY RUN — nothing will be written")
    print(f"library: {ROOT}\n")

    canon, collisions = build_canonical()
    print(f"terms spelled more than one way: {len(collisions)}")

    ranked = sorted(collisions.items(), key=lambda kv: -sum(kv[1].values()))
    print(f"\n=== canonical choices (top {args.show}) ===")
    for key, spellings in ranked[:args.show]:
        loser = ", ".join(f"{s}({c})" for s, c in spellings.items() if s != canon[key])
        print(f"   {canon[key]:<28} <- {loser}")

    files_changed = subs_total = drops_total = 0
    changed_files = []
    for i, nfo in enumerate(nfo_files()):
        if args.limit and i >= args.limit:
            break
        subs, dropped = plan_file(nfo, canon)
        if subs is None:
            print(f"   !! unparseable, skipped: {nfo.relative_to(ROOT)}")
            continue
        if not subs and not dropped:
            continue
        files_changed += 1
        subs_total += len(subs)
        drops_total += len(dropped)
        changed_files.append((nfo, subs, dropped))
        if args.apply:
            apply_file(nfo, subs, dropped)

    print(f"\n=== plan ===")
    print(f"   files affected:            {files_changed}")
    print(f"   tags recased:              {subs_total}")
    print(f"   intra-film duplicates cut: {drops_total}")

    print(f"\n=== sample of affected files ===")
    for nfo, subs, dropped in changed_files[:8]:
        print(f"   {nfo.parent.name}")
        for old, new in subs[:4]:
            print(f"       {old!r} -> {new!r}")
        for dup in dropped[:4]:
            print(f"       drop duplicate {dup!r}")

    if not args.apply:
        print("\nre-run with --apply to write. edited files get a .nfo.bak backup.")
        print("suggested first step:  --apply --limit 20")


if __name__ == "__main__":
    main()
