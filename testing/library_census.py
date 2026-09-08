#!/usr/bin/env python3
"""
Library Census

Reads the *actual media on disk* -- not the content registry -- and writes a
list of everything plus a genre analysis sized for channel decisions.

Sources, in the order they are trusted:

  movies/LIBRARY-INVENTORY.csv   2,063 rows, already probed and TMM-tagged.
                                 Authoritative; not re-derived here.
  tv/<Show (Year)>/tvshow.nfo    Scanned directly. The TV library has no
                                 inventory CSV, and its LIBRARY-REPORT.md is a
                                 technical audit with no genre data at all.

Episode counts are video files on disk, which is the number that matters for
scheduling -- an `.nfo` claiming 24 episodes does not fill a slot.

Usage:
    python3 -m scripts.testing.library_census
    python3 -m scripts.testing.library_census --media-root /path/to/media
"""

import argparse
import collections
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from scripts import config

MEDIA_ROOT = str(config.MEDIA_ROOT)

# Extensions the scanners count as an episode. Keep this at least as wide as
# ErsatzTV's own list: a scanner that knows fewer extensions than the server
# reports absence as certainty, and the manifest it writes is then quoted back
# as evidence about the server (V4).
#
# `.divx` and `.webm` were added 2026-09-08 after Makers Corner was budgeted
# against a New Yankee Workshop that looked like 151 episodes and is 281.
# ErsatzTV indexes both perfectly well -- they are ordinary AVI and WebM
# containers -- and the only thing that could not see them was this set. The
# cost was not one channel: **Magnum, P.I.'s entire season 7 is `.divx`**, so
# the show read 138 episodes against 158 on disk in every pool key that
# reaches it.
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".m4v", ".ts", ".mpg", ".mpeg",
                    ".wmv", ".mov", ".divx", ".webm"}

FOLDER_YEAR = re.compile(r"\((\d{4})\)\s*$")

# Genre combinations that map onto real scheduling decisions. Each is a name,
# the genres a title must have, and the genres that disqualify it. The exclusions
# are the whole point: 333 films are tagged Fantasy, but a third of those are
# sci-fi and another quarter are animation, and a fantasy channel built on the
# raw tag would be showing Star Wars and Shrek.
POOLS = [
    ("Sci-fi",              {"Science Fiction"}, set()),
    ("Sci-fi, live action",  {"Science Fiction"}, {"Animation"}),
    ("Fantasy",             {"Fantasy"}, set()),
    ("Fantasy, not sci-fi",  {"Fantasy"}, {"Science Fiction"}),
    ("Fantasy, live action", {"Fantasy"}, {"Science Fiction", "Animation"}),
    ("Horror",              {"Horror"}, set()),
    ("Horror, not comedy",   {"Horror"}, {"Comedy"}),
    ("Western",             {"Western"}, set()),
    ("Crime",               {"Crime"}, set()),
    ("Mystery",             {"Mystery"}, set()),
    ("Thriller",            {"Thriller"}, set()),
    ("War",                 {"War"}, set()),
    ("Musical",             {"Musical"}, set()),
    ("Animation",           {"Animation"}, set()),
    ("Family",              {"Family"}, set()),
    ("Documentary",         {"Documentary"}, set()),
]


def decade(year):
    return f"{(year // 10) * 10}s" if year else "unknown"


# ==============================================================================
# READING
# ==============================================================================

def read_movies(media_root):
    path = os.path.join(media_root, "movies", "LIBRARY-INVENTORY.csv")
    if not os.path.exists(path):
        raise SystemExit(f"Missing {path} -- regenerate the movie inventory first.")

    movies = []
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            year = row.get("year") or ""
            movies.append({
                "title": FOLDER_YEAR.sub("", row["folder"]).strip(),
                "year": int(year) if year.isdigit() else None,
                "genres": {g.strip() for g in row.get("genres", "").split(";") if g.strip()},
                "runtime": row.get("runtime_min") or "",
                "tier": row.get("tier") or "",
            })
    return movies


# Every tree under the media root that ErsatzTV indexes as a *show* library.
# `tv/` was the only one for as long as it was the only one, and that stopped
# being true when `youtube/shows/` was added: 637 episodes across six series
# were on disk, in ErsatzTV, and invisible to every offline tool here, so
# `key_census` reported live keys as EMPTY and `same_show_check` could not see
# a collision involving them. A scanner that knows about fewer libraries than
# the server does reports absence as certainty. Added 2026-09-07.
SHOW_ROOTS = ("tv", os.path.join("youtube", "shows"))


def show_folders(media_root):
    """(root, folder) for every show directory across all show libraries."""
    first = os.path.join(media_root, SHOW_ROOTS[0])
    if not os.path.isdir(first):
        raise SystemExit(f"Missing {first}")
    for name in SHOW_ROOTS:
        root = os.path.join(media_root, name)
        if not os.path.isdir(root):
            continue
        for folder in sorted(os.listdir(root)):
            yield root, folder


def read_shows(media_root):
    shows = []
    for root, folder in show_folders(media_root):
        path = os.path.join(root, folder)
        if not os.path.isdir(path):
            continue
        # TinyMediaManager parks deletions in `.deletedByTMM`. It is a real
        # directory with real subfolders, and counting it put the show total at
        # 576 against the library report's 574.
        if folder.startswith("."):
            continue

        title, year = folder, None
        match = FOLDER_YEAR.search(folder)
        if match:
            title = folder[:match.start()].strip()
            year = int(match.group(1))

        genres, studio = set(), ""
        nfo = os.path.join(path, "tvshow.nfo")
        if os.path.exists(nfo):
            try:
                node = ET.parse(nfo).getroot()
                title = node.findtext("title") or title
                studio = node.findtext("studio") or ""
                genres = {g.text.strip() for g in node.findall("genre")
                          if g.text and g.text.strip()}
                stamp = node.findtext("year") or (node.findtext("premiered") or "")[:4]
                if stamp and stamp.isdigit():
                    year = int(stamp)
            except ET.ParseError:
                # A malformed sidecar loses metadata, not the show. The folder
                # name still carries a usable title and year.
                pass

        episodes = 0
        for _, _, files in os.walk(path):
            episodes += sum(1 for f in files
                            if os.path.splitext(f)[1].lower() in VIDEO_EXTENSIONS)

        shows.append({"title": title, "year": year, "genres": genres,
                      "studio": studio, "episodes": episodes, "folder": folder})
    return shows


# ==============================================================================
# WRITING
# ==============================================================================

def write_tsv(path, rows, columns):
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([label for label, _ in columns])
        for row in rows:
            writer.writerow([get(row) for _, get in columns])


def select(items, include, exclude):
    return [i for i in items if include <= i["genres"] and not (exclude & i["genres"])]


def render(movies, shows, media_root):
    out = []
    w = out.append

    episodes = sum(s["episodes"] for s in shows)

    w("# Media Library Analysis")
    w("")
    w(f"Generated {datetime.now():%Y-%m-%d} by "
      "`python3 -m scripts.testing.library_census` from "
      f"`{media_root}`. Do not edit by hand.")
    w("")
    w("This describes **media that exists on disk**. It is not the content "
      "registry -- for that see [MEDIA_INVENTORY.md](../MEDIA_INVENTORY.md), "
      "which lists the keys the scheduler can address. A pool can be large here "
      "and unreachable there.")
    w("")
    w(f"- **{len(movies):,} films** — [library-movies.tsv](library-movies.tsv)")
    w(f"- **{len(shows):,} shows / {episodes:,} episode files** — [library-tv.tsv](library-tv.tsv)")
    w("")
    w("Genres come from TMM `.nfo` sidecars and are multi-valued, so the "
      "columns below sum to more than the library.")
    w("")

    w("## Pools that matter for channels")
    w("")
    w("| Pool | Films | Shows | Episodes |")
    w("|---|---:|---:|---:|")
    for name, include, exclude in POOLS:
        films = select(movies, include, exclude)
        series = select(shows, include, exclude)
        eps = sum(s["episodes"] for s in series)
        indent = "&nbsp;&nbsp;↳ " if "," in name else ""
        w(f"| {indent}{name} | {len(films):,} | {len(series):,} | {eps:,} |")
    w("")

    w("## Every genre tag in use")
    w("")
    film_genres = collections.Counter(g for m in movies for g in m["genres"])
    show_genres = collections.Counter(g for s in shows for g in s["genres"])
    w("| Genre | Films | Shows |")
    w("|---|---:|---:|")
    for genre in sorted(set(film_genres) | set(show_genres),
                        key=lambda g: -(film_genres[g] + show_genres[g])):
        w(f"| {genre} | {film_genres.get(genre, 0):,} | {show_genres.get(genre, 0):,} |")
    w("")

    w("## Films by decade")
    w("")
    by_decade = collections.Counter(decade(m["year"]) for m in movies)
    w("| Decade | Films |")
    w("|---|---:|")
    for name in sorted(by_decade):
        w(f"| {name} | {by_decade[name]:,} |")
    w("")

    w("## Shows by decade of first air")
    w("")
    show_decade = collections.Counter(decade(s["year"]) for s in shows)
    w("| Decade | Shows | Episodes |")
    w("|---|---:|---:|")
    for name in sorted(show_decade):
        eps = sum(s["episodes"] for s in shows if decade(s["year"]) == name)
        w(f"| {name} | {show_decade[name]:,} | {eps:,} |")
    w("")

    # The genre tags are broad enough that some pools need eyeballing before
    # they can be scheduled -- "Western" includes Cowboy Bebop.
    w("## Small pools, listed in full")
    w("")
    w("Anything under 50 shows or 50 films is printed here, because at that "
      "size the tag needs a human to look at it before it becomes a channel.")
    w("")
    for name, include, exclude in POOLS:
        series = select(shows, include, exclude)
        if 0 < len(series) <= 50:
            eps = sum(s["episodes"] for s in series)
            w(f"### {name} — {len(series)} shows, {eps:,} episodes")
            w("")
            w("| Show | Year | Episodes | Genres |")
            w("|---|---:|---:|---|")
            for s in sorted(series, key=lambda s: -s["episodes"]):
                genres = ", ".join(sorted(s["genres"]))
                w(f"| {s['title']} | {s['year'] or '—'} | {s['episodes']:,} | {genres} |")
            w("")

    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Census the media on disk.")
    parser.add_argument("--media-root", default=MEDIA_ROOT)
    parser.add_argument("--out-dir", default="scripts/reference")
    args = parser.parse_args()

    movies = read_movies(args.media_root)
    shows = read_shows(args.media_root)

    os.makedirs(args.out_dir, exist_ok=True)

    write_tsv(os.path.join(args.out_dir, "library-movies.tsv"), movies, [
        ("title", lambda m: m["title"]),
        ("year", lambda m: m["year"] or ""),
        ("genres", lambda m: "; ".join(sorted(m["genres"]))),
        ("runtime_min", lambda m: m["runtime"]),
        ("tier", lambda m: m["tier"]),
    ])
    write_tsv(os.path.join(args.out_dir, "library-tv.tsv"), shows, [
        ("title", lambda s: s["title"]),
        ("year", lambda s: s["year"] or ""),
        ("episodes", lambda s: s["episodes"]),
        ("genres", lambda s: "; ".join(sorted(s["genres"]))),
        ("studio", lambda s: s["studio"]),
        ("folder", lambda s: s["folder"]),
    ])

    analysis = os.path.join(args.out_dir, "library-analysis.md")
    with open(analysis, "w") as handle:
        handle.write(render(movies, shows, args.media_root))

    print(f"{len(movies)} films, {len(shows)} shows, "
          f"{sum(s['episodes'] for s in shows)} episode files")
    print(f"Wrote {args.out_dir}/library-movies.tsv, "
          f"{args.out_dir}/library-tv.tsv, {analysis}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
