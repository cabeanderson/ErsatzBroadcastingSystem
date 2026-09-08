#!/usr/bin/env python3
"""
doc_audit.py -- check the Markdown docs against the code they describe.

    python3 -m scripts.testing.doc_audit

Exits non-zero when a doc references something that does not exist, so it can
gate a pipeline like the other checkers.

## Why this exists

`IMPORTS.md` documented the pre-reorganisation module layout for months --
`scripts.schedule`, `scripts.logic.holidays`, `scripts.library.collections` --
and 31 of its import lines could not have run. `ARCHITECTURE.md` named six
modules that had been deleted or folded away. None of it was caught, because
prose has no test: a wrong docstring compiles exactly as well as a right one.

Three checks, cheapest first:

1. Every `` `path/file.py` `` names a file that exists.
2. Every `` `function()` `` names a `def` or `class` somewhere in the tree.
3. Every `from scripts... import a, b` line is executed -- the module is
   imported and each symbol looked up. This is the one that found the
   inverted "Re-Exports" section, where the docs claimed a package re-exported
   a name it does not.

Check 3 is the valuable one and the reason this is a script rather than a
grep: only an import can tell you whether `scripts.logic` really exposes
`DayDirector`. It does not.

## Deliberate exceptions

`ALLOWED_STALE` holds references that are *supposed* to name something gone --
the note in ARCHITECTURE.md explaining that `schedule.py` became
`scheduling/runner.py` is documentation of a rename, not a stale reference.
Private names (`_leading_underscore`) are skipped in the import check because
the anti-pattern examples name them on purpose.
"""

import importlib
import pathlib
import re
import sys

import scripts.testing  # noqa: F401 -- installs the etv_client mock

DOCS = ["ARCHITECTURE.md", "CONCEPTS.md", "IMPORTS.md", "README.md", "ERSATZTV_API.md"]

# (doc, reference) pairs that name something gone, on purpose.
ALLOWED_STALE = {
    ("ARCHITECTURE.md", "schedule.py"),      # the note explaining the rename
    ("IMPORTS.md", "schedule.py"),
}


def _root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent


def audit() -> list[str]:
    root = _root()
    files = {p.name for p in root.rglob("*.py")}
    source = "\n".join(
        p.read_text(encoding="utf-8", errors="replace") for p in root.rglob("*.py")
    )
    defined = set(re.findall(r"^\s*(?:def|class)\s+(\w+)", source, re.M))

    problems: list[str] = []
    for doc in DOCS:
        path = root / doc
        if not path.exists():
            problems.append(f"{doc}: missing")
            continue
        text = path.read_text(encoding="utf-8")

        for ref in sorted(set(re.findall(r"`([\w/]+\.py)`", text))):
            if (doc, ref.split("/")[-1]) in ALLOWED_STALE:
                continue
            if ref.split("/")[-1] not in files:
                problems.append(f"{doc}: references missing file `{ref}`")

        for ref in sorted(set(re.findall(r"`([a-z_][a-z0-9_]{4,})\(\)`", text))):
            if ref not in defined:
                problems.append(f"{doc}: references undefined `{ref}()`")

        for line in text.splitlines():
            m = re.match(r"\s*from (scripts[\w.]*) import ([\w, ]+)", line)
            if not m:
                continue
            module_name, symbols = m.group(1), m.group(2)
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                problems.append(f"{doc}: cannot import {module_name} ({type(exc).__name__})")
                continue
            for symbol in (s.strip() for s in symbols.split(",")):
                # Private names appear in the "don't do this" examples.
                if not symbol or symbol.startswith("_"):
                    continue
                if not hasattr(module, symbol):
                    problems.append(f"{doc}: {module_name} has no {symbol!r}")
    return problems


def main() -> int:
    problems = audit()
    if not problems:
        print(f"✅ docs match the code ({len(DOCS)} files checked)")
        return 0
    print(f"❌ {len(problems)} documentation problem(s):\n")
    for p in problems:
        print(f"  {p}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
