#!/usr/bin/env python3
"""
Title & Content-Key Validation
==============================

Walks a channel's configuration tree and checks that everything it schedules
can actually resolve:

  1. Bare content keys (e.g. "toonami_bumpers") exist in MASTER_SOURCES.
  2. Show titles match something in the media library.

Why this exists: titles are free strings in dozens of places. A typo produces
an empty search rather than an error, so the block silently falls through to
filler or fallback -- the channel just gets thinner, with nothing in the log to
say why. This surfaces that before it airs.

The library manifest comes from the reference lists rather than a live scan,
so this runs offline and fast:

    reference/library-tv-all.txt
    reference/library-movies-all.txt

Usage:
    python3 -m scripts.testing.validate_titles                    # all channels
    python3 -m scripts.testing.validate_titles cartoon_network    # one channel
    python3 -m scripts.testing.validate_titles --quiet            # findings only
    python3 -m scripts.testing.validate_titles --all              # include scaffolding
"""

import argparse
import importlib
import os
import pkgutil
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

# The mock etv_client must be installed before any channel import.
from scripts.testing import install_mocks
install_mocks()

from scripts.library.sources import MASTER_SOURCES
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import (
    CommercialBreak, ContentItem, Fallback, Feather, Swap
)
from scripts.logic.structures import Block, Program

REFERENCE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "reference"
)
MANIFESTS = ("library-tv-all.txt", "library-movies-all.txt")

# Matches show_title:"Foo" / title:"Foo" inside a Lucene query string.
_SHOW_TITLE_IN_QUERY = re.compile(r'show_title:"([^"]+)"')
_BARE_TITLE_IN_QUERY = re.compile(r'(?<!show_)\btitle:"([^"]+)"')
# Any constraint beyond the title itself can disambiguate a broad title match.
_QUALIFIERS = re.compile(
    r'\b(?:studio|show_studio|tag|show_tag|genre|show_genre|season_number'
    r'|episode_number|release_date|content_rating|type|plot)\s*:'
)
_YEAR_SUFFIX = re.compile(r"\s*\(\d{4}\)\s*$")


# ---------------------------------------------------------------- normalising

def tokens(title: str) -> frozenset:
    """
    Reduce a title to a comparable token set.

    Handles the two conventions that otherwise defeat naive matching: the
    library's trailing-article form ("Flintstones, The (1960)") and the year
    suffix. Sets rather than sequences, so word order stops mattering.
    """
    t = _YEAR_SUFFIX.sub("", title).lower()
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    return frozenset(w for w in t.split() if w)


def load_manifest() -> Dict[frozenset, List[str]]:
    """Build {token_set: [library entries]} from the reference lists."""
    index: Dict[frozenset, List[str]] = {}
    missing = []
    for name in MANIFESTS:
        path = os.path.join(REFERENCE_DIR, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                entry = line.strip()
                if entry:
                    index.setdefault(tokens(entry), []).append(entry)
    if missing:
        print(f"⚠️  Missing manifest(s): {', '.join(missing)} -- "
              f"regenerate with `ls /path/to/media/tv > reference/{MANIFESTS[0]}`",
              file=sys.stderr)
    return index


# ------------------------------------------------------------------- matching

class TitleIndex:
    def __init__(self, index: Dict[frozenset, List[str]]):
        self.index = index
        self.all_keys = list(index.keys())

    def lookup(self, title: str) -> Tuple[str, List[str]]:
        """
        Returns (status, candidates) where status is one of:
          "exact"     -- token sets match outright
          "subset"    -- title's tokens are contained by exactly one entry
          "ambiguous" -- contained by several entries; caller should qualify
          "missing"   -- nothing contains it
        """
        want = tokens(title)
        if not want:
            return "missing", []
        if want in self.index:
            return "exact", self.index[want]

        contained = [k for k in self.all_keys if want < k]
        if len(contained) == 1:
            return "subset", self.index[contained[0]]
        if contained:
            hits = [e for k in contained for e in self.index[k]]
            return "ambiguous", sorted(hits)
        return "missing", []


# -------------------------------------------------------------------- walking

class ConfigWalker:
    """
    Collects every schedulable leaf from a channel config.

    Mirrors the traversal in scheduling/pre_registration.py, but gathers
    instead of registering, so it needs no API and no ErsatzTV.
    """

    def __init__(self):
        # (label, query_or_None) -- the query is kept so validation can tell a
        # deliberately broad title narrowed by studio/tag from a real typo.
        self.items: Set[Tuple[str, Optional[str]]] = set()
        self.keys: Set[str] = set()
        self._seen: Set[int] = set()

    def walk(self, obj: Any, depth: int = 0) -> None:
        if obj is None or depth > 20:
            return
        if id(obj) in self._seen:
            return
        self._seen.add(id(obj))

        if isinstance(obj, SeasonalBlock):
            self.walk(obj.base, depth + 1)
            self.walk(obj.seasonal, depth + 1)
            return

        if isinstance(obj, (Swap, Feather, CommercialBreak)):
            self.walk(getattr(obj, "content", None), depth + 1)
            return

        if isinstance(obj, Fallback):
            self.walk(obj.primary, depth + 1)
            self.walk(obj.secondary, depth + 1)
            return

        if isinstance(obj, Block):
            self.walk(obj.items, depth + 1)
            for attr in ("filler", "intro", "outro", "bumpers"):
                self.walk(getattr(obj, attr, None), depth + 1)
            return

        if isinstance(obj, Program):
            self.walk(obj.content, depth + 1)
            for attr in ("filler", "intro", "outro", "bumpers", "commercials"):
                self.walk(getattr(obj, attr, None), depth + 1)
            if obj.scheduling:
                for query in obj.scheduling.get("generated_queries", {}).values():
                    self._harvest_query(query)
            return

        if isinstance(obj, ContentItem):
            query = getattr(obj, "query", None)
            if query:
                self._harvest_query(query)
            elif getattr(obj, "title", None):
                self.items.add((obj.title, None))
            return

        # Collections expose .items; dicts do too, hence the guard.
        if hasattr(obj, "items") and not isinstance(obj, dict):
            self.walk(obj.items, depth + 1)
            return

        if isinstance(obj, dict):
            for value in obj.values():
                self.walk(value, depth + 1)
            return

        if isinstance(obj, (list, tuple, set)):
            for item in obj:
                self.walk(item, depth + 1)
            return

        if isinstance(obj, str):
            self.keys.add(obj)
            return

    def _harvest_query(self, query: str) -> None:
        query = query or ""
        for match in _SHOW_TITLE_IN_QUERY.findall(query):
            self.items.add((match.replace("*", "").strip(), query))
        for match in _BARE_TITLE_IN_QUERY.findall(query):
            self.items.add((match.replace("*", "").strip(), query))


# ------------------------------------------------------------------ reporting

# Illustrative/scaffolding modules whose content keys are deliberate
# placeholders, not real library content.
SKIP_BY_DEFAULT = {"example_channel", "test_channel"}


def collect_channels(only: Optional[str], include_all: bool = False) -> List[Tuple[str, Any]]:
    import scripts.channels as channels_pkg
    names = [
        m.name for m in pkgutil.iter_modules(channels_pkg.__path__)
        if not m.name.startswith("_")
    ]
    if not only and not include_all:
        names = [n for n in names if n not in SKIP_BY_DEFAULT]
    if only:
        if only not in names:
            print(f"No such channel '{only}'. Available: {', '.join(sorted(names))}")
            sys.exit(2)
        names = [only]

    loaded = []
    for name in sorted(names):
        try:
            loaded.append((name, importlib.import_module(f"scripts.channels.{name}")))
        except Exception as exc:  # a broken channel shouldn't stop the rest
            print(f"⚠️  {name}: import failed -- {exc}")
    return loaded


def validate(module: Any, index: TitleIndex) -> Dict[str, List[str]]:
    walker = ConfigWalker()
    for attr in dir(module):
        if not attr.startswith("_"):
            walker.walk(getattr(module, attr))

    findings: Dict[str, List[str]] = {
        "missing_titles": [], "ambiguous_titles": [], "unknown_keys": [],
        "unverifiable": [],
    }

    # A query may name several titles via OR; if any branch resolves, the item
    # will find content, so only flag when every branch fails.
    # Group only genuine query strings; bare titles carry no OR relationship
    # to each other and must each stand on their own.
    by_query: Dict[Any, List[str]] = {}
    for title, query in walker.items:
        group = query if query else ("__bare__", title)
        by_query.setdefault(group, []).append(title)

    for group, titles in by_query.items():
        query = group if isinstance(group, str) else None
        qualified = bool(query and _QUALIFIERS.search(query))
        results = {t: index.lookup(t) for t in sorted(titles)}

        if any(status in ("exact", "subset") for status, _ in results.values()):
            continue  # at least one branch resolves

        for title, (status, candidates) in results.items():
            if status == "ambiguous":
                if qualified:
                    continue  # studio/tag/genre narrows it -- intentional
                shown = ", ".join(candidates[:4])
                more = f" (+{len(candidates) - 4} more)" if len(candidates) > 4 else ""
                findings["ambiguous_titles"].append(f"{title}  ->  {shown}{more}")
            elif status == "missing":
                # A bare `title:` can name an episode or special, which the
                # show/movie manifest cannot see. Report separately.
                if query and _BARE_TITLE_IN_QUERY.search(query) \
                        and not _SHOW_TITLE_IN_QUERY.search(query):
                    findings["unverifiable"].append(
                        f"{title}  (episode/special -- not checkable offline)")
                else:
                    findings["missing_titles"].append(title)

    for key in sorted(walker.keys):
        # Bare keys only: anything with Lucene syntax is a literal query, and
        # dotted/spaced strings are prose (block names, EPG titles).
        if key in MASTER_SOURCES:
            continue
        if not re.fullmatch(r"[a-z0-9_]+", key):
            continue
        findings["unknown_keys"].append(key)

    findings["_counts"] = [str(len(walker.items)), str(len(walker.keys))]
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("channel", nargs="?", help="Channel module name (default: all)")
    parser.add_argument("--quiet", action="store_true", help="Only print findings")
    parser.add_argument("--all", action="store_true", dest="include_all",
                        help="Include example/test scaffolding channels")
    args = parser.parse_args()

    index = TitleIndex(load_manifest())
    if not index.all_keys:
        print("❌ Library manifest is empty -- nothing to validate against.")
        return 2

    total = 0
    for name, module in collect_channels(args.channel, args.include_all):
        findings = validate(module, index)
        n_titles, n_keys = findings.pop("_counts")
        notes = findings.pop("unverifiable")
        problems = sum(len(v) for v in findings.values())
        total += problems

        if problems == 0:
            if not args.quiet:
                suffix = f"  ({len(notes)} unverifiable)" if notes else ""
                print(f"✅ {name}: {n_titles} titles, {n_keys} keys -- all resolve{suffix}")
            continue

        print(f"\n❌ {name}: {problems} problem(s) "
              f"across {n_titles} titles and {n_keys} keys")
        labels = {
            "missing_titles": "Titles not found in the library",
            "ambiguous_titles": "Titles matching several shows -- qualify these",
            "unknown_keys": "Content keys absent from MASTER_SOURCES",
        }
        for kind, entries in findings.items():
            if entries:
                print(f"\n   {labels[kind]} ({len(entries)}):")
                for entry in entries:
                    print(f"      • {entry}")
        if notes:
            print(f"\n   Not checkable offline ({len(notes)}):")
            for entry in notes:
                print(f"      • {entry}")

    print(f"\n{'✅ No problems found.' if total == 0 else f'Found {total} problem(s).'}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
