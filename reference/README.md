# Library Reference

Snapshots of `/media` taken 2026-08-29, for use when writing channel and block definitions.

| File | Contents |
|---|---|
| [library-tv-all.txt](library-tv-all.txt) | All 576 TV shows |
| [library-movies-all.txt](library-movies-all.txt) | All 2,067 movies |
| [library-animation-tv.md](library-animation-tv.md) | 151 animated series with episode and season counts |
| [library-animation-movies.md](library-animation-movies.md) | 94 animated features, grouped by studio |
| [bumper-inventory.md](bumper-inventory.md) | Interstitials in `filler/`, cross-referenced against what airs |
| [cartoon-network-review.md](cartoon-network-review.md) | Programming review of the Cartoon Network channel |
| [channel-plan.md](channel-plan.md) | The working plan — lineup, programming mechanics, sharing rules, gaps |
| [next-session.md](next-session.md) | Build order and carry-forward notes for CN / Disney |
| [channel-coverage.md](channel-coverage.md) | All 576 shows + 2,067 movies mapped to channels; orphans and conflicts |

Episode counts come from files under `Season NN/` folders. Two shows read as zero and need attention: `Bullwinkle Show, The (1959)` is an empty directory, and `Smurfs, The (1981)` holds 405 episodes flat with no season folders and no `tvshow.nfo`.

Regenerate the flat lists with `ls /media/tv` and `ls .../movies`. Per-file `.nfo` genre scanning over NFS is impractically slow — the animation lists were built by title sweep and hand-checked.

The manifests are also consumed by `scripts/testing/validate_titles.py`, which checks that every scheduled title still resolves. Regenerate them when the library changes.
