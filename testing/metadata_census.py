#!/usr/bin/env python3
"""
Metadata Facet Census
=====================

Answers "what can a content key actually select on?" by reading the library's
own `.nfo` files rather than the TSV manifests, which carry only title, year,
episodes, genres and studio.

**The library is richly tagged and nothing in `scripts/` could see it.** 2,046
of 2,066 films and 461 of 574 shows carry TMDB keyword `<tag>` elements --
**9,672 distinct film tags over 31,844 applications**. `key_census` *skips*
every `tag:` clause on the grounds that skipping widens rather than narrows,
which is right for sizing and blind for correctness: it cannot tell
`tag:christmas` (64 films) from `tag:valentines` (none at all).

That gap matters because 112 of the registry's 560 keys carry a `tag:` clause
and **about thirty of the tags they name do not exist in the library**. A
`tag:` ANDed into a query resolves to *nothing* when no document carries it --
the surviving clauses do not rescue it -- so those keys are empty, silently,
and the block falls through to `fallback_content` with nothing in the log.

So this is the tool to run before building any calendar, holiday or seasonal
block, because those are precisely the blocks written on tags.

What it reports:

  1. TAG COVERAGE   -- how much of the library is tagged, and the vocabulary.
  2. TAG-KEY HEALTH -- every registry key with a `tag:` clause, evaluated
                       against the real tags and sized, with the airtime each
                       carries. EMPTY is a live defect; THIN is a warning.
  3. FACETS         -- genre, studio, country, certification, collection.
  4. CALENDAR       -- the tags and keyword sweeps worth building holiday and
                       seasonal keys from, with what each would actually select.

Writes `reference/metadata-facets.md`.

**One caveat.** This reads what is on disk. Tags can also be applied inside
ErsatzTV -- the `filler/` trees are tagged `bumps`/`shows` and no `.nfo` says
so -- so a key reported EMPTY here may work on the server if its tags were
added there. That applies to the filler and bumper keys and to nothing else.

Usage:
    python3 -m scripts.testing.metadata_census
    python3 -m scripts.testing.metadata_census --tags-only
    python3 -m scripts.testing.metadata_census --tag christmas
    python3 -m scripts.testing.metadata_census --media /path/to/media
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from scripts import config

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

MEDIA_ROOT = str(config.MEDIA_ROOT)
REFERENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference")
OUT = os.path.join(REFERENCE_DIR, "metadata-facets.md")

# The holidays the lineup actually programs, and the words that find them when
# there is no `tag:` to ask. Plot text is included because a Christmas film is
# very often not titled one -- Die Hard is the canonical case.
CALENDAR_KEYWORDS = {
    "christmas":   ["christmas", "santa", "xmas", "yuletide", "north pole", "st. nick", "nativity"],
    "halloween":   ["halloween", "trick or treat", "jack-o", "haunted house"],
    "thanksgiving":["thanksgiving", "pilgrim"],
    "new_years":   ["new year's eve", "new years eve", "new year's day", "times square"],
    "valentines":  ["valentine"],
    "st_patricks": ["st. patrick", "saint patrick", "leprechaun", "irish luck"],
    "july_4":      ["independence day", "fourth of july", "4th of july"],
    "easter":      ["easter", "passover"],
}

FIELDS = ("genre", "studio", "country", "tag", "director", "credits")


# ==============================================================================
# READING
# ==============================================================================

def _text(el):
    return (el.text or "").strip() if el is not None else ""


def parse_nfo(path):
    """One record from an .nfo, or None if it will not parse.

    Malformed NFOs are common in a scraped library and one bad file must not
    abort a census over several thousand.
    """
    try:
        root = ET.parse(path).getroot()
    except Exception:
        return None

    rec = {f: [_text(e) for e in root.findall(f) if _text(e)] for f in FIELDS}
    rec["title"] = _text(root.find("title"))
    rec["year"] = _text(root.find("year")) or _text(root.find("premiered"))[:4]
    rec["plot"] = (_text(root.find("plot")) or _text(root.find("outline")))
    rec["certification"] = _text(root.find("mpaa")) or _text(root.find("certification"))
    setname = root.find("set/name")
    rec["set"] = _text(setname)
    rec["path"] = path
    return rec


def scan(media_root):
    """(movies, shows). Movie NFOs sit beside the film; TV uses tvshow.nfo."""
    movies, shows = [], []

    mroot = os.path.join(media_root, "movies")
    if os.path.isdir(mroot):
        for entry in sorted(os.scandir(mroot), key=lambda e: e.name):
            if not entry.is_dir():
                continue
            for f in sorted(os.listdir(entry.path)):
                # Skip the trailers/ and extras/ subtrees -- their NFOs describe
                # a featurette, not the film, and would double-count every facet.
                if f.endswith(".nfo") and not f.startswith("."):
                    rec = parse_nfo(os.path.join(entry.path, f))
                    if rec and rec["title"]:
                        rec["folder"] = entry.name
                        movies.append(rec)
                    break

    troot = os.path.join(media_root, "tv")
    if os.path.isdir(troot):
        for entry in sorted(os.scandir(troot), key=lambda e: e.name):
            if not entry.is_dir():
                continue
            p = os.path.join(entry.path, "tvshow.nfo")
            if os.path.exists(p):
                rec = parse_nfo(p)
                if rec and rec["title"]:
                    rec["folder"] = entry.name
                    shows.append(rec)
    return movies, shows


# ==============================================================================
# TAG-KEY HEALTH
# ==============================================================================

TAG_CLAUSE = re.compile(r'tag:"[^"]+"|tag:[\w:*-]+')


def as_query_records(movies, shows):
    """NFO records in the shape `key_census.evaluate` expects, plus `tags`.

    That function grew a `has_tags` parameter for this: given records that
    carry a tag set it evaluates `tag:` clauses instead of skipping them, which
    is the whole point of reading NFOs rather than the TSV.
    """
    def one(r, is_movie):
        try:
            year = int(r["year"])
        except (TypeError, ValueError):
            year = 0
        return {
            "title": r["title"],
            "year": year,
            "genres": {g.lower() for g in r["genre"]},
            "studio": "; ".join(r["studio"]),
            "tags": {t.lower() for t in r["tag"]},
            "minutes": 0,
            "episodes": 0,
        }
    return [one(r, True) for r in movies], [one(r, False) for r in shows]


def tag_key_report(films=None, tvshows=None):
    """Every registry key with a `tag:` clause, evaluated for real.

    Sizes the *whole* query against tag-bearing records, so an EMPTY verdict
    here means the key genuinely selects nothing -- not that a clause could not
    be checked, which is all `key_census` is able to say.
    """
    from scripts.testing import install_mocks
    install_mocks()
    from scripts.library.sources import MASTER_SOURCES
    from scripts.testing import key_census as KC

    rows = []
    for key, val in MASTER_SOURCES.items():
        q = val if isinstance(val, str) else getattr(val, "query", None)
        if not (isinstance(q, str) and "tag:" in q):
            continue
        tags = [t.split(":", 1)[1].strip('"').lower() for t in TAG_CLAUSE.findall(q)]
        n = None
        if films is not None:
            kind = KC.query_kind(q)
            recs = films if kind == "movie" else (tvshows if kind == "tv" else None)
            if recs is not None:
                n = len(KC.evaluate(q, recs, has_tags=True)[0])
        rows.append({"key": key, "query": q, "tags": tags, "size": n,
                     "verdict": ("?" if n is None else
                                 "EMPTY" if n == 0 else
                                 "THIN" if n < 10 else "OK")})
    order = {"EMPTY": 0, "THIN": 1, "OK": 2, "?": 3}
    rows.sort(key=lambda r: (order[r["verdict"]], -(r["size"] or 0), r["key"]))
    return rows


def airtime_by_key(_unused=None):
    """Hours-per-day each key carries, sampled a week per month across a year.

    The window has to span the calendar. A fortnight in January reports every
    `christmas_*` and `halloween_*` key as unscheduled, which is exactly
    backwards for a tool whose main finding is about holiday keys. One week
    per month enters every month, every weekday and every seasonal ramp.
    """
    import logging
    from datetime import date, timedelta
    from scripts.testing import collision_report as CR
    from scripts.testing.simulator import ChannelSimulator

    days = [date(2026, m, 7) + timedelta(days=i) for m in range(1, 13) for i in range(7)]
    out = defaultdict(float)
    logging.disable(logging.CRITICAL)
    try:
        for _, mod in CR.discover_channels().items():
            sim = ChannelSimulator(mod)
            for d in days:
                for e in sim.simulate_day(d, hours=24):
                    if e.get("type") != "content" or not isinstance(e.get("content"), str):
                        continue
                    out[CR.base_key(e["content"])] += (e.get("duration") or 0) / 60.0
    finally:
        logging.disable(logging.NOTSET)
    return {k: v / len(days) for k, v in out.items()}


# ==============================================================================
# FACETS
# ==============================================================================

def facet_counts(records, field):
    c = Counter()
    for r in records:
        for v in r.get(field) or []:
            if v:
                c[v] = c[v] + 1
    return c


def calendar_candidates(records, kind):
    """Items a keyword sweep of title and plot finds for each programmed holiday.

    This is what has to stand in for `tag:christmas` until something writes tags.
    Plot is searched as well as title because the useful ones are rarely titled
    for the holiday.
    """
    out = {}
    for holiday, words in CALENDAR_KEYWORDS.items():
        hits = []
        for r in records:
            hay = (r["title"] + " " + r["plot"]).lower()
            if any(w in hay for w in words):
                hits.append((r["title"], r["year"]))
        out[holiday] = sorted(set(hits), key=lambda x: (x[1] or "", x[0]))
    return out


# ==============================================================================
# OUTPUT
# ==============================================================================

def write_doc(movies, shows, tagrows, airtime, mvocab, svocab):
    L = []
    A = L.append

    A("# Metadata Facets — what a query can actually select on\n")
    A("Generated by `python3 -m scripts.testing.metadata_census`. Reads the")
    A("library's `.nfo` files directly, so it sees fields the TSV manifests drop.\n")
    A("> Regenerate whenever the library changes. This file is the answer to")
    A("> \"what can I write a content key against?\" — [library-analysis.md]"
      "(library-analysis.md) answers \"is there enough of it\".\n")
    A("---\n")

    # ---- 1. tags
    A("## 1. Tag coverage\n")
    A("| | Movies | Shows |\n|---|---:|---:|")
    A(f"| Scanned | {len(movies)} | {len(shows)} |")
    mt = sum(1 for r in movies if r["tag"]); st = sum(1 for r in shows if r["tag"])
    A(f"| Carrying a `<tag>` | {mt} | {st} |")
    A(f"| Distinct tags | {len(mvocab)} | {len(svocab)} |")
    A(f"| Tag applications | {sum(mvocab.values())} | {sum(svocab.values())} |\n")
    A("These are TMDB keyword tags, scraped with the rest of the metadata. They")
    A("are the most selective field the library has and **no tool in `scripts/`")
    A("could read them until now** — `key_census` skips every `tag:` clause, so")
    A("it cannot tell `tag:christmas` (64 films) from `tag:valentines` (none).\n")

    A("<details><summary><b>The 80 most common film tags</b></summary>\n")
    A("| Tag | Films |\n|---|---:|")
    for t, n in mvocab.most_common(80):
        A(f"| {t} | {n} |")
    A("\n</details>\n")
    A("<details><summary><b>The 60 most common show tags</b></summary>\n")
    A("| Tag | Shows |\n|---|---:|")
    for t, n in svocab.most_common(60):
        A(f"| {t} | {n} |")
    A("\n</details>\n")

    # ---- 2. tag-key health
    empty = [r for r in tagrows if r["verdict"] == "EMPTY"]
    thin = [r for r in tagrows if r["verdict"] == "THIN"]
    ok = [r for r in tagrows if r["verdict"] == "OK"]
    A(f"## 2. The {len(tagrows)} registry keys that bet on a tag\n")
    A("Each evaluated in full against the real tags, so a size here is the size.\n")
    A(f"- **EMPTY ({len(empty)})** — selects nothing. A `tag:` ANDed into a query")
    A("  resolves to nothing when no document carries it; the surviving clauses do")
    A("  not rescue it. Every one of these is a block playing its fallback.")
    A(f"- **THIN ({len(thin)})** — under ten titles. Not broken, but not the pool the")
    A("  block was written for.")
    A(f"- **OK ({len(ok)})**.\n")

    def _rows(group, title, note):
        live = sorted(((airtime.get(r["key"], 0.0), r) for r in group), key=lambda t: -t[0])
        if not live:
            return
        on = [(h, r) for h, r in live if h > 0]
        A(f"### {title}\n")
        if note:
            A(note + "\n")
        if on:
            A(f"**On air — {sum(h for h, _ in on):.1f} h/day.**\n")
            A("| h/day | Key | Size | Tags | Missing tags |\n|---:|---|---:|---|---|")
            for h, r in on:
                miss = [t for t in r["tags"] if not (mvocab.get(t) or svocab.get(t))]
                A(f"| {h:.2f} | `{r['key']}` | {r['size']} | {', '.join(r['tags'])[:44]} "
                  f"| {', '.join(miss)[:40] or '—'} |")
            A("")
        off = [r for h, r in live if h == 0]
        if off:
            A(f"<details><summary>{len(off)} more, currently unscheduled</summary>\n")
            for r in off:
                miss = [t for t in r["tags"] if not (mvocab.get(t) or svocab.get(t))]
                A(f"- `{r['key']}` ({r['size']}) — tags: {', '.join(r['tags'])[:60]}"
                  + (f" · **missing:** {', '.join(miss)[:50]}" if miss else ""))
            A("\n</details>\n")

    _rows(empty, "EMPTY — these are live defects",
          "The tag named does not exist in the library, or nothing carries it "
          "alongside the query's other clauses.")
    _rows(thin, "THIN — the pool is smaller than the block assumes", "")

    missing = sorted({t for r in tagrows for t in r["tags"]
                      if not (mvocab.get(t) or svocab.get(t))})
    if missing:
        A(f"### The {len(missing)} tags the registry names and the library does not have\n")
        A("Any key ANDing one of these selects nothing. Either retag the library, "
          "or rewrite the key against a tag that exists, a genre, or a title list.\n")
        A("```\n" + "\n".join(missing) + "\n```\n")

    # ---- 3. facets
    A("## 3. What the library *can* be queried on\n")
    for label, field, recs, top in (
        ("Movie genres", "genre", movies, 40),
        ("Show genres", "genre", shows, 40),
        ("Movie studios", "studio", movies, 40),
        ("Show studios", "studio", shows, 40),
        ("Movie countries", "country", movies, 30),
    ):
        c = facet_counts(recs, field)
        A(f"<details><summary><b>{label}</b> — {len(c)} distinct</summary>\n")
        A("| Value | Items |\n|---|---:|")
        for v, n in c.most_common(top):
            A(f"| {v} | {n} |")
        A("\n</details>\n")

    certs = Counter(r["certification"] for r in movies if r["certification"])
    A(f"<details><summary><b>Movie certifications</b> — {len(certs)} distinct, "
      f"{sum(certs.values())} of {len(movies)} films carry one</summary>\n")
    A("| Rating | Films |\n|---|---:|")
    for v, n in certs.most_common():
        A(f"| {v} | {n} |")
    A("\n</details>\n")

    # ---- 4. collections: the marathon primitive
    sets = Counter(r["set"] for r in movies if r["set"])
    multi = {k: v for k, v in sets.items() if v > 1}
    A(f"## 4. Collections — {len(sets)} named sets, {len(multi)} with more than one film\n")
    A("`<set>` is the field a franchise marathon wants: it is already the exact")
    A("grouping a `MarathonSequence` needs, and it is more reliable than the")
    A("year-bounded `movie_by_title` phrase matches the horror and Bond marathons")
    A("are built from. **It is not currently used by any key.**\n")
    A("| Collection | Films |\n|---|---:|")
    for v, n in sorted(multi.items(), key=lambda kv: (-kv[1], kv[0]))[:60]:
        A(f"| {v} | {n} |")
    A("")

    # ---- 5. calendar
    A("## 5. Building calendar and holiday keys\n")
    A("What each programmed holiday can actually be selected by. The **tag** column")
    A("is what `tag:` would return today; the **keyword** column is a title-and-plot")
    A("sweep, which is what has to stand in where the tag is absent or thin. A")
    A("keyword list becomes a `title:` OR-group, which `validate_titles` can check")
    A("and a `tag:` clause never can.\n")
    mcand = calendar_candidates(movies, "movie")
    scand = calendar_candidates(shows, "show")
    TAGFOR = {"christmas": "christmas", "halloween": "halloween",
              "thanksgiving": "thanksgiving", "new_years": "new years",
              "valentines": "valentines", "st_patricks": "st patricks day",
              "july_4": "july 4th", "easter": "easter"}
    A("| Holiday | `tag:` films | `tag:` shows | keyword films | keyword shows | verdict |")
    A("|---|---:|---:|---:|---:|---|")
    for h in CALENDAR_KEYWORDS:
        t = TAGFOR[h]
        tm, ts = mvocab.get(t, 0), svocab.get(t, 0)
        km, ks = len(mcand[h]), len(scand[h])
        verdict = ("tag works" if tm >= 10 else
                   "**tag is empty — use keywords**" if tm == 0 else
                   "tag is thin — widen with keywords")
        A(f"| {h} | {tm} | {ts} | {km} | {ks} | {verdict} |")
    A("")
    for h in CALENDAR_KEYWORDS:
        if not mcand[h] and not scand[h]:
            continue
        A(f"<details><summary><b>{h}</b> — {len(mcand[h])} films, {len(scand[h])} shows by keyword</summary>\n")
        if mcand[h]:
            A("**Films:** " + ", ".join(f"{t} ({y})" for t, y in mcand[h]) + "\n")
        if scand[h]:
            A("**Shows:** " + ", ".join(f"{t} ({y})" for t, y in scand[h]) + "\n")
        A("</details>\n")

    A("## 6. Seasonal tags that actually exist\n")
    A("The four `classic_hollywood_<season>_movies` keys are built from mood tags.")
    A("These are the ones with something behind them — the rest of each key's list")
    A("is in section 2's missing-tag block.\n")
    SEASON = {
        "WINTER": ["snow", "ice", "blizzard", "cold", "winter", "mountain", "alaska",
                   "antarctica", "ski", "cabin", "fireplace", "storm", "isolation",
                   "survival", "holiday", "christmas"],
        "SPRING": ["garden", "nature", "hiking", "exploration", "travel", "roadtrip",
                   "romance", "dating", "wedding", "youth", "fair", "farm",
                   "countryside", "animals", "festival"],
        "SUMMER": ["summer", "beach", "ocean", "lake", "island", "vacation", "camp",
                   "camping", "concert", "sports", "surf", "pool", "heat", "desert",
                   "jungle", "teen", "party"],
        "FALL":   ["rain", "fog", "autumn", "harvest", "noir", "detective", "mystery",
                   "thriller", "psychological", "gothic", "halloween", "witch",
                   "ghost", "haunted", "school", "college", "campus"],
    }
    for name, tags in SEASON.items():
        live = [(t, mvocab.get(t, 0)) for t in tags if mvocab.get(t)]
        dead_ = [t for t in tags if not mvocab.get(t)]
        A(f"**{name}** — {sum(n for _, n in live)} tag applications across "
          f"{len(live)} live tags; {len(dead_)} of the key's tags are absent.  ")
        A("live: " + ", ".join(f"`{t}` ({n})" for t, n in sorted(live, key=lambda x: -x[1])))
        A("  \nabsent: " + (", ".join(f"`{t}`" for t in dead_) or "—") + "\n")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    return OUT


def vocab(records):
    c = Counter()
    for r in records:
        for t in r["tag"]:
            c[t.lower()] += 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", default=MEDIA_ROOT)
    ap.add_argument("--tags-only", action="store_true",
                    help="print the tag-key verdicts and exit; no doc")
    ap.add_argument("--tag", help="list everything carrying this tag, and exit")
    args = ap.parse_args()

    print(f"scanning {args.media} ...", file=sys.stderr)
    movies, shows = scan(args.media)
    if not movies and not shows:
        print(f"no .nfo files found under {args.media}", file=sys.stderr)
        return 2
    print(f"  {len(movies)} movies, {len(shows)} shows", file=sys.stderr)
    mvocab, svocab = vocab(movies), vocab(shows)

    if args.tag:
        want = args.tag.lower()
        for label, recs in (("FILM", movies), ("SHOW", shows)):
            for r in sorted(recs, key=lambda r: r["year"] or ""):
                if want in {t.lower() for t in r["tag"]}:
                    print(f"{label}  {r['year']:<6}{r['title']}")
        return 0

    films_q, shows_q = as_query_records(movies, shows)
    tagrows = tag_key_report(films_q, shows_q)

    if args.tags_only:
        for r in tagrows:
            miss = [t for t in r["tags"] if not (mvocab.get(t) or svocab.get(t))]
            print(f"{r['verdict']:<7}{str(r['size']):>5}  {r['key']:<38}"
                  + (f"MISSING: {', '.join(miss)}" if miss else ""))
        return 0

    print("simulating for airtime ...", file=sys.stderr)
    airtime = airtime_by_key()
    path = write_doc(movies, shows, tagrows, airtime, mvocab, svocab)

    empty = [r for r in tagrows if r["verdict"] == "EMPTY"]
    onair = [r for r in empty if airtime.get(r["key"], 0) > 0]
    hrs = sum(airtime.get(r["key"], 0) for r in onair)
    print(f"\nWrote {os.path.relpath(path)}")
    print(f"  {len(movies)} movies + {len(shows)} shows; "
          f"{len(mvocab)} film tags, {len(svocab)} show tags")
    print(f"  {len(tagrows)} keys use tag:  --  {len(empty)} EMPTY, "
          f"{len(onair)} of those on air ({hrs:.1f} h/day)")
    return 1 if onair else 0


if __name__ == "__main__":
    sys.exit(main())
