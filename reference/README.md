# Library Reference

Snapshots of the local media library, for use when writing channel and
block definitions.

> **Local only.** The seven `library-*` snapshots below are gitignored — they
> inventory a personal collection, so they live on disk but are not published.
> Regenerate them with the commands in the tables; the links here resolve only
> in a local checkout.

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
| [channel-rules.md](channel-rules.md) | **The rules for making and curating channels** — founding, grid, cross-channel curation, and the checks a channel passes before it counts as built |
| [metadata-facets.md](metadata-facets.md) | **What a content key can select on** — the 9,672-tag TMDB vocabulary the manifests drop, every `tag:` key evaluated for real, and the facets and keyword sweeps to build calendar and holiday keys from. `python3 -m scripts.testing.metadata_census` |
| [lineup-audit.md](lineup-audit.md) | **The 2026-09-03 depth-and-programming audit** — content per channel measured over a year, the 102 orphan shows, and where marathons, seasons and appointments are unused |
| [guide-site-plan.md](guide-site-plan.md) | **The plan for the listings-magazine website** — what the live feed carries, the XMLTV horizon settings, where per-title trivia comes from, and the publishing risk review |
| [channel-plan.md](channel-plan.md) | The working plan — lineup, programming mechanics, sharing rules, gaps |
| [acquisitions.md](acquisitions.md) | What the lineup is missing, per channel — the gap each acquisition fills |
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

The manifests are also consumed by two checkers, both offline:
`scripts/testing/validate_titles.py`, which checks that every scheduled *title*
resolves, and `scripts/testing/key_census.py`, which resolves every *key* in
`MASTER_SOURCES` against them and fails on any key a collection lists that
selects nothing. Regenerate the manifests when the library changes — a stale
manifest makes both checkers wrong in the direction of false alarms.
