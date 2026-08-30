# The Modern Movie Channel — build plan

> Step 4 of the film-policy work order. Steps 1–3 are done: the collision report
> exists, Classic Cinema handed back modern film, and Other Worlds / Mystery
> Theatre were settled by ownership. This is the channel those steps were
> clearing the way for.
>
> Numbers below are from `reference/library-movies.tsv` (2,063 films with a
> parseable year) and a fresh `collision_report` run, 2026-08-30.

---

## The finding that changes the shape

Steps 2 and 3 achieved **zero shared film pools** by giving every genre channel
an exclusive cut. That policy is correct for genre-vs-genre — Other Worlds and
Mystery Theatre are both narrow, and neither needed the Nick at Nite hours rule.
**It does not survive contact with a general movie channel**, because a general
movie channel is cross-genre by definition. Under the current policy it is not a
channel, it is a remainder.

The post-1990 live-action library is **1,234 films**. Here is what happens when
every *planned* owner takes its exclusive cut — including the two channels memory
records as going scripted, High Noon and Nightmare Theatre:

| Owner | Claims (1990+, live-action) |
|---|---:|
| Other Worlds | science fiction — 272 |
| Mystery Theatre | crime/mystery non-comedy — 260 |
| Nightmare Theatre *(planned)* | horror — 132 |
| fantasy *(parked, `library/fantasy.py`)* | fantasy — 170 |
| High Noon *(planned)* | western — 26 |

**571 films survive.** And the survivors are not a neutral slice — they are the
comedy/drama/romance half of the library with the spine pulled out:

```
comedy 345 · drama 309 · action/adventure 182 · romance 116
thriller 90 (down from 390) · family 42 · music 49 · war/history 69
```

A "video store" channel that cannot air *The Matrix*, *Se7en*, *Scream*, *Fargo*,
*Lord of the Rings* or *Blade Runner 2049* is not the channel in the plan. **This
is the one thing to settle before writing any blocks** — the same position the
Cabes Classic Cinema summer swap held last session.

571 films is not a volume problem. At a 117m mean runtime a 24h day is ~12.3
features and a year is ~4,504 slots, so 571 films repeat **7.9×/year** — Classic
Cinema lives on less. It is an *identity* problem.

---

## Recommendation: add a recency axis

Every ownership rule on this lineup so far has cut along **genre** (Other Worlds),
**era** (`classic_crime_movie` / `modern_crime_movie`, drawn at 1980), or **hours**
(Nick at Nite / Good Times). Recency is a fourth axis and **nothing else on the
lineup uses it** — which is exactly why it is free.

**The rule: the modern movie channel owns everything from 2018 on, across all
genres. Genre channels own their genre up to 2017.**

This is the crime split's shape — a date line, one genre pool cut in two, neither
channel able to draw the other's film — applied once, globally, at a different
year. It costs the genre channels very little:

| Channel | Total pool | Loses to 2018+ | |
|---|---:|---:|---|
| Other Worlds | 382 | 73 | 19% |
| fantasy *(parked)* | 238 | 31 | 13% |
| Nightmare Theatre | 242 | 29 | 12% |
| High Noon | 45 | 4 | 9% |
| Mystery Theatre | 365 | 27 | 7% |

Nobody loses their identity — Other Worlds keeps every sci-fi film made before
2018, which is where the canon is. And the movie channel gets the one thing the
residual pool could never give it: **a reason to exist that is not "the films
nobody else wanted."** New releases.

**Resulting pool: 692 films.** 1990s 217 · 2000s 153 · 2010s 170 · 2020s 152.
Repeat rate 6.5×/year.

### Why 2018 and not 2020

2020+ is 152 films — enough for a Friday appointment (2.9 years before a repeat
at one feature a night) but too thin to carry a daypart. 2018+ is 219, which
supports a nightly recent-film presence as well as the Friday event. If the
Friday block wants to feel genuinely *new*, run it off a tighter `2022+` key
(112 films) nested inside the wider claim.

### If this is rejected

The fallback is honest relabelling, not a smaller version of the same channel:
call it **comedy-and-drama**, program the 571 as its real identity, and drop the
"video store" framing. That is a coherent channel. It is just a different one,
and `MODERN_BLOCKBUSTERS` stays homeless either way — 439 of the 1990+ action
films are behind the sci-fi and crime lines.

---

## Grid

Uses the existing `"movies"` preset (`overnight` 0–6, `morning` 6–12,
`afternoon` 12–18, `prime` 18–24). Long slots, because a two-hour daypart map
cuts features in half. Same preset Classic Cinema runs, so no new timeslot map
and none of the midnight-wrap trouble CN and Nick had.

| Slot | Mon–Thu | Friday | Saturday | Sunday |
|---|---|---|---|---|
| 00–06 overnight | **The Late Shift** — cult, midnight comedy | ← | ← | ← |
| 06–12 morning | Catalogue, decade rotation | ← | **Weekend Matinee** — family/PG | ← |
| 12–18 afternoon | **Decade Afternoon** — `monthly_rotation()` | ← | **Double Bill** | ← |
| 18–24 prime | Decade Night | **NEW RELEASES** — the appointment | Saturday Night Feature | Sunday Drama |

**Friday prime is the whole channel's argument.** It is the only slot on the
lineup that promises something *recent*, and it is what the recency claim buys.
Two features, 18:00 and 21:00, off the tightest recency key available.

**`annual_show()` does not apply** — there are no seasons here. The mechanics
that do, all proven elsewhere:

- `monthly_rotation()` over decade pools — Nick and Disney both run it
- `SeasonalBlock` for a summer-blockbuster / autumn-thriller prime swap — note
  this is the swap Classic Cinema just gave up, landing where it belongs
- `Marathon` + `triggers.has_label` for date-anchored events, as CN now uses

---

## Registry work, before any blocks

This is the Disney/CN order — keys first, then blocks. `MOVIE_REGISTRY` has era
coverage for every decade but **genre × era only exists for the 80s and 90s**.

**New — recency (the whole recommendation depends on these):**

```
recent_movie          movie_source(era="release_date:[2018-01-01 TO *]")   # 219
new_release_movie     movie_source(era="release_date:[2022-01-01 TO *]")   # 112
```

**New — modern genre × era.** Verified counts, live-action:

| Key | Films | | Key | Films |
|---|---:|---|---|---:|
| `00s_action_movie` | 120 | | `10s_action_movie` | 127 |
| `00s_comedy_movie` | 115 | | `10s_comedy_movie` | 96 |
| `00s_drama_movie` | 162 | | `10s_drama_movie` | 156 |
| `00s_romance_movie` | 52 | | `10s_romance_movie` | 29 |

**Two traps in the existing registry, both live:**

1. **`blockbuster_action_movie` has no era filter.** It is
   `genre:action AND (studio:Marvel OR studio:DC OR tag:superhero)` — every era.
   It sits in `MODERN_BLOCKBUSTERS`, so handing that collection to this channel
   hands it pre-1990 superhero film too, straight into Totally 80s' decade. Add
   an era bound before use.

2. **A `modern_thriller_movie` key would be mostly other channels' film.**
   Thriller is 390 films at 1990+, but 189 are Mystery Theatre's crime/mystery
   and 153 are sci-fi or horror. **Only 90 are actually free.** Any thriller key
   needs `NOT genre:crime NOT genre:mystery NOT genre:"science fiction" NOT
   genre:horror` or it silently re-opens three settled borders — which is the
   failure mode step 3 spent a session closing.

---

## Open, and worth deciding now

**1. Is 1990 still the line?** Effectively yes, and not by choice — Totally 80s
owns `eighties_*`, which is the whole 1980–89 decade (315 films). "Video store
starts in 1985" would mean taking 182 films off Totally 80s, which is a Totally
80s decision, not a movie-channel one. Leave 1990.

**2. Classic Cinema's `WESTERN_MATINEE` is a collision waiting for High Noon.**
`movies.WESTERN_MATINEE` = `western_movie`, unbounded by era, on Classic Cinema's
weekend afternoon. Memory records High Noon as going scripted; westerns are only
45 films and it cannot afford to share them. Not this channel's problem to fix,
but it is the next `collision_report` finding after this build and it should be
written down before it surprises someone. Same shape as the sci-fi showcase
overlap that went unseen for four sessions.

**3. Channel name and number.** Still pending, as with Nick, Disney and CN.

**4. Horror is only unclaimed until Nightmare Theatre exists.** The 2018+ rule
settles this in advance rather than leaving it to be re-fought — which is the
point of drawing the line before either channel is built.

---

## Build order

1. **Settle the 2018 recency rule.** Everything below is downstream of it.
2. Add the recency and genre × era keys; fix the `blockbuster_action_movie` era
   bound; apply the thriller exclusions.
3. Add the 2018-cut to the genre channels' keys — Other Worlds, Mystery Theatre,
   `library/fantasy.py`. Five keys, mechanical, mirrors the crime split.
4. `library/modern_movies.py` — collections and blocks.
5. `channels/modern_movies.py` — grid, marathons, holiday schedules.
6. Simulate 365 continuous days; re-run `collision_report` and confirm the
   lineup is still at zero shared film pools.
