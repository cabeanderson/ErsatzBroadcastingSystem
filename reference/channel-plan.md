# Channel Plan

Working plan for the scripted-schedules lineup. Companion to [channel-coverage.md](channel-coverage.md) (what exists and where it goes) and the library references in this directory.

---

## The organizing principle

**A tune-in channel needs episodes that stand alone.**

This is the rule everything else follows from. ErsatzTV earns its keep when you don't know what to watch and you turn something on — which only works if any given episode is enjoyable cold. Serialized shows fail that test: nobody tunes in mid-season-2 of *Six Feet Under*, they select it. Those belong on-demand.

Every channel already in the lineup selects for episodic content without anyone having decided it: sitcoms, westerns, detective-of-the-week, horror anthology, cartoons, sketch, cooking, DIY, 80s action. That is why they work, and it is why ~75% of the 108 unhomed shows are unhomed — they're serialized.

The escape hatch is `annual_show()` Broadcast Mode: one season a year, chronological, weekly, reruns filling the gap. That converts a serialized show into appointment TV, which is a different promise — "this channel has a Thursday show" rather than "turn it on whenever." Good for one or two anchors per channel. Never for a whole channel.

---

## Lineup

### Existing

| # | Channel | Content | Scripted |
|---|---|---|---|
| 104 | Across the Pond | British comedy & panel | yes |
| 116 | Cartoon Network | CN + Toonami + Adult Swim | yes |
| 120 | Lucy TV | I Love Lucy 24/7 | no |
| 142 | Cabes Classic Cinema | classic film | yes |
| 144 | Mystery Theatre | detective / procedural | yes |
| 151 | Other Worlds | sci-fi & fantasy | yes |
| 164 | Japanorama | anime | no |
| 180 | Totally 80s | 80s TV — **stays 80s** | yes |
| 190 | Good Times | sitcoms | yes |
| — | Nick (+ Nick at Nite) | Nicktoons, WB animation, classic TV | yes — **built**, channel number pending |
| — | Disney | Disney Afternoon, ABC mornings, Star Wars animation | yes — **built**, channel number pending |
| 240 | Travelers Table | cooking — **+ nature docs** | no |
| 241 | Makers Corner | DIY & craft | no |
| 242 | Corncob TV | absurd comedy | no |
| 243 | High Noon | westerns | no |
| 244 | Nightmare Theatre | horror, TV + film | no |
| 246 | The Beat | **music videos only** | no |

### To build

| Channel | Pool | Shows | Notes |
|---|---:|---:|---|
| **Boomerang** | 1,193 (1,598 w/ Smurfs fixed) | 16 | Pre-1990 only, keeps it clear of CN |
| **Modern movies** | ~1,390 films | — | 1990-present; the largest untapped thing in the library |

---

## Channel notes

### Cartoon Network
CN originals + Toonami + Adult Swim on one channel, dayparted. Keeping Adult Swim attached is right — each daypart draws its own pool, so nothing competes. Dragon Ball after school is the anchor.

Rough shape: vault 06–08 · CN originals 08–15 · action syndication 15–16 as a ramp · **Toonami 16–20** · Adult Swim 20–02 · acquisitions 02–06.

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

### Boomerang
Pre-1990 as a hard rule — keeps it from competing with CN for Dexter/PPG/Johnny Bravo. Two things gate it: Smurfs (405 eps, flat, no `tvshow.nfo`, won't index) and Bullwinkle (empty directory).

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

**Collision report.** The framework has no cross-channel awareness. Sharing rules stay a convention until something can simulate N days across all channels and flag a title double-booked in the same hour. `visualize_week.py` and the walker in `validate_titles.py` are the two halves of it — same traversal, plus a time dimension. Deferred again in favour of the Cartoon Network restructure, on the grounds that CN's eviction list is already written down rather than needing deriving. That reasoning expires the moment a fourth channel wants the same library. See [next-session.md](next-session.md).

---

## Sharing rules

No channel airs a title *while* another channel is airing it. Sharing itself is fine and often the point, because the two channels mean different things by it.

**Nick at Nite vs. Good Times.** Nine shared titles (Bewitched, Bob Newhart, Dick Van Dyke, Gilligan's Island, I Love Lucy, Mary Tyler Moore, Taxi, Andy Griffith, MASH). Good Times keeps all of them and airs them mornings and daytime — just not during 21:00–02:00. I Love Lucy stays on Nick at Nite despite Lucy TV; it earns the exception.

*Done in code when Nick was built.* Good Times used to run a collection literally named `NICK_AT_NITE` in its 23:00–02:00 slot. That is now `LATE_NIGHT_SYNDICATION` — Cheers, Wonder Years, Married… with Children, Newsradio, Drew Carey, Wings, Mad About You, 3rd Rock, The Nanny, Coach — none of them shared. The winter prime variants swapped in `CLASSIC_SITCOMS_60s_70s`, which reaches into 21:00–23:00, so they now take `EIGHTIES_NINETIES_CLASSICS` instead; and the channel fallback moved off the classics for the same reason. Mornings, daytime and the 02:00–06:00 overnight are untouched.

**Disney vs. Cartoon Network.** Gravity Falls and The Owl House left `animation.CARTOON_NETWORK_CLASSICS` when Disney was built and are Disney's outright — no shared hours, they simply moved. Three things did *not* move and are still double-booked until the CN restructure: `animation.DISNEY_MORNING` in CN's 06:00–08:00 weekday slot, `animation.DISNEY_AFTERNOON` as the base of `CN_AFTERNOON_BLOCK` (14:00–18:00), and CN's Star Wars Day marathon, which now runs against Disney's. Gravity Falls also survives inside `common.HALLOWEEN_TEEN_FRIGHTS`, which CN uses on Halloween. All four come out in the restructure.

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
