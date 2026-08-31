#!/usr/bin/env python3
"""
Registry Key Census
===================

Resolves every key in `MASTER_SOURCES` against the library manifests and
reports what each one actually selects.

Why this exists: **a key that returns nothing is indistinguishable from a
working one until a channel schedules it.** `validate_titles.py` checks that a
*title* resolves; nothing checked that a *key* was non-empty. Totally 80s spent
its whole life with six such keys -- Cosby, Family Ties, Growing Pains, Airwolf,
V and G.I. Joe are none of them on disk -- so three of its seven prime nights
were one show on loop and its two branded NBC nights were one show each. The
grid said otherwise and the logs said nothing.

Three findings, in severity order:

  EMPTY    a key some collection lists resolves to nothing. This is the defect
           above, and the only one that exits non-zero.
  THIN     a pool key (one built from genre/era rather than a title) resolves
           to fewer than --thin titles. Not a defect -- a warning that a block
           written as a rotation is really one show.
  BROAD    a title key matches more than one title, which is the phrase-match
           trap `library/horror.py` documents: `title:"Halloween"` also returns
           Halloween II, III, 4 and The Halloween Tree. Bound it by year.

Reads `reference/library-tv.tsv` and `reference/library-movies.tsv`, so it runs
offline with no ErsatzTV and no simulation.

**A pool reported here is a superset of the truth.** The manifests carry no
`tag:` or `content_rating:` column, so those clauses are skipped rather than
guessed at -- which can only widen a result. An empty key is therefore
genuinely empty; a large one may be smaller in reality. Keys that search
`other_video`, `music_video` or a playlist are not in the manifests at all and
are counted, not judged; for those trees see `bumper-inventory.md`.

**What this cannot see: the ErsatzTV index.** It resolves against the
manifests, which record what is *on disk*. `classic_western_tv` and
`classic_horror_tv` both returned nothing on the real server, and this reports
them as 5 shows / 952 episodes and 3 shows / 106 episodes -- the content
exists, so whatever emptied them lives in the index rather than the library.
Both are `type:show ... AND release_date:[...]`, and five of the six keys this
tool does catch are `type:episode` title lookups, which is a sharp enough
split to be worth one real build to settle. A PASS here means the library can
answer the key, not that ErsatzTV will.

Titles are matched on whole words with punctuation ignored, so
`show_title:"Star Wars The Clone Wars"` finds `Star Wars: The Clone Wars` the
way ErsatzTV's tokenizer does. That is looser than ErsatzTV in at least one
known case -- `Magnum P.I.` against the folder `Magnum, P.I.` matches here and
did not there -- so this cannot catch a punctuation typo. It errs toward
saying a key works.

Usage:
    python3 -m scripts.testing.key_census                  # findings
    python3 -m scripts.testing.key_census --all            # every key, with counts
    python3 -m scripts.testing.key_census eighties_        # keys whose name contains this
    python3 -m scripts.testing.key_census --thin 5         # widen the THIN bar
    python3 -m scripts.testing.key_census --quiet          # findings only, no summary
"""

import argparse
import csv
import os
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing import install_mocks

install_mocks()

from scripts.library.sources import MASTER_SOURCES
from scripts.testing.collision_report import (
    channel_collections, collection_membership, library_collections, query_for,
)

REFERENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference")
MOVIE_TSV = os.path.join(REFERENCE_DIR, "library-movies.tsv")
TV_TSV = os.path.join(REFERENCE_DIR, "library-tv.tsv")

# Clauses the manifests can answer. Everything else -- tag:, content_rating:,
# season_number:, plot: -- is skipped and reported, which widens the result set
# rather than narrowing it and keeps an EMPTY finding trustworthy.
CHECKABLE = (
    "type:", "genre:", "show_genre:", "release_date:", "year:", "minutes:",
    "title:", "show_title:", "studio:", "show_studio:",
)

# Only the TV manifest carries a studio column. On the film side `studio:` is
# unevaluable and has to be skipped -- scoring it as false reported Disney's
# `disney_movie` and `pixar_movie` as empty when both are simply unanswerable
# from `library-movies.tsv`.
STUDIO_FIELDS = ("studio:", "show_studio:")

MOVIE_TYPES = {"movie"}
TV_TYPES = {"show", "episode"}

DATE_RANGE = re.compile(r"release_date:\[(\S+) TO (\S+)\]")
MIN_RANGE = re.compile(r"minutes:\[(\S+) TO (\S+)\]")
YEAR_RANGE = re.compile(r"year:\[(\S+) TO (\S+)\]")
TYPE_CLAUSE = re.compile(r'type:"?([a-z_]+)"?')


# ==============================================================================
# MANIFESTS
# ==============================================================================

def _phrase(text):
    """Punctuation-insensitive form for phrase matching.

    ErsatzTV tokenizes before matching, so `show_title:"Star Wars The Clone
    Wars"` finds `Star Wars: The Clone Wars`. Comparing the raw strings does
    not, and reported four live Disney keys as empty.
    """
    return " " + re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip() + " "


def _genres(raw):
    return {g.strip().lower() for g in (raw or "").split(";") if g.strip()}


def _int(raw, default=0):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def load_films():
    """Films from the movie manifest, skipping rows with no parseable year."""
    films = []
    with open(MOVIE_TSV) as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            try:
                year = int(row["year"])
            except (TypeError, ValueError):
                continue
            films.append({
                "title": row["title"],
                "year": year,
                "genres": _genres(row["genres"]),
                "minutes": _int(row["runtime_min"]),
                "episodes": 0,
                "studio": "",
            })
    return films


def load_shows():
    """Shows from the TV manifest. `episodes` is what sizes a strip, not titles."""
    shows = []
    with open(TV_TSV) as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            shows.append({
                "title": row["title"],
                "year": _int(row["year"]),
                "genres": _genres(row["genres"]),
                "minutes": 0,
                "episodes": _int(row["episodes"]),
                "studio": (row.get("studio") or ""),
            })
    return shows


# ==============================================================================
# QUERY EVALUATION
# ==============================================================================

def _split_clauses(query):
    """Top-level AND clauses, respecting parentheses and quotes.

    Every query in the library is built by queries.py's `*_source` helpers,
    which join their parts with ' AND ' and parenthesise anything compound, so
    this recovers exactly the constraint set that built the key.
    """
    clauses, depth, buf, quoted = [], 0, "", False
    for ch in query:
        if ch == '"':
            quoted = not quoted
        if not quoted:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
        buf += ch
        if depth == 0 and not quoted and buf.upper().endswith(" AND "):
            clauses.append(buf[:-5].strip())
            buf = ""
    if buf.strip():
        clauses.append(buf.strip())
    return clauses


def _year_bound(token, default):
    return default if token == "*" else int(token[:4])


def _field_match(record, field, expr):
    """`genre:horror`, `genre:"science fiction"`, `genre:(mystery OR crime)`."""
    expr = expr.strip()
    if expr.startswith("(") and expr.endswith(")"):
        parts = [p.strip().strip('"').lower() for p in expr[1:-1].split(" OR ")]
        return any(_field_match(record, field, p) for p in parts)
    value = expr.strip('"').lower()
    if field == "genre":
        return value in record["genres"]
    if field == "studio":
        # Substring, not whole-word: the manifest holds "ITV1", "BBC One" and
        # "Disney+", and `studio:(bbc OR itv)` means to reach all of them.
        return value in record["studio"].lower()
    # Phrase match on whole words, the rule Lucene applies -- which is why
    # `title:"Halloween"` also reaches Halloween II and the BROAD finding
    # exists, while `show_title:"V"` reaches neither Voyager nor Veronica Mars.
    return _phrase(value) in _phrase(record["title"])


def query_kind(query):
    """'movie', 'tv', or None for playlists, bumpers and music video keys."""
    if not isinstance(query, str):
        return None
    types = set(TYPE_CLAUSE.findall(query))
    if types & MOVIE_TYPES:
        return "movie"
    if types & TV_TYPES:
        return "tv"
    return None


def _clause_test(body, kind):
    """A predicate for one clause, or None when the manifests cannot answer it.

    Handles the parenthesised OR groups `queries.py` builds -- `(title:*Mario*
    OR title:*Sonic*)`, `genre:(thriller OR mystery)` -- because a whole group
    scored as unevaluable silently widened those keys to the entire film
    library and made `videogame_movie` look like 1,858 films.
    """
    if body.startswith("(") and body.endswith(")"):
        parts = [p.strip() for p in re.split(r"\s+OR\s+", body[1:-1]) if p.strip()]
        tests = [_clause_test(p, kind) for p in parts]
        if not tests or any(t is None for t in tests):
            return None
        return lambda r, ts=tests: any(t(r) for t in ts)

    if not body.startswith(CHECKABLE):
        return None

    # Only the TV manifest carries a studio column.
    if body.startswith(STUDIO_FIELDS):
        if kind == "movie":
            return None
        expr = body.split(":", 1)[1]
        return lambda r, e=expr: _field_match(r, "studio", e)

    if body.startswith(("genre:", "show_genre:")):
        expr = body.split(":", 1)[1]
        return lambda r, e=expr: _field_match(r, "genre", e)

    if body.startswith(("release_date:", "year:")):
        m = DATE_RANGE.search(body) or YEAR_RANGE.search(body)
        if not m:
            return None
        lo = _year_bound(m.group(1), -9999)
        hi = _year_bound(m.group(2), 9999)
        return lambda r, lo=lo, hi=hi: lo <= r["year"] <= hi

    if body.startswith("minutes:"):
        m = MIN_RANGE.search(body)
        if not m:
            return None
        lo = 0 if m.group(1) == "*" else int(m.group(1))
        hi = 99999 if m.group(2) == "*" else int(m.group(2))
        return lambda r, lo=lo, hi=hi: lo <= r["minutes"] <= hi

    if body.startswith(("title:", "show_title:")):
        expr = body.split(":", 1)[1]
        return lambda r, e=expr: _field_match(r, "title", e)

    return None


def title_targets(query):
    """Titles a query names outright, as top-level clauses.

    A key built from a title is a single-show lookup and a key built from genre
    or era is a pool; they fail in opposite directions and are judged by
    different rules. Titles inside an OR group do not count -- those are
    pattern searches (`title:*Mario*`), not a named show.
    """
    targets = []
    for clause in _split_clauses(query or ""):
        # A negated title clause is an exclusion, not a name: `classic_horror_tv`
        # is "pre-2010 horror, but NOT The X-Files" and names nothing.
        if clause.upper().startswith("NOT "):
            continue
        body = clause
        if body.startswith(("title:", "show_title:")):
            value = body.split(":", 1)[1].strip().strip('"')
            if "*" not in value:
                targets.append(value)
    return targets


def evaluate(query, records):
    """Records a query selects, plus the clauses that could not be checked.

    Unevaluable clauses are dropped whole -- including negated ones, where
    guessing would be worse than widening: `NOT tag:sitcom` cannot be tested,
    and treating it as false would empty every pool that carries it.
    """
    if not query:
        return [], ["<no query>"]

    kind = query_kind(query)
    selected = list(records)
    unchecked = []

    for clause in _split_clauses(query):
        negate = clause.upper().startswith("NOT ")
        body = clause[4:].strip() if negate else clause

        if body.startswith("type:"):
            wanted = TYPE_CLAUSE.findall(body)
            allowed = MOVIE_TYPES if kind == "movie" else TV_TYPES
            # A second, contradictory type clause selects nothing at all.
            if wanted and not set(wanted) & allowed:
                return [], unchecked
            continue

        test = _clause_test(body, kind)
        if test is None:
            unchecked.append(clause)
            continue

        selected = [r for r in selected if test(r) != negate]

    return selected, unchecked


# ==============================================================================
# CENSUS
# ==============================================================================

def references():
    """Map key -> the named collections and channel schedules that list it.

    Both halves are needed. Most keys reach air through a library collection,
    but channels name keys directly too -- Mystery Theatre's LUNCH_SPECIAL is
    three bare keys written in the channel module.
    """
    named = dict(library_collections())
    named.update(channel_collections())
    return collection_membership(named)


def census(pattern=None):
    """Resolve every registry key. Returns a row per key, in registry order."""
    films, shows = load_films(), load_shows()
    used = references()

    rows = []
    for key in MASTER_SOURCES:
        if pattern and pattern not in key:
            continue
        query = query_for(key)
        kind = query_kind(query)
        if kind is None:
            rows.append({
                "key": key, "kind": None, "query": query, "count": None,
                "episodes": 0, "titles": [], "unchecked": [],
                "used_by": sorted(used.get(key, ())), "by_title": False, "targets": [],
            })
            continue

        selected, unchecked = evaluate(query, films if kind == "movie" else shows)
        targets = title_targets(query)
        titles = [r["title"] for r in selected]
        rows.append({
            "key": key,
            "kind": kind,
            "query": query,
            "count": len(selected),
            "episodes": sum(r["episodes"] for r in selected),
            "titles": titles,
            "unchecked": unchecked,
            "used_by": sorted(used.get(key, ())),
            "by_title": bool(targets),
            "targets": targets,
        })
    return rows


def findings(rows, thin):
    """Split resolvable rows into the three finding classes."""
    empty, thin_pools, broad = [], [], []
    for row in rows:
        if row["kind"] is None:
            continue
        if row["count"] == 0:
            empty.append(row)
        elif row["by_title"]:
            if row["count"] > 1:
                broad.append(row)
        elif row["count"] < thin:
            thin_pools.append(row)
    return empty, thin_pools, broad


# ==============================================================================
# REPORT
# ==============================================================================

def _where(row):
    return ", ".join(row["used_by"]) if row["used_by"] else "-- not referenced --"


def _size(row):
    if row["kind"] == "tv":
        return f"{row['count']:>3} show(s), {row['episodes']:>5} eps"
    return f"{row['count']:>3} film(s)"


def report(rows, thin, quiet, show_all):
    empty, thin_pools, broad = findings(rows, thin)
    referenced_empty = [r for r in empty if r["used_by"]]
    orphan_empty = [r for r in empty if not r["used_by"]]

    print("=" * 78)
    print("REGISTRY KEY CENSUS")
    print("=" * 78)

    if not quiet:
        resolvable = [r for r in rows if r["kind"] is not None]
        skipped = len(rows) - len(resolvable)
        print(f"  Keys examined : {len(rows)}")
        print(f"  Resolvable    : {len(resolvable)} "
              f"({sum(1 for r in resolvable if r['kind'] == 'movie')} film, "
              f"{sum(1 for r in resolvable if r['kind'] == 'tv')} television)")
        print(f"  Not in manifests: {skipped} (playlists, bumpers, music video)")
        print()

    print(f"EMPTY -- referenced by a collection and resolves to nothing ({len(referenced_empty)})")
    print("-" * 78)
    if referenced_empty:
        for row in referenced_empty:
            print(f"  {row['key']}")
            print(f"      {row['query']}")
            print(f"      listed by: {_where(row)}")
    else:
        print("  none")
    print()

    if orphan_empty and not quiet:
        print(f"EMPTY -- unreferenced, so harmless until something schedules it ({len(orphan_empty)})")
        print("-" * 78)
        for row in orphan_empty:
            print(f"  {row['key']:<34} {row['query']}")
        print()

    print(f"THIN -- pool keys resolving to fewer than {thin} titles ({len(thin_pools)})")
    print("-" * 78)
    if thin_pools:
        for row in sorted(thin_pools, key=lambda r: r["count"]):
            print(f"  {row['key']:<34} {_size(row)}   {', '.join(row['titles'])}")
            if row["used_by"]:
                print(f"      listed by: {_where(row)}")
    else:
        print("  none")
    print()

    print(f"BROAD -- title keys matching more than one title ({len(broad)})")
    print("-" * 78)
    if broad:
        for row in sorted(broad, key=lambda r: -r["count"]):
            print(f"  {row['key']:<34} {_size(row)}   {', '.join(row['titles'][:8])}")
    else:
        print("  none")
    print()

    if show_all:
        print("ALL RESOLVABLE KEYS")
        print("-" * 78)
        for row in rows:
            if row["kind"] is None:
                continue
            note = " [partial: " + "; ".join(row["unchecked"]) + "]" if row["unchecked"] else ""
            print(f"  {row['key']:<34} {_size(row)}{note}")
        print()

    if referenced_empty:
        print(f"FAIL: {len(referenced_empty)} referenced key(s) resolve to nothing.")
    else:
        print("PASS: every referenced key resolves to at least one title.")
    return 1 if referenced_empty else 0


def main():
    ap = argparse.ArgumentParser(description="Resolve every registry key against the library manifests.")
    ap.add_argument("pattern", nargs="?", help="only keys whose name contains this")
    ap.add_argument("--thin", type=int, default=3, help="THIN bar for pool keys (default 3)")
    ap.add_argument("--all", action="store_true", help="list every resolvable key with its size")
    ap.add_argument("--quiet", action="store_true", help="findings only")
    args = ap.parse_args()

    rows = census(args.pattern)
    if not rows:
        print(f"No keys match {args.pattern!r}.")
        return 1
    return report(rows, args.thin, args.quiet, args.all)


if __name__ == "__main__":
    sys.exit(main())
