# Reference

The programming method behind the lineup: how channels get founded, how the
grid is built, how content is curated across channels, and how a break is
composed. These are the documents the channel code was written against, and
they are meant to be reusable — the reasoning is portable even though the
collection it was applied to is not.

## The method

| File | Contents |
|---|---|
| [channel-rules.md](channel-rules.md) | **The rules for making and curating channels** — founding, grid, cross-channel curation, and the checks a channel passes before it counts as built. The law, with the channel that proved each rule. |
| [channel-plan.md](channel-plan.md) | The working plan — lineup, programming mechanics, sharing rules, and the design of each channel. |
| [filler-taxonomy.md](filler-taxonomy.md) | **The filler tree** — how ErsatzTV derives tags from folder paths, the applied reorganisation, the commercial gates, and the movie trailer/extras farm. |
| [interstitial-policy.md](interstitial-policy.md) | **When a break happens and what goes in it** — the smart-bumper modes and the break invariant. |
| [interstitial-acquisition.md](interstitial-acquisition.md) | **Where interstitial material is and how to get it** — archive.org identifiers per gap, and the fetch/split/delete cycle. |
| [guide-site-plan.md](guide-site-plan.md) | **The plan for the listings-magazine website** — what the live feed carries, the XMLTV horizon settings, and the publishing risk review. |

## Worked examples

Two channel designs kept as written, for the reasoning rather than the result.

| File | Contents |
|---|---|
| [cartoon-network-review.md](cartoon-network-review.md) | Programming review of the Cartoon Network channel — **implemented**; see its status header for what shipped differently. |
| [modern-movies-plan.md](modern-movies-plan.md) | Build plan for a modern film channel — **superseded**; it shipped as Be Kind Rewind. |

## Library snapshots — local only, not published

Channel and block definitions are written against manifests of the actual
library: what is on disk, how large each genre pool is, and which keys resolve
to nothing. Those files inventory a personal collection, so they are gitignored
— they exist in a working checkout and not in this repository.

Nothing in the framework needs them at runtime. They are inputs to writing
channels, and to two offline checkers: `scripts/testing/validate_titles.py`,
which checks that every scheduled *title* resolves, and
`scripts/testing/key_census.py`, which resolves every *key* in `MASTER_SOURCES`
and fails on any that selects nothing.

Both ask what the *library* can satisfy. A third asks what the *schedule* can
reach, which is neither — it needs no library and no server, only the config:

```bash
python3 -m scripts.testing.unaired_check      # config the schedule never selects
```

`unaired_check` exists because a branch of a channel's configuration can name
real content, type-check, pass every other checker, and still never be chosen.
Disney's Star Wars reruns block was unreachable on all seven days of the week —
its parent routed the weekend away before the branch was consulted, and Mon–Fri
always carries the `WEEKDAY` label that shadowed it. It simulates three years,
diffs what aired against what the config declares, and separates a genuinely
dead branch from a random collection that merely did not get round to
everything.

Two further checkers ask what the server actually *aired*, which is a different
question again and catches what the manifests cannot see:

```bash
python3 -m scripts.testing.continuity_check --future-only   # dead air
python3 -m scripts.testing.key_airing_check                 # keys that never play
```

`key_airing_check` exists because a block with a working `fallback_content` can
schedule a key that selects nothing and still look perfectly healthy — no gap,
no error, and the wrong content on air. A gap is a loud failure; a fallback is a
silent one.

Generate your own against your own library:

```bash
python3 -m scripts.testing.library_census      # film + TV manifests, genre pools
python3 -m scripts.testing.media_inventory     # every content key and what airs it
python3 -m scripts.testing.metadata_census     # what a query can actually select on
```

All three read `config.MEDIA_ROOT`, or take `--media-root`. See
[Configuration](../README.md#configuration).

> A stale manifest makes both checkers wrong in the direction of false alarms.
> Regenerate when the library changes.

## Notes that outlived their file

Two library quirks worth knowing, because they change what a query means:

* **Season folders named by year.** `Popeye the Sailor (1933)` is foldered by
  broadcast year (`Season 1943` … `Season 1949`) rather than season number. It
  indexes fine, but `season_number:` against it means the year.
* **Episode counts** come from files under `Season NN/` folders, so a show
  whose seasons are not foldered that way will count as zero.
