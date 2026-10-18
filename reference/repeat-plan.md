# Repeats: the plan

Started 2026-10-18 from a report on Cartoon Network's weekend: Titan A.E. "almost
every Sunday", and the day's shows airing two or three times. The audit found
five causes. One of them sat in the engine and hit every channel; it is fixed. The
rest are per-channel configuration and are worked through below, Cartoon
Network's weekend first, then the method is applied to the rest of the lineup.

## The rule

The operator's words, 2026-10-18:

> I don't mind if the last show or two in the block are the block starting over
> again, because then the first show would have at least five shows between it
> and it airing again. What I really don't like is a show airing twice in a row,
> three times in a row, or shows bouncing back and forth, like Dexter's Lab to
> Powerpuff, and back and forth over and over again.

As a pass/fail test, per channel per day, with consecutive segments of one show
merged into a single airing:

- **Fail:** the same show twice in a row; three times in a row; two shows
  alternating (A B A B).
- **Fail:** a show back on the same day with fewer than four other shows between
  (five was the first wording; the operator relaxed it to four on 2026-10-18).
- **Pass:** a block that wraps to its first show or two at the tail, once at
  least four other shows have aired between.
- **Segments:** two of the same short show back to back is one airing; three is
  not. `_half_hour()` groups two at most.
- **Exempt:** deliberate repeats — marathons, double features, a power hour of
  two consecutive episodes. These are declared, not accidental.

Toonami-style blocks should hold one pick per show for the whole window, so a
block that wraps needs about six shows or more. This tightens the block repeat
rule recorded on 2026-09-27 (each block plays each show once; group short
segments into half-hour picks).

## What the audit found

Measured on the live `xmltv.xml` for 2026-10-03 to 10-22.

### 1. Rotations restarted at every mid-day build — all channels — FIXED

ErsatzTV runs a `continue` build from wherever the playout ends, usually
mid-day, and each build is a fresh process. Collections keep their place in
the day in memory, so the first pick after a build boundary repeated the day's
first pick. Proof from the guide:

| When | What |
|---|---|
| Sun 10-11 | Ed, Edd n Eddy opens the block at 09:03, 12:21 and 13:07 — each is `day_offset % 5`, step zero |
| Sun 10-11 | Rick and Morty at 22:21 and again at 23:06 |
| Sun 10-18 | Metalocalypse at 22:06 and 23:18; The Boondocks at 22:29 and 23:42 |

ARCHITECTURE.md promised "the same date produces the same schedule across
restarts", which was only true of a restart at midnight. The fix is the **pick
ledger** (`core/pick_ledger.py`): every collection pick is recorded with its time
under `logs/state/<channel>.json`, and a build that starts at T replays the day's
picks before T so every collection resumes in place. A plain-list block cut off
mid-list resumes at its next item. Verification:

- **Split builds.** 16 channels × 8 split points, each a two-process build
  compared against one continuous build. Without the ledger 61 of 128 diverged
  after the split. With it, 127 match exactly. The last one matches on every
  show and differs only by a skipped block outro (see open items).
- **Unchanged from midnight.** A seven-day build starting at 00:00 is
  byte-identical to the old code on all 16 channels, so the ledger only changes
  builds that resume mid-day.
- 90 unit tests pass.

### 2. Cartoon Theatre's film has no memory across weeks — CN

`RandomCollection` resets each day by design, and Cartoon Theatre has one
pick a week, so every Sunday is an independent draw from seven films. Replaying
the real seed: Titan A.E. on **10-18, 10-25 and 11-01**; ten Sundays in the
next 52 against Roger Rabbit's three. Separately, the Dragon Ball Z: Battle of
Gods entry never plays the film — on 10-11 the slot aired stray Dragon Ball
episodes and two hours of Looney Tunes instead.

### 3. One Cartoon Cartoons list in two slots on the same day — CN

`CARTOON_CARTOONS_WEEKEND` (five shows) is used at 08:00–10:00 Saturday, and at
09:00–10:00 and 12:00–14:00 Sunday. On Sunday 10-18 Dexter, Powerpuff, Johnny
Bravo, Ed Edd n Eddy and Courage each aired twice. Saturday wraps to Courage.

### 4. Sunday FOX repeats on purpose — CN

`FOX_PRIMETIME` lists Simpsons, King of the Hill and Family Guy twice each to
fill three hours with six shows. That breaks the rule.

### 5. Toonami Saturday 20:00–23:00 is short — CN

Six shows against about eight picks, so Sailor Moon and InuYasha air twice;
Samurai Jack and Batman Beyond have also already aired earlier that day.

### Also seen

The two weekend days are near-copies: each runs Cartoon Cartoons, the modern CN
shows, the syndication package and Action Hour, in a different order. It isn't a
same-day repeat, but it is why the weekend reads as samey.

## Decisions made (2026-10-18)

- **Sunday FOX shortens to 19:00–21:00**: six shows, each once, the real
  Animation Domination shape. Adult Swim takes Sunday from 21:00.
- **Sunday becomes its own day** rather than a reshuffle of Saturday's blocks.
  The anchor is a **Sunday Cartoon Theatre double feature** around midday.
  Draft the grid and show it before building.
- **The film roster expands** beyond what aired on Cartoon Network (below).
- **The ledger writes beside the logs**, in `logs/state/`.

## Second pass, 2026-10-18 — what the live guide showed after the ledger

The operator deployed the ledger, reset Cartoon Network and still saw repeats.
The ledger was not the cause of what they saw; these were:

- **Three segments per pick.** Dexter, Johnny Bravo, Looney Tunes, Tom and
  Jerry, Yogi Bear and Popeye played three in a row. Now two.
- **One show, several chronological feeds.** `cn_daytime_`, `cn_weekend_`,
  `cn_prime_` and `cn_friday_` were four positions on the same run; so were
  `fox_weekday_`/`fox_sunday_`, `toonami_weekday_`/`toonami_saturday_`, and
  Batman Beyond and Samurai Jack in two places each. A reset rewinds every key,
  so all of them opened on the same episodes a day apart. Merging them into one
  key per show was tried and rejected by the operator the same day: the split
  is the point, as with a network's prime-time run and a station's 7pm reruns.
  The split stays, and the second feed now opens well into the show:
  `playback_order(..., start=(season, episode))`, applied once on a reset
  build (core/build_mode.py). Weekday prime, the weekday Toonami block and the
  weekday FOX pair run from episode one; `cn_weekend_*`, `fox_sunday_*` and
  `toonami_saturday_*` start one-half to three-quarters in. Weekday-morning
  Cartoon Cartoons (`cn_daytime_*`) are shuffled. Weekday Dragon Ball Z
  restarts at episode one on 2026-10-19; Saturday's opens on the Android saga,
  S04E19.
- **Season 0 in the rotations.** A bare title includes the specials and TV
  movies: The Flintstones' I Yabba-Dabba Do! took 92 minutes of a weekday
  morning, and its Christmas specials aired on October Saturdays.
  `episodes_without_specials()` (library/queries.py) now backs every CN feed
  and title item.
- **18:00 outside prime's rotation.** The fixed weekday pairs repeated prime's
  shows within the hour (Adventure Time 18:21 and 19:45). 18:00 now draws from
  prime's own rotation; Friday's takes the four shows CCF never airs.
- **Toonami padding.** Up to eighteen minutes of `toonami_bumpers` closed the
  block. Toonami is now 16:00–18:00 — Dragon Ball, two Dragon Ball Z, one show
  from a five-show rotation, then ThunderCats or Pokémon alternating by day.
  The afternoon ahead of it is now Marvel and SWAT Kats at 12:00, Scooby at
  13:00 and the DC Action Hour 14:00–16:00, leading into Toonami.

Simulated week of 2026-11-09 with real segment lengths: four failures before
(all 18:00-against-prime), one after (Home Movies across two Adult Swim blocks,
Monday 01:10 and 03:25, pre-existing).

**Not yet fixed: the Halloween schedule.** The same check over 10-19 to 10-25
fails 23 times, all inside the Halloween takeover: `CN_HALLOWEEN` and the
overnight horror slot are small `RandomCollection`s, and they ping-pong
(Metalocalypse, horror, Metalocalypse; Halloween cartoons, Scooby, Halloween
cartoons).

## Phase 1 — Cartoon Network's weekend

1. ~~Pick ledger (engine).~~ Done 2026-10-18.
2. ~~**Calendar shuffle-bag for weekly film slots.**~~ Done 2026-10-18 as
   `CalendarDeck` (logic/structures.py); Battle of Gods fixed (it is a movie,
   not a season-0 episode). Deal every film once per
   cycle in an order fixed by the calendar: cycle = week number // N, with the
   order shuffled by a seed derived from the cycle, and the first film of a new
   cycle never equal to the last of the old one. It needs no state, and a film
   comes back every N weeks rather than whenever the dice say so. Fix or drop
   the Battle of Gods entry.
3. **Expand the film roster** (below) and give it two Sunday slots plus one
   Saturday slot. *Sunday done 2026-10-18:* 58 films, a double feature at
   10:00 and 12:00 dealt from one deck, replacing the 12:00 Cartoon Cartoons
   rerun. The rare Saturday 16:00 movie is now the shows' own TV movies
   (season 0, 16 of them). Still open: the Saturday Ghibli slot.
4. **Sunday grid**: replace the 12:00 Cartoon Cartoons rerun; FOX 19–21; Adult
   Swim from 21:00 with enough shows that 21:00–02:00 does not cycle.
5. **Toonami Saturday 20–23**: enough shows for one pick each, none already seen
   that day.
6. Verify: schedule diff of all channels before/after; the repeat counter
   against the live guide after the deploy and a reset.

## Phase 2 — tooling

- **`testing/repeat_check.py`**, the repeat counter. It reads only: it pulls the
  live `xmltv.xml`, merges consecutive segments of one show into one airing, and
  reports per channel per day every same-day re-air with its gap, failing on the
  rule above. Same as `continuity_check`, it reads the guide rather than a
  simulation, because the guide is what aired. A draft produced the numbers
  below.
- **The same check over a simulation**, so a config change can be measured
  before it is deployed. Use real runtimes; the simulator's flat guess hides
  segment-length problems.
- **A static checker** over the channel modules that flags:
  - one collection used in more than one slot on the same day, where the slots
    need more picks than the collection has shows;
  - a block with fewer shows than its window has picks;
  - a `RandomCollection` in a slot that comes round less than daily, which has
    no memory across days (the Titan A.E. shape).

## Phase 3 — the rest of the lineup

The ledger is lineup-wide, so re-measure after it deploys before touching any
channel config; much of what follows may already be gone. Weekend reruns per
day before the fix (draft counter, 2026-10-08 to 10-21):

| Channel | Same-day re-airs/day | Within 3h | Worst |
|---|---|---|---|
| Nickelodeon | 54.8 | 45.8 | Magic School Bus, Schoolhouse Rock!, Ren & Stimpy |
| Good Times | 41.8 | 36.8 | Martin, Married... with Children, Moesha |
| Disney | 41.8 | 34.0 | Rescue Rangers, Buzz Lightyear, DuckTales |
| Totally 80s | 27.5 | 19.8 | music videos — different rule |
| Japanorama | 26.8 | 22.0 | Tatami Galaxy, Dragon Ball, DAN DA DAN |
| Corncob TV | 22.0 | 19.2 | Strangers with Candy, Man Seeking Woman |
| Cartoon Network | 21.5 | 19.2 | Courage, Johnny Bravo, Dexter |
| Across the Pond | 17.0 | 13.5 | Mr. Bean, Wallace & Gromit shorts |

Then worst first, per channel: run the static checker, fix block sizing and
same-day reuse, re-measure. The Beat (music videos by artist) needs its own rule
and is out of scope here. Schoolhouse Rock! is interstitial-length and may be
legitimate.

## The film roster

205 animated films are on disk. Two shelves are taken: Disney and Pixar are the
Disney channel's (`disney_movie`, `pixar_movie`); Japanese features are
Japanorama's (`ghibli_movie`, `anime_*_movie`). The operator has cleared Ghibli for
Cartoon Network, and the sharing rule only forbids the same title at the same
time. Japanorama runs Ghibli all Sunday evening, so Cartoon Network's Ghibli
goes on Saturday.

Roughly 65 more are claimed by no channel:

- **CN / Hanna-Barbera / Warner:** The Iron Giant, Batman: Mask of the Phantasm,
  Steven Universe: The Movie, Charlotte's Web, Once Upon a Forest, The Lego Movie,
  The Lego Batman Movie, Happy Feet 1–2, The Day the Earth Blew Up.
- **Rankin/Bass and classics:** The Hobbit (1977), Yellow Submarine, Watership
  Down, The Secret of NIMH, An American Tail 1–2, The Land Before Time, All Dogs
  Go to Heaven, The Brave Little Toaster, FernGully, The Pagemaster.
- **DreamWorks and others:** Antz, The Prince of Egypt, The Road to El Dorado,
  Chicken Run, Shrek, Madagascar, Kung Fu Panda 1–3, How to Train Your Dragon,
  Megamind, Rise of the Guardians, Ice Age, Cloudy with a Chance of Meatballs,
  The Mitchells vs. the Machines, The Wild Robot, Spider-Verse 1–2, TMNT: Mutant
  Mayhem, Transformers One, The Super Mario Bros. Movie, KPop Demon Hunters,
  Klaus, The Sea Beast.
- **Stop-motion and arthouse:** Coraline, Fantastic Mr. Fox, Isle of Dogs, the
  Wallace & Gromit features, The Secret of Kells, Song of the Sea, Wolfwalkers,
  Flow, Guillermo del Toro's Pinocchio.

Handled separately:

- **Holiday-only:** Rudolph, Frosty, The Year Without a Santa Claus, the Grinch,
  A Charlie Brown Christmas, The Snowman; The Halloween Tree (Hanna-Barbera,
  1993) for Cartoon Network's Halloween.
- **Sunday FOX night:** The Simpsons Movie, The Bob's Burgers Movie.
- **Post-film fill instead of Looney Tunes:** A Grand Day Out, The Wrong
  Trousers, A Close Shave, Paperman, One Small Step.
- **Adult Swim hours or nowhere:** South Park: Bigger, Longer & Uncut,
  Anomalisa, Waking Life, Cool World, The Animatrix.
- **Nick properties that may belong on Nick:** Invader Zim: Enter the Florpus,
  Avatar Aang.

At one film a week about 88 films is a two-year cycle, which is the case for
the double feature and the Saturday slot. Check every addition with
`same_title_check` / `same_show_check` against Be Kind Rewind and Cabes Classic
Cinema, whose `studio:`/`tag:` keys score as supersets and need reading by hand.

## Open items left by the ledger

- **Is `logs/` writable in the ErsatzTV container?** If not, the ledger warns
  once per build and the channel behaves as before. Check the first build log
  after deploying for `Pick ledger not saved`.
- **The backup must not clobber it.** `backup.sh` mirrors the project to hdpool
  with `--delete`; `logs/state/` is excluded so a mirror never overwrites or
  removes the server's ledger.
- **A block's outro is skipped when a build boundary falls between its last
  show and the outro.** This is cosmetic and was already the case before the
  ledger; the next slot starts a few minutes early.
- **`DayDirector.pick()` / `pick_weighted()` streams are not replayed.** They
  are used for one-off choices (resolving a list key, a marathon's season), not
  rotations. Revisit only if the repeat counter points at one.
