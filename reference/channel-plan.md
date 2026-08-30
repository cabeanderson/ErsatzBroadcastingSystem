# Channel Plan

Working plan for the scripted-schedules lineup. Companion to [channel-coverage.md](channel-coverage.md) (what exists and where it goes) and the library references in this directory.

---

## The organizing principle

**A tune-in channel needs episodes that stand alone.**

This is the rule everything else follows from. ErsatzTV earns its keep when you don't know what to watch and you turn something on — which only works if any given episode is enjoyable cold. Serialized shows fail that test: nobody tunes in mid-season-2 of *Six Feet Under*, they select it. Those belong on-demand.

Every channel already in the lineup selects for episodic content without anyone having decided it: sitcoms, westerns, detective-of-the-week, horror anthology, cartoons, sketch, cooking, DIY, 80s action. That is why they work, and it is why ~75% of the 108 unhomed shows are unhomed — they're serialized.

The escape hatch is `annual_show()` Broadcast Mode: one season a year, chronological, weekly, reruns filling the gap. That converts a serialized show into appointment TV, which is a different promise — "this channel has a Thursday show" rather than "turn it on whenever."

**How many a channel can carry is not a number.** What governs it is whether each appointment has its own night and its own bed. An appointment needs a slot that gates it — a weekday arm of the schedule, not `frequency` — and something to run in that slot the other fifty weeks. Give it both and a channel can carry one or six; High Noon carries six, one a night, with a film bed under each. What breaks a channel is appointments sharing a slot, because a `DailyOrderedCollection` that wraps replays the same episode twice a night — which is the actual defect behind Good Times' `MUST_SEE_THURSDAY`, and it happens at four appointments in one slot just as readily as at two.

---

## Lineup

### Existing

| # | Channel | Content | Scripted |
|---|---|---|---|
| 104 | Across the Pond | British comedy & panel | yes |
| 116 | Cartoon Network | CN originals + Toonami + Adult Swim | yes — **rebuilt** |
| 120 | Lucy TV | I Love Lucy 24/7 | no |
| 142 | Cabes Classic Cinema | classic film | yes — modern film **and westerns** handed back |
| 144 | Mystery Theatre | detective / procedural | yes — **refined** |
| 151 | Other Worlds | science fiction | yes — **refined**, fantasy & horror removed |
| 164 | Japanorama | anime | no |
| 180 | Totally 80s | 80s TV — **stays 80s** | yes |
| 190 | Good Times | sitcoms | yes |
| — | Nick (+ Nick at Nite) | Nicktoons, WB animation, classic TV | yes — **built**, channel number pending |
| — | Disney | Disney Afternoon, ABC mornings, Star Wars animation | yes — **built**, channel number pending |
| 240 | Travelers Table | cooking — **+ nature docs** | no |
| 241 | Makers Corner | DIY & craft | no |
| 242 | Corncob TV | absurd comedy | no |
| 243 | High Noon | westerns | yes — **built**. The TV is the spine: 946 episodes, five B&W shows |
| 244 | Nightmare Theatre | horror, TV + film | no — 244 films, but horror TV is only 21 shows / 799 eps |
| 246 | The Beat | **music videos only** | no |

### To build

| Channel | Pool | Shows | Notes |
|---|---:|---:|---|
| **Modern movies** | ~1,390 films | — | **Next.** 1990-present, 67% of the movie library. Classic Cinema's summer swap is gone, so the contention is resolved |
| **Fantasy** | 238 films / 40 shows | 40 | Registry and `library/fantasy.py` built 2026-08-30; **channel deliberately deferred**. Content is there — 333 fantasy films, more than horror |
| ~~Boomerang~~ | 1 show | 1 | **Closed — see below.** Disk problems fixed; the premise is what is gone |

---

## Channel notes

### Cartoon Network — rebuilt
`scripts/channels/cartoon_network.py` · `scripts/library/animation.py`

Restructured against [cartoon-network-review.md](cartoon-network-review.md), which is the audit this grid came from. The channel was giving **27 hours a week to Disney and 13 to Nickelodeon** while Cartoon Network's own originals held five, and Adult Swim ran 20:00–02:00 with Hanna-Barbera behind it until 06:00 — the exact inverse of the real thing. Both other claimants on the animation library were built first, so the eviction list was written down rather than derived.

| Slot | Mon–Thu | Friday | Saturday | Sunday |
|---|---|---|---|---|
| 00–02 after hours | Midnight Run | Midnight Run | Midnight Run | Adult Swim originals *(Sun night)* |
| 02–06 overnight | Adult Swim, acquisitions | ← | ← | **Toonami: The Midnight Run** *(Sat night)* |
| 06–08 early | The Vault | ← | ← | ← |
| 08–10 morning | Cartoon Cartoons | ← | Saturday Morning | The Scooby Block |
| 10–12 midday | Cartoon Network | ← | Cartoon Cartoons | The Vault |
| 12–14 noon | The Vault | ← | Syndication Hour | Cartoon Theatre |
| 14–17 afternoon | Action Hour | ← | Action Hour | Cartoon Network |
| 17–20 evening | **Toonami** | Cartoon Cartoon Fridays | **Toonami Saturday** | Cartoon Cartoons |
| 20–23 prime | Adult Swim originals A/B | A | Toonami Saturday cont. | FOX Primetime |
| 23–24 night | Midnight Run | Midnight Run **premiere** | Midnight Run | Adult Swim originals |

Simulated over 365 continuous days: no gaps, no circuit breakers, no unresolved programs. Airtime share of ~21,000 programme plays — **CN originals 22.6%, anime/Toonami 16.7%, Adult Swim originals 11.1%** (50.4% between them, against ~9% before), acquisitions 14.3%, the vault 19.3%, superhero 9.9%. Disney and Nickelodeon are at zero.

**Adult Swim runs last, not first.** Originals at 20:00, the anime Midnight Run at 23:00, acquisitions 02:00–06:00. The old grid had the 2009–2014 acquisitions as the 20:00 marquee and the Williams Street originals behind them.

**Own timeslot map, split at midnight.** The default preset's `night: (23, 2)` wraps, and a wrapping slot is entered twice under two different day labels — so "Sunday night" resolved to two different nights and a `DailyOrderedCollection` replayed its first items across the boundary. `night` is 23–24 and `after_hours` is 00–02, each with its own block. Same reason Nick and Disney carry their own maps.

**Two appointments, both day-gated by their block.** Dragon Ball DAIMA (20 eps) premieres Saturdays inside Toonami Saturday; Attack on Titan Junior High (12 eps) premieres Fridays at 23:00 inside a Friday-only variant of the Midnight Run. The gating has to come from the slot — `frequency` only paces the episode index, it does not stop the appointment airing on other days. See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md).

**Per-show bumpers are wired.** ~940 Toonami and 5,316 Adult Swim files were unreachable; each Toonami and Adult Swim item now carries its own set through a `Program` wrapper (`animation._with_bumpers`). `play_smart_bumper` would find them by title on its own, but it requires a `bumpers` tag and the trees are tagged `bumps`/`shows`.

**No daytime filler.** `filler_content="adult_swim_bumpers"` was channel-wide and only the five branded blocks overrode it, so ~14 hours of every 24 — Saturday-morning Scooby-Doo included — ran Adult Swim bumps. There is nothing to replace it with: `filler/bumpers/cartoon network/general/` is empty and the 110 files under `commercials/90s` are mislabelled 2000s British adverts. Silence is closer to Cartoon Network than Adult Swim is. Sourcing checkerboard / Powerhouse / CN City branding is the outstanding asset job.

Summer (Jun–Aug) hands weekday 08:00–14:00 to CN's own shows and drops the vault from lunchtime; spring still leans Marvel, in the Action Hour rather than the retired 08:00 superhero hour. Marathons are date-anchored — Thanksgiving and New Year's Toonami, July 4th DBZ, Memorial Day Bebop, first Saturday of the month CN — each keeping its old random chance on top via `triggers.any_of`.

### Disney — built
`scripts/channels/disney.py` · `scripts/library/disney.py`

Three eras of one studio, dayparted so they never argue: the ABC morning cartoons at 06:00–08:00, **The Disney Afternoon** at 15:00–17:00, the modern Disney Channel shows after school at 17:00–19:00, and Star Wars 19:00–24:00. 22 shows, 1,364 episodes.

The channel carries its own timeslot map. The default preset puts afternoon at 14–17 and prime at 20–23; the Disney Afternoon is two hours ending at 17:00, so noon becomes 12–15, afternoon 15–17, prime 19–21 and the night splits at 21:00.

**The bench is three strips, not four.** Overnight, morning and midday ride `monthly_rotation()` over four pools — Duckburg (DuckTales, Darkwing Duck, Chip 'n' Dale), Disney Adventure (TaleSpin, Gargoyles, Goof Troop), One Saturday Morning (Aladdin, Hercules, Pepper Ann), Disney Action (Kim Possible, Buzz Lightyear, Mighty Ducks) — each starting the cycle a month apart. 902 episodes.

Noon (12:00–15:00) is deliberately held **off** the bench. Duckburg and Disney Adventure are the two halves of the Disney Afternoon, so a bench turn there would put the marquee's own six shows in the three hours leading into it — four hours of one rotation, and the 15:00 appointment stops meaning anything. Noon gets Disney Toons instead: everything the Afternoon is not. This is the one place Disney departs from the Nick pattern, and the reason is that Disney has a marquee where Nick has a flagship pool.

**Serialized shows stay off the bench.** Gravity Falls, The Owl House and Amphibia carry the chronological-weekday / shuffle-weekend split in the 17:00–19:00 strip, and the shuffle half runs again at 00:00–02:00 as Disney After Dark — same two keys, no third registration. Star Wars (Clone Wars 133, Rebels 69, Bad Batch 47) does the same at 19:00–21:00, with the shuffled vault behind it at 21:00–24:00.

**Four Saturday events.** The short series — Tales of the Jedi (6), Tales of the Empire (6), Tales of the Underworld (6), Maul – Shadow Lord (10) — are too short to strip, so each is an `annual_show()` appointment: one episode a Saturday, six or ten weeks, one per season of the year. Between them they give 28 Saturdays a first-run premiere; the vault covers the other 24. The block uses `DailyOrderedCollection` so each show holds the same position every week and premieres at the same time.

Sunday 19:00–21:00 is **The Wonderful World of Disney** in place of the Star Wars strip, and May 4th takes 08:00–22:00 as a Clone Wars marathon.

No filler: `filler/bumpers/` has cartoon network and fox kids trees and nothing else, and the library has no Disney shorts to stand in.

Built against bare season strings while the `("SEASON", "DAY")` tuple form was broken; that form is now fixed and both work. See [KNOWN_ISSUES.md](../KNOWN_ISSUES.md).

### Nick — built
`scripts/channels/nick.py` · `scripts/library/nickelodeon.py`

Nicktoons daytime, **Nick at Nite** 21:00–02:00. Nick's 8 animated shows can't rotate on their own — the WB trio (Animaniacs 197, Pinky 95, Tiny Toons 98) gives it a real bench, and they sit closer tonally to Ren & Stimpy than to Disney Afternoon. Daria lands here too.

Four daytime pools (Nicktoons Classic, Nicktoons, the WB bench, Nick Learns) ride `monthly_rotation()` across four strips — overnight, morning, midday, afternoon — each starting the cycle a month apart, so all four are showing different pools on any given day and all four move on together at the turn of the month.

Nick at Nite splits at midnight: 21:00–24:00 is pre-1970 (I Love Lucy, Dick Van Dyke, Andy Griffith, Bewitched, I Dream of Jeannie, The Addams Family, Gilligan's Island), 00:00–02:00 is the 70s shift (Mary Tyler Moore, Bob Newhart, Taxi, MASH, Sanford and Son, Good Times, Soap, Mork & Mindy, Smothers Brothers). Sixteen shows, not seventeen — the library's only other pre-1980 comedies are *The Lucy Show* and *The Lucy-Desi Comedy Hour*, which stay with Lucy TV.

The channel does not use the default timeslot preset: Nick at Nite needs 21:00–02:00, which `prime` 20–23 / `night` 23–02 can't express.

Avatar and Korra are the evening strip and the only serialized shows on the channel, so they carry the chronological-weekday / shuffle-weekend split — two content keys per show, because an ErsatzTV key carries its playback order and one key would be pinned to whichever order registered first.

Filler is Schoolhouse Rock — three minutes a piece, and the only interstitial the channel has assets for. There are no Nick bumpers on disk.

### High Noon — built
`scripts/channels/high_noon.py` · `scripts/library/western.py`

Two libraries that do not mix, dayparted so they never argue.

**The spine is five black-and-white network westerns**, 1955–1963, **946 episodes**: Bonanza (431, complete run), Gunsmoke (233, the half-hour Dennis Weaver years), The Rifleman (166, complete), Wanted: Dead or Alive (94, complete), Rawhide (22, season one only). All episodic, all standalone. That is the channel for fifteen hours a day.

The plan's old figure of 1,373 episodes was three things at once. It counted **Cowboy Bebop** (anime, already Toonami's), **Breaking Bad** and **Westworld** — all three carry a Western genre tag and none is a western — and it counted `extras/` folders as episodes. The honest number is 946 for the spine and 234 for the moderns.

| Slot | Mon–Fri | Saturday | Sunday |
|---|---|---|---|
| 00–02 night | Late feature | ← | ← |
| 02–06 overnight | The Long Ride | ← | ← |
| 06–08 early | Wanted: Dead or Alive | Half-Hour West | Half-Hour West |
| 08–10 morning | The Rifleman | Half-Hour West | Dodge City |
| 10–12 midday | Dodge City *(Gunsmoke)* | The Rifleman | Wanted: Dead or Alive |
| 12–14 noon | **High Noon** — the feature | ← | ← |
| 14–17 afternoon | The Ponderosa *(Bonanza)* | Weekend Matinee | Weekend Matinee |
| 17–20 evening | The Trail Drive | Brisco County | The Ponderosa |
| 20–22 prime | **The appointment** | Saturday film night | **Bass Reeves** |
| 22–24 late | Late feature | Saturday film night | Late feature |

Simulated over 365 continuous days: no gaps, no overlaps, no circuit breakers, 17,377 programme plays. Re-run over three years to check the appointments advance.

**Split by running time, not by title.** A two-hour daypart holds four half-hours or two hour-longs, and mixing them strands the slot's tail. Gunsmoke, The Rifleman and Wanted: Dead or Alive are the half-hours; Bonanza and Rawhide are the hour-longs. Each morning strip is one show, so the hour reads as *The Rifleman is on at eight* rather than *westerns are on*.

**Rawhide rides behind Bonanza.** 22 episodes cannot strip — a nightly hour exhausts it in three weeks. It shares the evening wheel instead, where it surfaces every other night and stays a treat. Bonanza carries the afternoon alone; at 431 episodes it is 46% of the spine.

**Six serialized shows, six nights, one season a year.** Justified (Mon), Longmire (Tue), Deadwood (Wed), Dark Winds (Thu), Yellowstone (Fri), Lawmen: Bass Reeves (Sun) — `annual_show()` Broadcast Mode, premieres staggered across the four seasons so the channel always has one or two first-run nights and never six. `modern_western_movie` is the bed under all of them. Saturday has no appointment and runs 20:00–24:00 of film, which is where a 168-minute *Hateful Eight* can actually play.

Six appointments on one channel is the most in the lineup, and it works because each has its own night and its own bed. The alternative was leaving 234 episodes of the 2004+ pool unused, or stripping serialized drama nobody can drop into.

**The day-gating comes from the slot, not from `frequency`.** `PRIME_BLOCK` is a weekday dict, the same shape Mystery Theatre uses. `frequency=["MONDAY"]` alone would air Monday's episode all seven nights. Verified over three simulated years: every appointment aired on its own weekday and nowhere else, and seasons advanced s1→s2→s3 with Yellowstone looping back to s1 after its two on-disk seasons.

**Season lengths are counted off disk**, not read from `library-tv.tsv`, which counts `extras/` folders as episodes — it overstates Justified by 39 and Deadwood by 15. Yellowstone has two of its five seasons on disk and the appointment declares two, rather than opening windows for episodes that would resolve to nothing and stall the block.

**Its own timeslot map, split at midnight.** Prime is 20:00–22:00, not the default's 20:00–23:00: the appointment is two episodes of a 45-minute cable drama and a three-hour slot leaves an hour of bed behind it every night. And the default's `night: (23, 2)` wraps midnight, which is the bug Cartoon Network, Nick and Disney each carry their own map to avoid.

No filler and no bumpers — there are no western assets on disk.

### Boomerang — closed

The original plan was "pre-1990 as a hard rule", which kept it clear of CN when CN's vault sat in the 02:00–06:00 overnight dead zone. **The restructure moved that vault to the centre of the channel** — 06:00–08:00 daily, 12:00–14:00 weekdays, Sunday midday, Saturday morning, and the Saturday Syndication Hour. Pre-1990 stopped being free the day that landed.

Counted against the library: of **24 pre-1990 animated series, 22 are now claimed** — 20 by Cartoon Network, plus DuckTales and Chip 'n' Dale on Disney and Schoolhouse Rock on Nick. What is left is:

| Show | Eps | State |
|---|---:|---|
| Smurfs, The (1981) | 405 | flat, no `tvshow.nfo` — will not index |
| Bullwinkle Show, The (1959) | 0 | empty directory |

As of 2026-08-30 the disk problems are mostly fixed, and they turned out not to be the binding constraint:

| Show | State |
|---|---|
| Smurfs, The (1981) | **Fixed** — 8 season folders, 367 eps, `tvshow.nfo` present. Season 9 still missing |
| Bullwinkle Show, The (1959) | **Gone from `tv/`** under any name; files exist elsewhere, unidentified and unplaced |
| Popeye the Sailor (1933) | Indexes, but foldered by broadcast *year* — `season_number:` against it means the year |
| Superman (1941) | Clean; already on CN's Saturday morning via `superman_fleischer_tv` |

So the pool is **one show**. Smurfs alone is not a channel, and everything else it would have programmed is now Cartoon Network's identity rather than its overflow.

Reviving it would mean re-founding it on a different principle than "pre-1990" — a second window on a shared library, the way Nick at Nite and Good Times share sixteen titles by splitting the clock. That is a sharing-rule design, and with three channels already sharing the animation library it needs the collision report to police it rather than another hand-maintained list. **Until then it is closed, not deferred.**

### Modern movies — next to build
~1,390 films from 1990 on, 67% of the movie library and the largest untapped pool. The framing is a **video store, not a cinema**: Friday-night new releases, weekend matinees, late-night cult. That gives the channel a *week*, which is what distinguishes it from Cabes Classic Cinema (an era) and Other Worlds (a genre).

It is not clean greenfield, and that is the thing to settle first:

- **Cabes Classic Cinema swaps its whole prime to `MODERN_BLOCKBUSTERS` every summer** (`movies.MOVIE_PRIMETIME_FEATURE`) — 90s/00s/10s films plus `blockbuster_action_movie`, three months a year on a classic-cinema channel. That swap only exists because there was nowhere else to put them, and it should hand them back.
- **Other Worlds and Mystery Theatre take genre slices across all eras** — modern sci-fi, cyberpunk, four horror pools, mystery/crime. This is the lineup's first genuinely hard sharing question: unlike the CN restructure, where every collision had a clean owner and eviction was the answer, a modern movie channel and a sci-fi channel both have a real claim on the same film. Split by hours, not by library.
- Disney (Sunday 19:00–21:00) and CN (Sunday Cartoon Theatre) are narrow and fixed — easy to work around.

Key coverage is uneven. Era keys are complete (`90s_movie` … `20s_movie`), but **genre × era exists only for the 80s and 90s**, and `classic_horror_movie` is 1980s-only, so post-1990 horror has no key at all. Expect to add keys before writing blocks — the same order Disney and CN were built in.

Use the `"movies"` timeslot preset (four six-hour slots) or something close. A two-hour daypart map cuts features in half.

### Travelers Table
Gains the nature documentaries: Planet Earth I–III, Blue Planet II, Seven Worlds One Planet, Prehistoric Planet, Cosmos, Life (2009). Plus 236 episodes of Japanese Food Noodles from `youtube/`.

### The Beat
Music videos only — no Daria, no Jersey Shore, and *The Beatles: Get Back* is a documentary, not a music video. 64 artist folders, currently unstructured. Decide the organizing axis before foldering, because the folder tree becomes the tag schema. MTV's own rotation blocks are the obvious model: morning mix, afternoon countdown, late-night alternative.

---

## Programming mechanics

### Available now, no framework change

**Chronological on weekdays, shuffled on weekends.** `_unwrap_nested_structure` resolves any dict without a `title`/`query` key by day label, so this is valid as a block item today:

```python
{"WEEKDAY": {"title": "DuckTales", "order": "Chronological"},
 "default":  {"title": "DuckTales", "order": "Shuffle"}}
```

Simulates new episodes on weekdays and reruns on weekends.

**Season-then-wait.** `annual_show(premiere_year=, premiere_season=, reruns=, loop=True)` — Broadcast Mode. In production on sitcoms, detective, scifi and Disney. `premiere_season` takes a bare season (`"FALL"`) or a season/weekday pair (`("FALL", "THURSDAY")`), which pins the premiere to that day of the week. Absent from the cartoon channel.

**Short series as yearly events.** Anything too short to strip becomes an annual appointment rather than a rounding error: Dragon Ball DAIMA (20), Attack on Titan Junior High (12), Over the Garden Wall (10), Police Squad! (6), FLCL (6), the Star Wars *Tales* shorts (6 each), Macross Plus (4).

**Probabilistic blending.** `Feather(content, ratio)` inside a `SeasonalBlock` substitutes at a probability scaled by season strength. Right tool for rare specials — the 1941 Superman shorts dropping in occasionally, say.

**Seasonal swaps.** `SeasonalBlock(base=..., seasonal={"SUMMER": Swap(X)})`. Four buckets.

### Built this session

**Month labels.** `derive_labels()` now emits a month label (`JANUARY` … `DECEMBER`) alongside the existing weekday, season, daypart, holiday and positional labels. Month variants resolve anywhere the label system reaches:

```python
MIDDAY_BLOCK = {"JULY": SUMMER_BLOCK, "OCTOBER": SPOOKY_BLOCK, "default": REGULAR}
```

`scripts/core/registry.py::MONTHS` · `scripts/core/states.py::derive_labels`

**`monthly_rotation()`.** Builds a month-keyed variant dict that cycles a list, so short shows stay in rotation instead of being ground down. In production on Nick, where four strips share one four-pool bench:

```python
from scripts.logic.factories import monthly_rotation
MIDDAY = monthly_rotation([BLOCK_A, BLOCK_B, BLOCK_C])   # Jan→A, Feb→B, Mar→C, Apr→A…
MIDDAY = monthly_rotation([SUMMER, WINTER], start_month=6)
```

Returns a plain dict the pipeline already understands — no new resolution logic. `scripts/logic/factories.py`

**Title validation.** `scripts/testing/validate_titles.py` walks each channel's config tree and checks that every scheduled title exists in the library and every bare content key exists in `MASTER_SOURCES`.

```bash
python3 -m scripts.testing.validate_titles                  # all channels
python3 -m scripts.testing.validate_titles cartoon_network  # one
python3 -m scripts.testing.validate_titles --quiet          # findings only
```

Matches on token sets, so the library's `Flintstones, The (1960)` form and a scheduled `the flintstones` line up. It is query-aware: a broad title narrowed by `studio:`/`tag:`/`genre:` is not flagged, an `OR` query passes if any branch resolves, and bare `title:` lookups that name an episode or special are reported separately as unverifiable rather than missing. Exits non-zero when it finds something, so it can gate a build.

Reads the manifests in `reference/`, so it runs offline with no ErsatzTV.

### Still needs building

**Collision report.** The framework has no cross-channel awareness. Sharing rules stay a convention until something can simulate N days across all channels and flag a title double-booked in the same hour. `visualize_week.py` and the walker in `validate_titles.py` are the two halves of it — same traversal, plus a time dimension. Deferred through the Cartoon Network restructure, on the grounds that CN's eviction list was written down rather than needing deriving. That list is now cleared, so the next time two channels overlap nothing will be holding the answer — and `common.HALLOWEEN_TEEN_FRIGHTS` is already one live example. See [next-session.md](next-session.md).

---

## Sharing rules

No channel airs a title *while* another channel is airing it. Sharing itself is fine and often the point, because the two channels mean different things by it.

**Nick at Nite vs. Good Times.** Nine shared titles (Bewitched, Bob Newhart, Dick Van Dyke, Gilligan's Island, I Love Lucy, Mary Tyler Moore, Taxi, Andy Griffith, MASH). Good Times keeps all of them and airs them mornings and daytime — just not during 21:00–02:00. I Love Lucy stays on Nick at Nite despite Lucy TV; it earns the exception.

*Done in code when Nick was built.* Good Times used to run a collection literally named `NICK_AT_NITE` in its 23:00–02:00 slot. That is now `LATE_NIGHT_SYNDICATION` — Cheers, Wonder Years, Married… with Children, Newsradio, Drew Carey, Wings, Mad About You, 3rd Rock, The Nanny, Coach — none of them shared. The winter prime variants swapped in `CLASSIC_SITCOMS_60s_70s`, which reaches into 21:00–23:00, so they now take `EIGHTIES_NINETIES_CLASSICS` instead; and the channel fallback moved off the classics for the same reason. Mornings, daytime and the 02:00–06:00 overnight are untouched.

**Disney vs. Cartoon Network — settled.** Everything Cartoon Network was holding for Disney has gone back: `DISNEY_MORNING`, `DISNEY_AFTERNOON`, Gargoyles, and the Star Wars Day marathon that used to run against Disney's own. CN's Halloween schedule no longer reaches for `common.HALLOWEEN_TEEN_FRIGHTS` either — it has `animation.CN_HALLOWEEN`, built from Courage and Infinity Train. Other Worlds was also borrowing CN's Star Wars block at 06:00 and now uses Disney's `star_wars_animation_tv` key.

**Nick vs. Cartoon Network — settled.** The Nicktoons Vault is retired, and Daria, Animaniacs and Pinky and the Brain are Nick's alone. Ed, Edd n Eddy went the other way: it is a Cartoon Cartoon and had been filed under Nicktoons.

**Still crossed:** `common.HALLOWEEN_TEEN_FRIGHTS` is Gravity Falls (Disney), Infinity Train and Courage (both Cartoon Network), and **Nick** is the only channel still using it — so on Halloween Nick airs three shows it does not own. Nick's problem to fix, in Nick's session; it wants a `NICK_HALLOWEEN` the way Disney and CN now have their own.

**Other Worlds vs. Cabes Classic Cinema — settled by eviction.** Both handed
Saturday prime to `movies.SCI_FI_SHOWCASE`, and because each drew a different arm
of the collection they never shared a *key* — nothing flagged it while both ran
sci-fi features 20:00–24:00 every week. Classic Cinema gave it up. Its morning
block also moved to `classic_hollywood_pure_movie`, which is the same 1950–69 era
with science fiction excluded; the unfiltered key was putting Forbidden Planet,
Day the Earth Stood Still and Godzilla opposite Other Worlds' own classic sci-fi
film. Other Worlds gave back Disney's `star_wars_animation_tv` in exchange.

**High Noon vs. Cabes Classic Cinema — settled by eviction.** Classic Cinema ran
`WESTERN_MATINEE` — all 46 western films — across *both* weekend afternoons,
twelve hours a week, and it was the only claim on the pool. High Noon takes the
shelf whole, the same eviction Other Worlds got for science fiction. Classic
Cinema's weekend afternoon is now `movies.WEEKEND_MATINEE`, a `SeasonalBlock`
on its own era with the four `classic_hollywood_<season>_movies` keys feathered
on top — which is where `..._summer_movies` and `..._fall_movies` finally get
used, both having been in the registry and on no channel.

`classic_hollywood_pure_movie` also drops westerns now, not just science
fiction. The 1950–69 slice is The Searchers, Shane, Giant, The Magnificent
Seven, the Leone trilogy and Butch Cassidy — eleven films that are the western
channel's centre, and they were on Classic Cinema's weekday afternoon.
An era split was considered and rejected: 46 films is too few to halve, and the
pre-1980 half is precisely the half High Noon cannot do without.

**Mystery Theatre vs. Cabes Classic Cinema — settled by era split.** Both want
crime film and both run it overnight. `mystery_crime_movie` (365 films) is now
`classic_crime_movie` (pre-1980, 74) for Classic Cinema and `modern_crime_movie`
(1980+, 291) for Mystery Theatre. Neither can draw the other's film. This is the
first era-split on the lineup and it is the pattern to reach for when two
channels have an equally real claim on one genre.

**Mystery Theatre vs. Across the Pond — shared on purpose.** Poirot and Miss
Marple air on both. Decided, not an oversight: both channels have a real claim
and the hours do not overlap. Across the Pond airs them roughly three times as
often, which is fine.

**Adult Swim vs. Corncob TV.** Tim and Eric, The Eric Andre Show, Check It Out! with Dr. Steve Brule. Adult Swim is **first-run** — chronological, appointment-scheduled, late. Corncob is **syndication** — shuffled, daytime, drop in anywhere. Same show, two presentations. This generalizes: it's the cross-channel form of the chronological-weekday / shuffle-weekend pattern.

---

## Known gaps

| | Detail |
|---|---|
| **YouTube unused** | 637 eps — Japanese Food Noodles 236, Best of the Worst 154, Historia Civilis 88, On The Line 80, Timothy Wilmots Woodworking 51, Pedulla Studio 28 |
| **Features with zero uses** | `alternating_seasons()`, `timeslot_commercials`, `global_filter`, `seasonal_blocks` param — `loop_restart_season` is now exercised by Disney's four Saturday events |
| **Switched off globally** | `ENABLE_COMMERCIALS` (110 tagged 90s spots idle), `ENABLE_FILLER` (why bumpers never fire outside the 5 branded blocks) |
| **Assets not wired** | ~940 per-show Toonami bumpers reachable by tag, referenced by nothing; 5 AS outros with no registry key; `fox_kids_*` keys referenced but undefined over an empty folder |
| **Empty commercial decades** | 50s, 60s, 70s, 00s, 10s, 20s — the 00s gap matters most |
| **Broken on disk** | Smurfs (405 eps, unindexable), Bullwinkle (empty dir) |
| **Dead code** | `FOX_KIDS_BLOCK`, `ACTION_ANIMATION`, `SYNDICATED_CARTOONS`, `BRANDING_90S_KIDS` |
| **Largest untapped** | ~1,390 films from 1990 on |
| **Manifests overstate episodes** | `library-tv.tsv` counts `extras/` folders as episodes — Justified reads 117 for 78, Deadwood 51 for 36, Rifleman 167 for 166. Count off disk before sizing an `annual_show()` |
| **Genre tags are not genres** | Breaking Bad, Westworld and Cowboy Bebop all carry a Western tag. `western_tv` returns all three, which is why High Noon names its shows instead |
