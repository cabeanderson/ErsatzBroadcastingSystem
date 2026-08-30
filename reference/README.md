# Library Reference

Snapshots of `/media`, for use when writing channel and
block definitions.

## Generated — do not edit by hand

Four files are produced by scripts and regenerate in seconds. Regenerate them
when the library changes or the registry does.

| File | Contents | Regenerate with |
|---|---|---|
| [library-movies.tsv](library-movies.tsv) | 2,063 films: title, year, genres, runtime, tier | `python3 -m scripts.testing.library_census` |
| [library-tv.tsv](library-tv.tsv) | 575 shows: title, year, episode count, genres, studio | same |
| [library-analysis.md](library-analysis.md) | Genre pools sized for channel decisions, plus full listings of small pools | same |
| [registry-inventory.md](registry-inventory.md) | All content keys, their queries, and which channels air them | `python3 -m scripts.testing.media_inventory` |

`library-analysis.md` answers "is there enough content for a channel";
`registry-inventory.md` answers "can the scheduler address it". Those are
different questions and a pool can be large in one and unreachable in the other.

## Hand-maintained

| File | Contents |
|---|---|
| [library-tv-all.txt](library-tv-all.txt) | Flat list of TV show folders |
| [library-movies-all.txt](library-movies-all.txt) | Flat list of movie folders |
| [library-animation-tv.md](library-animation-tv.md) | 151 animated series with episode and season counts |
| [library-animation-movies.md](library-animation-movies.md) | 94 animated features, grouped by studio |
| [bumper-inventory.md](bumper-inventory.md) | Interstitials in `filler/`, cross-referenced against what airs |
| [cartoon-network-review.md](cartoon-network-review.md) | Programming review of the Cartoon Network channel — **implemented**, see its status header |
| [channel-plan.md](channel-plan.md) | The working plan — lineup, programming mechanics, sharing rules, gaps |
| [next-session.md](next-session.md) | Build order and carry-forward notes — framework bugs found in the CN restructure, then the collision report |
| [channel-coverage.md](channel-coverage.md) | All 576 shows + 2,067 movies mapped to channels; orphans and conflicts |

Episode counts come from files under `Season NN/` folders.

Two long-standing exceptions were resolved on 2026-08-30. **Smurfs** is reorganized and indexes: 8 season folders, 367 episodes, `tvshow.nfo` present — season 9 is still missing, and the count is down from the 405 loose files because of it. **Bullwinkle** is no longer in `tv/` under any name and has been dropped from these lists; the files exist elsewhere but have not been identified or placed, so nothing can schedule it yet.

`Popeye the Sailor (1933)` seasons are foldered by broadcast **year** (`Season 1943` … `Season 1949`), not by season number. It indexes, but any query using `season_number:` against it means the year.

Regenerate the flat lists with `ls /media/tv` and `ls .../movies`.

**Correction (2026-08-30):** this file previously said per-file `.nfo` genre
scanning over NFS was impractically slow, which is why the animation lists were
built by title sweep and hand-checked. It is not — `library_census.py` parses all
575 `tvshow.nfo` files and walks 42,412 episode files in a few seconds. Movie
genres come free from `movies/LIBRARY-INVENTORY.csv`, which was already probed.
Genre data is cheap; the hand-built lists were solving a problem that no longer
needs solving.

The manifests are also consumed by `scripts/testing/validate_titles.py`, which checks that every scheduled title still resolves. Regenerate them when the library changes.
