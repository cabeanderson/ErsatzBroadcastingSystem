# Known Issues & Tech Debt

A living checklist of findings from the codebase review. Severity: 🔴 high ·
🟠 medium · 🟡 low. Resolved items are kept (struck through) for history.

## Resolved

### 2026-09-02 — the Totally 80s gaps that survived the reset

The 2026-09-02 playout reset cleared the 26 hours of stale-epoch gaps, and gaps
kept appearing. Three separate causes, none of them stale playout, found by
simulating with realistic film durations rather than the mock's uniform 20
minutes — at 20 minutes every film divides the slot exactly and all three are
invisible.

- ~~🔴 **Totally 80s left roughly an hour of dead air every Friday.**
  `FRIDAY_NIGHT_MOVIES_BLOCK` was declared `fill_strategy="gap"`, commented
  "Leave dead air if movie ends early". `gap` maps to `wait_until_time` in
  `engines/dispatcher.py`, which is literally unscheduled time. Prime is
  20:00–23:00 and a blockbuster is under two hours, so the tail was a hole. It
  was the only `fill_strategy="gap"` in the lineup and the only channel with any
  gaps at all across a 30-day, 13-channel sweep.~~ Now `bridge`, which starts
  The Sketch Hour — already the 23:00 slot — early.

- ~~🟠 **`_bridge_to_next_slot` silently dropped every next-slot entry that was
  not a `Block` or `Program`.** It read `day_schedule` and handed the *raw*
  entry to `play_block`, which accepts only those two types and warns
  `play_block received an unsupported type` for anything else. `runner.py`
  resolves each entry through `resolve_content` before dispatching; the bridge
  skipped that step, so a `SeasonalBlock`, a Collection or a bare key made the
  bridge a no-op. Totally 80s' `afternoon` is a `SeasonalBlock`, so The Cult
  Matinee's bridge had never once worked — 62 warnings in a single build log.~~
  The bridge now resolves first: a resolved Block or Program hands off as
  before, and a resolved content key is played to the current slot's boundary,
  so the next slot still begins on time.


**The method that found all three.** Walk the schedule summing each item's
duration and flag wherever the next item starts after the previous one ends.
The existing tools did not do this — `visualize_week` prints structure and
`collision_report` compares channels, but nothing measured continuity.

**Now a tool: `scripts/testing/continuity_check.py`** (2026-09-07). It reads the
live XMLTV export rather than a simulation, which is the important half — a
simulation shows what the current code would build, and the most common cause of
a real gap is a playout built by older code and never reset. Exits non-zero when
it finds one, so it can gate a pipeline; `--future-only` restricts it to the
gaps that can still be fixed.

### 2026-09-01 — what the live server said that the offline tools could not

Found by reading `iptv/xmltv.xml` off the running box rather than by simulating.
**Not one of these is a query defect.** `key_census` scores all 485 keys and
every key belonging to the affected channels passes; `validate_titles` is clean
on all four. The offline tools ask "can the library satisfy this query", and the
answer was yes in every case. The question they cannot ask is "is the right
thing actually on the air".

- ~~🔴 **Nightmare Theatre aired the Good Times sitcom lineup.** For a window on
  2026-08-31 the horror channel carried 171 sitcom episodes — Bob Newhart, Mary
  Tyler Moore, Fresh Prince, M\*A\*S\*H, Sanford and Son. Its 34 titles were a
  **100% subset** of Good Times' 36. A frame pulled from the live HLS stream at
  20:44 showed 30 Rock and matched the guide exactly, so stream and EPG agreed
  with each other and both were wrong.~~ Fixed by a playout refresh; the channel
  now carries 40 programmes over 35 titles, all horror. **The code was never at
  fault** — the local simulation for the same build scheduled correct horror
  (Tales from the Crypt, The Legacy, Hannibal, Twin Peaks, Ash vs Evil Dead).
  The defect lived entirely in ErsatzTV's playout wiring, which is in the
  root-owned SQLite DB and invisible to everything in `scripts/`.

  **The lesson worth keeping:** a channel can be perfectly configured, pass every
  offline check, and still broadcast another channel's content. Title *diversity*
  is not a health signal — 34 distinct titles looked healthy and was the bug.
  Only reading the actual titles catches this.

- ~~🟠 **High Noon was defined but never on air.** Channel 243 existed in
  `/api/channels` (id 20) yet appeared in no feed.~~ Fixed in two steps, which is
  the useful part: enabling the channel put it in `channels.m3u` but **not** in
  `xmltv.xml`, and it took a separate EPG enable plus a build before it
  appeared. It now carries 84 programmes over 16 titles — Gunsmoke, Bonanza,
  The Rifleman, Wanted: Dead or Alive, Rawhide. See the channel-visibility
  ladder in [ERSATZTV_API.md](ERSATZTV_API.md); the three states are distinct and
  a channel can sit in any of them.

- ~~🟡 **Logs grew without bound, and it looked like an infinite loop when it was
  not.** `logs/pond.log` reached 88MB with 983,457 lines and only 2,032 distinct
  ones, repeating `Item: Unnamed Item (17:00-20:00)` / `Fill Strategy: 'yield'.
  Stopping.` at a single timestamp.~~ There was no spin. Counting structure
  rather than repetition: 3,749 day-headers over 36,887 blocks and 258,977
  programmes is **~7 programmes per block and ~10 blocks per day, which is
  normal**. The file held **eleven complete runs** stacked between 18:07 and
  18:16, because `logging.FileHandler` opens in append mode and never rotates.
  The identical lines were consecutive ordinary days sharing a wall-clock second.

  Fixed in two places. `core/logger.py` now uses a `RotatingFileHandler` with
  `maxBytes=0` and an explicit rollover at construction — nothing rotates *during*
  a run, so one build is always one file, but each run starts clean and the last
  `LOG_BACKUP_RUNS` (default 3) are kept as `.1`/`.2`/`.3`. And
  `library/queries.py:196` now summarises the seasonal tag injection: the OR-chain
  was 409 characters a line, 55,148 times, 20.5MB per file — the single largest
  byte category, larger than the programme lines. A/B on the same one-day build
  measured **31,083 → 24,990 bytes, 19% smaller**, with the full query still
  available at DEBUG behind `LOG_FULL_TAG_QUERIES`.

  **Diagnostic note:** repetition alone is not evidence of a loop. Divide by the
  structural counts — days, blocks, programmes — before concluding anything.
  This one cost a wrong call in the first pass of the audit.

### 2026-08-30 — content-key and schedule-shape bugs

Found by the collision report and the library census, both added this session.
Every one of these was silent: the schedule built, the simulation stayed green,
and the channel aired something. What it aired was wrong.

- ~~🟠 **Cartoon Network's guide never showed an episode title.** All 21
  blocks in `library/animation.py` set `use_epg_group=True` — the only channel
  in the repo with no ungrouped airtime (disney 8/15, nickelodeon 3/10, every
  other library 0). `engines/blocks.py:99` wraps a whole block in an EPG group
  on that flag, and ErsatzTV collapses the group into one guide entry named
  after the block, so the grid read "The Vault" / "Cartoon Cartoons" /
  "Toonami" / "Adult Swim" from 06:00 to 06:00 and could never surface what was
  actually on. Nothing was wrong with the scheduling — the items played fine,
  they were just invisible.~~ Fixed: all 21 flags are now `False`. Grouping is
  kept **for marathons only**, which get it independently from
  `logic/calendar/assembly.py:122` when the marathon Block is built — so
  "DBZ Marathon" still reads as one entry, which is the case grouping is for.
  Verified against the simulator: a normal Friday went 10 groups → 0, and
  2026-07-04 / 2026-09-05 kept exactly their one marathon group each. Item
  counts drop by 2 per removed group because the mock records the start/stop
  as pseudo-items; no content was lost.

  Extended the same day to the other two channels, on the operator's call:
  disney (8 blocks) and nickelodeon (3) are now `False` as well, so **no static
  block anywhere in the repo is EPG-grouped**. Weekly groups: Disney 29 → 0,
  Nick 15 → 0, Cartoon Network 0; real item counts unchanged at 434 / 490 /
  676. The Nick removal also un-hides the nine Nick at Nite classics shared
  with Good Times, which were grouped 14x a week behind two block names.

  **The reason grouping is not worth keeping as it stands:** `playout.py:299`
  always passes `custom_title`, and on a live build that renders as one
  name-only guide entry — no artwork, no episode title, no description.
  Whether a group *without* `custom_title` would keep per-item metadata is
  open question #5 in [ERSATZTV_API.md](ERSATZTV_API.md); it needs one real
  build, and the mock explicitly does not model grouping effects. Until that is
  answered, grouping stays only where the items really are noise — marathons,
  via `logic/calendar/assembly.py:122`.

- ~~🟡 **Two Programs were named `<built-in method title of str object at
  0x...>`.** `animation._with_bumpers` did `getattr(item, "title", str(item))`,
  but `str` *has* a `.title` method, so a bare content key returned the bound
  method instead of ever reaching the fallback. It hit both string call sites
  (`animation.py:466` and `:573`, the Attack on Titan rerun bed in the two
  Midnight Run blocks), and the memory address meant the name was not even
  stable between runs.~~ Fixed with an explicit `isinstance(item, ContentItem)`
  check. Log-only while the blocks were grouped; found during the EPG fix
  above, which is exactly what would have exposed it.

- ~~🔴 **Noir November had never once aired.** Mystery Theatre's signature
  seasonal takeover lived on `PRIME_BLOCK["default"]`, behind five explicitly
  named weekdays. `PRIME_BLOCK` is only wired into `SCHEDULES["WEEKDAY"]`, and
  Saturday/Sunday have their own prime, so nothing could ever reach the default
  arm.~~ Fixed: `"NOVEMBER"` is now the first key in the dict and dict resolution
  takes the first matching label. Scoped to November rather than FALL on purpose
  — a season-level swap would delete the Mon–Fri lineup for three months.
  Verified with Dark Winds, the one title unique to the block: 0 airings in
  October, 30 in November, 0 in December. `test_03_resolution_pipeline` now
  asserts the takeover instead of asserting that *something* resolved.

- ~~🔴 **Unreachable `default` arms across two channels.** When a block's guards
  are `WEEKEND` + `WEEKDAY_A` + `WEEKDAY_B`, or all seven day names, they cover
  the week and any `default` behind them is dead.~~ Five of Other Worlds' eight
  blocks had one. `EARLY_BLOCK`'s was the only weekday fantasy on the channel, so
  it never aired at all. Fixed: no block on either channel has an unreachable
  arm now.

- ~~🔴 **`supernatural_tv` queried a genre that does not exist.** It was
  `genre:"(supernatural OR tag:paranormal)"`. There is no Supernatural genre in
  the library and `tag:paranormal` is on three shows, so a near-empty key held a
  third of a daily block.~~ Fixed: `tag:supernatural OR tag:paranormal`, which is
  12 shows. `tag:supernatural` is the tag that actually exists.

- ~~🔴 **`true_crime_tv` resolved to one show with six episodes.**
  `genre:documentary AND genre:crime`. It was in `DETECTIVE_LATE_NIGHT`, which
  covers overnight, early *and* night — six episodes carrying 47 hours a
  month.~~ Fixed: true crime dropped from Mystery Theatre; the slot went to
  Alfred Hitchcock Presents (268 episodes, previously on no channel).

- ~~🟠 **A whole-season `Swap` deleted Other Worlds' weekday prime for three
  months.** `"SPRING": Swap(MODERN_SCIFI_BLOCK)` sat at the top level of the
  seasonal dict rather than inside a day map, so it replaced all five days.
  X-Files, Babylon 5, BSG and Sarah Connor each dropped to about 45 minutes a
  week.~~ Fixed: spring is per-day, matching how summer was already written.
  **General trap:** at the top level of a `SeasonalBlock`, `Swap` replaces every
  day. Nest it in a day map unless a total takeover is the intent.

- ~~🟠 **`space_opera_tv` was the widest pool in the registry.**
  `genre:"science fiction" AND NOT tag:sitcom` — the only sci-fi key without a
  `NOT genre:fantasy` clause, so it returned everything `scifi_tv` did plus
  Stargate SG-1, Quantum Leap, Xena and Sabrina the Teenage Witch. It was
  scheduled 52 hours a week as though it were a themed block.~~ Renamed
  `scifi_all_tv` and used deliberately for one broad slot. **Do not simply add
  `NO_FANTASY` to it:** this library tags Stargate SG-1 and Quantum Leap as
  Fantasy, and that clause is exactly why the named title collections exist.

- ~~🟠 **`MYSTERY_MOVIE_WHEEL` contained no movies.** Named for the NBC wheel;
  held Columbo, Poirot, Miss Marple and Murder She Wrote, all television. It was
  Saturday evening *and* prime.~~ Fixed: the TV rotation is `WHODUNIT_WHEEL` and
  the movie wheel shows film. Mystery Theatre went from 2% film to 18%, against
  a library of 365 crime and mystery features.

- ~~🟠 **Title queries that matched the wrong thing, or nothing.**~~
  `show_by_title("Magnum P.I.")` against a folder named `Magnum, P.I.`;
  `show_title:"Star Trek"` is a phrase match and returned every Trek series,
  making Other Worlds' vault a second Trek playlist; a bare `"House"` also
  returns House of the Dragon and House Of Cosbys. Fixed by correcting the comma
  and year-bounding the other two. **Verify title queries against
  `reference/library-tv.tsv` — the simulator cannot catch these, because it
  generates a key from whatever title it is given.**

- ~~🟠 **`collision_report.base_key()` collapsed every appointment show to
  `_`.**~~ `factories.annual_show` mints `__auto_<title>_s<n>`, which matched the
  tag-injection suffix pattern the normalizer strips. Lost, Alias and Fringe all
  became the same key, which would have invented collisions between them. Fixed
  with a prefix guard.

- ~~🟡 **`golden_scifi_tv` duplicates `syndicated_scifi_tv`** byte for byte.~~
  Still both present; `golden_scifi_tv` is on no channel. Left in place rather
  than deleted, but it is a trap.

- ~~🔴 **`id()`-seeded RNG broke determinism.** Collections/list picks seeded RNG
  with memory addresses, so output changed every process run.~~ Fixed: seeds now
  use `core/identity.stable_hash()`; `OrderedCollection` is date-anchored;
  `RandomCollection` resets per day. Verified reproducible across processes.
- ~~🟠 **No `requirements.txt` / undocumented `etv_client`.**~~ Fixed: added
  `requirements.txt` (stdlib-only) and README notes (container vs. local).
- ~~🟠 **`install_mocks()` ordering footgun.**~~ Fixed: auto-installed on
  `scripts.testing` import; production-safe (real client always wins).
- ~~🟠 **Stray non-Python prototype in `channels/`** (`main.go`, `schema.sql`,
  `simple_backend.py`).~~ Removed by author.
- ~~🟡 Stale module-path header comments / `schedule.py` reference.~~ Fixed in
  `library/queries.py`, `logic/resolution/resolver.py`, `logic/resolution/pipeline.py`.
- ~~🟠 **Broken test: `test_smoke_simple_channel_run`.**~~ Fixed: it now unpacks
  the 3-tuple from `assemble_day_schedule(...)`. `test_scenarios` is 9/9.
- ~~🟠 **Module-level caches leaked across channel builds**
  (`BUMPER_FAILURE_CACHE`, `_INJECTION_CACHE`).~~ Fixed: `reset_bumper_failure_cache()`
  / `reset_injection_cache()` are called at the start of `ScheduleRunner.run()`,
  scoping both caches to a single build. Verified entries don't survive a run.

- ~~🔴 **Run-aborting crash when a content-less Program hit a Block fallback.**~~
  An off-season Appointment Program (`content=None`, no active schedule) fell
  through to static resolution, which substituted `config.fallback_content`. When
  that fallback is a `Block`/Collection (e.g. Cartoon Network's
  `fallback_content=CLASSIC_CARTOONS`), the Block was handed downstream and
  `get_query_data` did `Block in dict` → `TypeError: unhashable type`, aborting the
  entire `run()` — i.e. "the channel just stops having content." Fixed: such
  programs skip cleanly (`engines/blocks.py`), and `get_query_data` is
  type-guarded (`logic/resolution/resolver.py`). Verified: 14 continuous days of
  Cartoon Network now schedule content with no crash.

- ~~🔴 **Marathons overran their window by days.** A marathon whose content is
  unbounded (a whole show, no episode range — e.g. `simpsons_random_marathon`)
  resolved to `play_count = None`, which `_convert_marathon_to_block` replaced
  with `DEFAULT_MARATHON_LIMIT = 1000` "to ensure continuous play". That became
  a single `add_count(count=1000)`, and ErsatzTV's `AddCountInternal` applies no
  time bound at all — it commits every item in one call. `strict_window` could
  not help: it is checked *between* block items, and the marathon block held
  exactly one. A 6-hour Simpsons slot became ~14 days of playout.~~ Fixed:
  `Program.fill_window` marks unbounded marathon content, and the engine asks
  for exactly the remaining window via `add_duration` (`playout.play_for_duration`).
  Verified: the 2026-04-30 Simpsons marathon now runs 16 items inside 16:00–22:00,
  down from 1000 items spanning 13d 21h. Regression test:
  `TestMarathonWindow.test_unbounded_marathon_stays_in_window`.
- ~~🟠 **`pad_until` / `wait_until` silently did nothing across month
  boundaries.**~~ The HH:MM endpoints carry the date in a separate `tomorrow`
  flag, and ErsatzTV schedules *nothing* (no error) when the target time of day
  has passed and `tomorrow` is false. All three call sites computed it as
  `target.day > now.day`, which is False on Aug 31 → Sep 1 (`1 > 31`). That is
  the "pad under-filled" failure the safety net in `fill_to_boundary` was
  papering over. Fixed: `fill_until_time` / `wait_until_time` take a `datetime`
  and call `pad_until_exact` / `wait_until_exact`, which also avoid ErsatzTV's
  own acknowledged DST bug in the time-of-day variants.
- ~~🟠 **The simulator could not reproduce API-contract bugs.** `MockAPI.add_count`
  ignored `count`, there was no per-key enumerator, and `pad_until`/`wait_until`
  always jumped to their target.~~ Fixed: the mock now follows
  `SchedulingEngine.cs`, the build window defaults to 2 days (matching
  `PlayoutDaysToBuild`), and API round trips are counted. Pinned by
  `TestApiContract` (8 tests). See [ERSATZTV_API.md](ERSATZTV_API.md).

- ~~🟠 **Marathon random start never fired.** `simpsons_random_marathon` declares
  `start_mode="random"` with `start_season=[3, 9]`, but the guard in
  `_convert_marathon_to_block` read `play_count and play_count > 1`.
  `play_count` is `None` for unbounded content — which is exactly the content
  that declares a random start — so the branch was dead and every Simpsons
  marathon opened on the same episode. It was also the only marathon in the
  library using `start_mode="random"`.~~ Fixed: the guard is now
  `play_count != 1` (None and >1 both have room to start somewhere), and season
  selection uses `boss.pick()` instead of `random.randint()`, which reseeded per
  process and would have broken same-date reproducibility once the branch went
  live. Verified: S9/S5/S9 on three trigger dates, identical across processes.
- ~~🟠 **`skip_to_item` was orphaned by injections.** The skip was issued inside
  `_resolve_and_prepare_program_content`, before `apply_injections` could
  rewrite the content key. Seasonal injection turned
  `auto_gen_cowboy_bebop_eps_23_26_d1e246` into `..._auto_spring`, so the skip
  positioned an enumerator that was never played from and the marathon silently
  started at episode 1. The Appointment TV branch had the same shape, skipping
  the registry key while playing `resolver.resolve(key)`.~~ Fixed: both branches
  now *report* a start point and `play_program` issues the skip once the final
  key is known. Verified: orphaned skips across two years of Cartoon Network
  went 30 → 0, with all 3001 correct skips preserved.
- ~~🟠 **Redundant `get_context` on the hottest path.** Every scheduling endpoint
  already returns a `PlayoutContext`, but `playout.play_item` discarded it and
  issued a separate `get_context`, doubling round trips against ErsatzTV's 30s
  build timeout.~~ Fixed: `play_item` uses the returned context and only falls
  back to `get_context` on failure. A Cartoon Network day went 295 → 152 calls.

- ~~🔴 **`premiere_season=("SEASON", "DAY")` scheduled nothing, silently.**
  `annual_show()` passes `(year, premiere_season)` to `states.resolve_season_date`,
  which only understood `(int, str)`. Given a tuple season it returned `None`,
  `_build_season_windows` skipped every season, and `_resolve_appointment_schedule`
  bailed on the empty window list — so the Program played its `reruns` forever and
  never premiered. No warning: an appointment that never fires is indistinguishable
  from one between seasons. `loop_restart_season` had the same problem from the
  other end — it defaults to `premiere_season`, and a tuple there failed the
  `isinstance(str)` check and silently selected the immediate-loop branch instead
  of the annual restart. Six appointments were dead: The Office, Parks and Rec,
  Community and 30 Rock (`library/sitcoms.py`), True Detective and Fargo
  (`library/detective.py`).~~ Fixed at the root: `resolve_season_date` now accepts
  a `(season, weekday)` pair and moves the resolved date forward to the first
  matching weekday, so a `("FALL", "THURSDAY")` premiere lands on a Thursday
  (2026-09-17) rather than on whatever day the season's peak starts (2026-09-15);
  `states.season_label()` normalises the season half in `annual_show` and
  `_apply_schedule_looping`. All six now premiere and advance weekly. Covered by
  `TestSeasonSpecResolution` (9 tests) in `test_scenarios.py`.

- ~~🔴 **`fallback_content` was silently dead on five channels.** It reaches
  `circuit_breaker`, which hands it straight to `play_item` — and `play_item`
  stringifies anything that is not already a key. A Block fallback arrived at
  ErsatzTV as the literal text `Block(name='The Disney Afternoon', items=<...
  object at 0x7f...>)`: matching nothing, carrying a memory address so it was
  not even stable between runs, and still logging "✅ Fallback succeeded". The
  two call sites disagreed — `engines/dispatcher.py` resolved first,
  `engines/blocks.py:141` passed it raw — so the same config behaved differently
  depending on which one fired.~~ Fixed: both now go through
  `dispatcher.resolve_fallback_key()`, which resolves, returns a key or None,
  and warns when a fallback resolves to something unusable. That makes
  Collections work at both sites (british, classic_movies, sitcoms were already
  passing Collections); Blocks remain invalid per `pipeline.py:109`, so Disney
  and Nick moved to new `disney_vault_tv` / `nicktoons_vault_tv` keys —
  genre-qualified OR queries over each channel's own shows, following the
  `toonami_vault_tv` pattern. Nick's deliberately excludes the Nick at Nite
  titles, which are shared with Good Times. Covered by `TestFallbackResolution`,
  including a repo-wide test that every channel's fallback resolves to a key.

- ~~🟠 **The simulator sized content by substring, inventing a failure.**
  `MockAPI._guess_duration` matched `'movie' in key`, so the *show* Home Movies
  — key `auto_gen_home_movies_<hash>` — was treated as a two-hour film. That one
  item ate the rest of its Adult Swim block and all of the hour after it, which
  made Cartoon Network appear to drop its Friday 23:00 slot every single week
  and never air Attack on Titan Junior High. `validate_schedule` reported no
  gaps throughout, so it read as a real scheduling bug rather than an artifact.
  `intro`/`outro` were also absent from the shorts list while `bumper`/`filler`
  were present, so branding stings were sized at 20 minutes — 40 minutes of
  ident either side of a block boundary, enough to squeeze a real item out of a
  one-hour slot.~~ Fixed: a registered `type:movie` query is now authoritative,
  name matching is on whole words rather than substrings, and `intro`/`outro`/
  `ident`/`promo` are shorts. `validate_schedule` uses the duration the build
  actually recorded instead of re-deriving it. Three library titles tripped the
  old wire; only Home Movies was scheduled anywhere. Covered by
  `TestSimulatorDurationGuess`.

### 2026-09-02 (later) — the music video collection, reorganised

- ~~🔴 **`eighties_music_videos` matched nothing, and it was six hours a day of
  Totally 80s.** Found in the live `xmltv.xml` *after* the playout reset, which
  is what made it conclusive: the channel carried a 2026-09-02 epoch, was running
  the current design, and still showed **12.1 hours of gaps over a three-day
  guide** — 6 hours from 00:00 on Thu 03 Sep and again on Fri 04 Sep, exactly the
  `night` and `overnight` slots, both of which held this key. The query was
  `type:"music_video" AND year:[1980 TO 1989]` against a library where **no music
  video had any year metadata at all** — all 751 airings in the guide carried no
  `<date>`.~~ Fixed by reorganising the collection; see below.

  **Why nothing caught it.** `key_census` reads the two TSV manifests, which hold
  shows and films only — its own docstring says `music_video` keys "are not in the
  manifests at all". The census passed at 560 keys with the channel's largest key
  dead. Simulation cannot see it either: the mock returns content for any key.

**What the reorganisation did.** ErsatzTV derives a music video's *artist* from
the top-level folder, not the `.nfo` — proven on the server, where
`90's/Foo Fighters/… - Learn to Fly.avi` has `<artist>Foo Fighters</artist>` in
its sidecar and still aired as `<title>90's</title>`. 244 of 303 files sat under
genre buckets, so the guide listed "hip_hop" as an artist 242 times. The layout
is now `<Artist>/<Artist> - <Title>.<ext>` with a Kodi `.nfo` beside each file
carrying title, artist, genre and year; genre moved off the directory tree and
into the sidecar. 176 artist folders, 303 videos, 303 sidecars, no empty
directories. The move manifest and the scripts are in `_tools/` next to the
collection, so the whole thing is reversible.

**Years came from the filenames plus curation, not from the files.** ffprobe
found zero artist and zero date tags across the collection — the pre-existing
`music_meta.sh` read `format_tags=date`, which is why every `<year>` it wrote
came out empty. MusicBrainz was tried and rejected: it dates "Material Girl" to
1993 on a reissue, and for a channel whose whole premise is the decade a wrong
year is worse than none. 298 of 303 are dated; the remaining five (MF DOOM,
three Bouncing Souls tracks) are **left blank rather than guessed**.

**The pool is smaller than the schedule assumed, and that is the real finding.**
The collection skews hard to the 90s and 2000s — 111 videos from the 1990s, 125
from the 2000s, and **31 from the 1980s**. Opening the window to the late 1970s
brings it to 35 videos and 152 measured minutes. So `eighties_music_videos` is
now `year:[1975 TO 1989]`, and Totally 80s' video block is **two hours
(04:00-06:00), not six** — the four hours it gives back go to `After Hours`,
action and drama reruns, which is what an 80s independent actually ran overnight.
Organising the collection made the key *work*; it could never have made it *fill*.

  > **CORRECTION 2026-09-07.** The claim that organising the collection made the
  > key work was never verified on the server, and it is false. The key still
  > selects nothing and Totally 80s airs no music videos at all. Reopened at the
  > top of Open. The pool measurements in this entry are all confirmed correct —
  > 302 videos, 298 dated, 35 in window — which is what makes the query the only
  > remaining suspect.

- ~~🟠 **`enable_filler=True` with `filler_content=None` is an inert flag.**~~
  Totally 80s was pointed at `eighties_music_videos` for filler. **The flag is no
  longer inert, but the content it names still resolves to nothing** (see the
  2026-09-07 entry), so the practical effect is unchanged until the key is fixed.
  **Worth auditing the other channels for the same pairing.**

## Open

### 2026-09-08 — the guards moved to where the mistake is made

Nine items closed in one pass. **Three are the same bug wearing different
clothes: a configuration that resolves correctly and then plays nothing.**
`Block(items="key")`, a `Fallback` holding a Collection, a `Block` handed to
`fallback_content` — each one type-checks, names a real content key, survives
every offline checker, and produces an empty slot that the circuit breaker
quietly papers over.

Two more are the same *kind* of failure from further away: a logger that made
a 365-day scan report clean by capturing one day, and an unescaped title that
dropped a show's bumper without a miss being recorded anywhere. The remaining
four are hygiene — an import that wrote to disk, two dead parameters, a
duplicated helper and a six-branch ternary.

The pattern in the fixes is that **the guard belongs where the mistake is
made, not where it finally hurts.** All three now raise at construction, in
the channel file, with the correction named in the message. That is a
different thing from validating at build time: a build-time warning still
needs someone to read a log, and this repo's whole history is of failures that
produced no log to read.

Two second-order results worth keeping:

- **A repo-wide invariant beats a fix.** Rather than correct the one bad
  block, `test_scenarios` now walks every `Block` in `channels/` and
  `library/` and asserts the engine could iterate it. The Japanorama bug was
  found by building Japanorama; the test finds the next one on a channel
  nobody is looking at.

- **Two of the nine were misdiagnosed in this file**, and both misdiagnoses
  were the same shape as the bugs — a plausible claim nobody re-checked
  against the code. `circuit_breaker` had already been fixed at both call
  sites, and the `inject_tag` half of the escaping item would have broken every
  seasonal injection if "fixed" as written. **Re-read the code before
  believing this file**, including this entry.

Measured after: 48 unit tests green, and a 7-day simulation across all 16
built channels — 112 channel-days — with zero errors and zero warnings. That
sweep is also the first one worth trusting, because the logger fix in this
batch is what makes a multi-day capture real rather than day one repeated.

### 2026-09-08 (later) — the appointment scheduler, and the loose-script hack

Four more closed. Two were real scheduling defects that every channel in the
lineup was quietly working around by hand:

- **`frequency` paced an appointment without gating it**, so a show declared
  `["FRIDAY"]` in a seven-night block aired the same episode all seven nights.
  Six Toonami strips and a Friday-only block variant existed to route around
  this. It now gates.

- **A Contiguous-Mode strip took `"FALL"` as its loop restart** from a
  `premiere_season` the caller never set, and went dark from June to September.

**The method mattered more than either fix.** The frequency gate looked right,
passed all 48 tests, and was wrong: it tested the date *after* looping had
rewritten it into the season window, which dropped Rurouni Kenshin from
Toonami's Thursday. What caught it was snapshotting 14 days of all 16 channels
before and after and diffing item by item — two changed channel-days out of
224, both a show vanishing from a day it declares. **For a change inside a
resolver, diff the schedule.** The unit tests only cover what you already
thought of; the diff covers what you did not. After the correction the same
diff reads 0 of 224, which is the proof that the entry's claim — every
appointment was saved by its day-gated block — was true.

The other two were hygiene with a sting: the eleven `sys.path.insert` lines
are gone, and the shipped example turned out to be broken in *both* directions
rather than merely teaching a bad habit. See that entry for why a module
inside a package cannot fix its own package's import order.

### 2026-09-07 — the music video key never resolved, and the "fixed" note was wrong

- [x] ~~🔴 **`eighties_music_videos` still matches nothing on the server, and the
  entry in Resolved claiming it "finally resolves" was never verified against a
  live guide.**~~ **Fixed 2026-09-07.** The key is now
  `type:"music_video" AND release_date:[1975-01-01 TO 1989-12-31]`.

  **The cause was the field name, not the library.** `year:` does not answer on
  this server for any type. This key was **the only one of 645** using it; every
  other era filter in `library/filters.py` — more than forty, all working — was
  already on `release_date:`. The music video library was reorganised, rescanned
  and reset twice to fix a query that was never about music videos at all.

  The field vocabulary, settled: `release_date:` **yes**, `genre:` **yes**,
  `artist:` **yes**, `tag`/`tag_full` **yes**, `year:` **no**. A sidecar
  overrides all of `Tags`, `Genres` and `Artists` — `GetMusicVideoMetadata`
  clearing them describes only the no-NFO fallback path, not a ceiling. **Every
  file already carries a decade tag** (`00s` 125, `90s` 111, `80s` 31, `10s` 18,
  `70s` 6, `60s` 6, `20s` 2), exactly consistent with `<year>`, so The Beat can
  be scripted by decade. Recorded in filler-taxonomy.md §1c.

  **Two traps closed with it.** `movie_source(year=…)` and `show_source(year=…)`
  both appended the same dead `year:` clause and had never once been called;
  they now build a `release_date:` range, so the next era key written through
  them works instead of silently selecting nothing. And the standing lesson:
  **a `<date>` in the guide proves metadata carries a value, never that a field
  can be queried.** Validating the 2026-09-02 reorganisation by reading `<date>`
  out of XMLTV confirmed the wrong store, which is the whole reason this
  survived as long as it did.

  **Verified on air 2026-09-07**, after the deploy and a reset. Totally 80s now
  carries **149 music video airings over 27 distinct videos**, every one of them
  inside the window — years aired run 1976–1988 with **zero out-of-window**, so
  the `release_date:` bound is precise as well as working. The Video Jukebox
  slot reads Boston (1976), The Rolling Stones (1981), Michael Jackson (1979),
  AC-DC (1980), Cyndi Lauper (1986) where it read Knight Rider and Magnum P.I.
  the day before. `key_airing_check` went **1 DEAD → 0**, which is the first
  time this key has ever been confirmed by anything other than an assumption.

  27 of the 35 surface in a 12-day guide, which is ordinary rotation depth and
  not a shortfall. The block opened no gaps: the channel's only remaining dead
  air is 2 minutes at 13:57 on 11 Sep, in the middle of the day and unrelated.

  Regression-tested by `key_airing_check`, which keeps The Beat as the declared
  witness for this key. *Original entry below.* Totally 80s airs **zero** music videos. Measured 2026-09-07 on a
  freshly reset playout: the channel's 185 programmes span 51 distinct titles and
  **not one** of them appears in the 302-video music library, which The Beat airs
  from without trouble on the same server.

  **The content is there and it is dated.** The Beat carries 302 distinct videos,
  **298 of them dated**, and **exactly 35 fall in 1975–1989** — the number the
  docstring predicts, aired 166 times in a four-day guide. So the reorganisation
  did everything it claimed: the sidecars exist, the years are real, ErsatzTV
  reads them, and the pool is the size it was measured to be. What was never
  checked is the one thing that matters: whether
  `type:"music_video" AND year:[1975 TO 1989]` selects any of it. It does not.

  **04:00–06:00 is not dark, which is why `continuity_check` is green.** The slot
  is covered by `fallback_content`, so the channel airs Knight Rider, Magnum P.I.
  and Remington Steele in The Video Jukebox hour. A working fallback is exactly
  what makes this invisible: the guide is continuous, the channel looks healthy,
  and the block behind it has never played. **A gap is a loud failure; a fallback
  is a silent one.** This is the same lesson as the Nightmare Theatre sitcom
  incident from a different direction.

  **Root cause, settled 2026-09-07 by build.** `type:"music_video"` alone
  returns videos. Adding `year:[1975 TO 1989]` returns nothing. **ErsatzTV does
  not populate the Lucene `year` field for music videos**, so any range clause
  on it empties the result regardless of what the sidecars say. The `<year>` in
  the NFO reaches ErsatzTV's *metadata* — the guide prints it as `<date>` on
  1,428 of The Beat's airings — but never reaches the *search index*. Metadata
  and index are different stores, and only one of them answers a query.

  This is worth stating as a rule, because it generalises past music videos:
  **a field visible in the guide is not evidence that the field is queryable.**
  The reorganisation was validated by reading `<date>` out of XMLTV, which
  confirmed the wrong store.

  There is **no read API to ask with** — `/api/search` and `/graphql` both serve
  the SPA shell (re-probed 2026-09-07, including a POST, which 400s identically
  for an invented path), and `api.add_search` schedules items without reporting a
  count. A build was the only instrument available, and it was the one that
  should have been used in the first place.

  **Fixed by changing the field, not the data.** `release_date:` was there the
  whole time and is what the rest of the repo uses; it selects exactly the
  curated 35. `tag_full:"80s"` also works and selects 31 — the tag route the
  original entry proposed was viable all along. `release_date` is kept because
  it matches the 1975–1989 intent, which no single decade tag can express.

  **Genre is not the escape hatch** — the 35 in-window videos are Oldies 19, no
  genre 10, Rock 5, Hip-Hop 1, and `Oldies` is only 19-of-27 in window.

  > **Correction.** This entry first claimed there was no decade facet on these
  > files, so the `<tag>80s</tag>` route was dead. That was wrong: every file
  > carries a decade tag and `tag_full:"80s"` works. The claim came from reading
  > `<category>` in the guide, which carries genre and never tags — the same
  > class of mistake as validating `<year>` by reading `<date>`. **Absence from
  > XMLTV is not absence from the index.** Read the sidecars on disk instead.

  **Why nothing caught it — and the checker that now does.** `key_census` reads
  the two TSV manifests, which hold shows and films only. The simulator's mock
  returns content for any key. `validate_schedule` sees a structurally fine
  block. And `continuity_check` passes because the fallback fills the hole. Five
  checkers, all green, on a block that has never played.

  **`scripts/testing/key_airing_check.py`** (2026-09-07) closes it. It reads the
  live guide and asks, of every key a channel schedules, whether anything
  attributable to it aired. The design problem is that absence is not death — a
  guide covers days and a deep rotation will not surface in it — so a key is
  called DEAD only on positive evidence: either the manifests confirm the library
  holds nothing for it, or a declared *witness* channel airs its pool while the
  scheduling channel airs none of it. The music video key is the witness case:
  The Beat airs 176 titles from the pool and Totally 80s airs zero.

  On the current lineup it reports **1 DEAD, 3 UNWITNESSED, 33 ABSENT, 172 OK,
  124 POOL** over 333 scheduled keys. The three UNWITNESSED are the UK and
  general commercial spots — no tool in the repository verifies those either,
  and `--list-unwitnessed` names them.

### 2026-09-07 — measured with `continuity_check` against the live guide

> Both findings in this section are **closed**. The stale-playout pair was reset
> and the Japanorama gaps were a rebuild away; the lineup now runs with two
> minutes of dead air in total, all of it whole-item placement residue.

- [x] ~~🟠 **Totally 80s and Be Kind Rewind are on pre-rescan playouts and are
  broadcasting 570 minutes of future dead air between them.**~~ **Resolved by
  reset, verified 2026-09-07.** Both channels are continuous; Be Kind Rewind has
  no gaps at all and Totally 80s has two minutes of whole-item placement residue.
  Lineup-wide future dead air went **570 minutes → 2**. Note that the reset alone
  would not have fixed Totally 80s' Jukebox slot — it closed the *gap* by letting
  the fallback fill it, and the block itself needed the `release_date:` fix
  before any music video played. Two defects wearing one symptom. Both were built
  *before* the music-video rescan landed, so `eighties_music_videos` still
  resolves to nothing inside their baked playouts even though the index is now
  correct. Totally 80s has **4 future gaps totalling 420 minutes**, every one of
  them 04:00–06:00 — precisely The Video Jukebox slot. Be Kind Rewind has **one,
  119 minutes, Tue 08 Sep 04:07–06:05**, in the same hours.

  **Not a config defect, and not fixable by editing the channel.** This is the
  deployment rule biting again in its narrower form: a rebuild extends a playout
  forward, but already-built items keep the resolution they were built with. The
  fix is a **reset** of those two channels, and only those two — every other
  channel on the lineup is continuous.

  Reproduce with `python3 -m scripts.testing.continuity_check --future-only`.

- [x] ~~🟡 **Japanorama drops 4–16 minutes before 19:00 most nights.** Four future
  gaps, each ending exactly at 19:00: Mon 18:56, Tue 18:43, Wed 18:53, Thu 18:54.~~
  **Resolved, verified 2026-09-07.** Japanorama is now **completely continuous —
  no gaps at all, past or future** — across the whole guide. It was read as a
  live code defect because the playout was built that morning by current code;
  it was not, and a rebuild closed it. The diagnosis to keep is the one that was
  wrong: *"built by current code" is not the same as "built by the code on disk
  now"*, and on a day with several deploys those drift apart within hours.

- [x] ~~🟡 **Totally 80s leaves a 2-minute tail before 14:00 on 11 Sep.**~~ **Not
  a defect — it is the filler working.** The 12:06 film ends at 13:53, filler
  places a 4-minute music video at 13:53–13:57, and the ~3 minutes left cannot
  hold another whole 3–5 minute item, so the slot waits for 14:00.
  `pad_until_exact` places whole items only, which is documented and correct.

  This is the visible edge of a fix, not a fault. Totally 80s carries **149 music
  videos: 120 in the 04:00–06:00 Jukebox block and 29 placed as tail filler
  elsewhere** — so `filler_content="eighties_music_videos"` is genuinely doing
  its job for the first time. Channel dead air went from **420 minutes to 2**
  over a comparable window. Two minutes across twelve days is the residue of
  whole-item placement and is not worth closing.

- [x] ~~🟠 **`Block(items="some_key")` silently plays nothing, and
  `example_channel.py` documents it as the way to do it.**~~ **Fixed
  2026-09-08.** `Block.__post_init__` now refuses a bare string and names the
  fix in the message (`OrderedCollection(["key"])` to repeat it for the slot,
  `["key"]` to play it once), so the failure lands at import time instead of
  as an empty slot three hours into a build. `engines/blocks.py` keeps a
  second guard — `_block_items_are_iterable`, logged as an error before the
  loop — for a block mutated after construction, because the two fail
  differently: the constructor stops a channel being *written* wrong, the
  engine stops one *playing* wrong. A repo-wide test
  (`TestSilentConfigFailures.test_every_block_in_the_lineup_is_iterable`)
  walks every `Block` in `channels/` and `library/` so this cannot come back
  on a channel nobody was looking at. All 18 channels import clean and a
  7-day sweep of the lineup runs 112 channel-days with zero errors.
  *Original entry below.*
  `engines/blocks.py::_get_next_block_item` accepts a collection (anything with
  `.pick`) or a `list`, and returns `None` for everything else — so a bare
  content-key string makes the block report `0 items played`, time does not
  advance, and the slot falls through to the circuit breaker. There is no
  warning: the block looks correctly configured, resolves a real key, and plays
  nothing.

  Found building Japanorama 2026-09-03, where three single-key blocks
  (`FRIEREN_NIGHT`, `VINLAND_NIGHT`, `GHIBLI_SUNDAY`) took out 19:00–23:00 with
  circuit breakers on most days of a 365-day simulation. `validate_schedule`
  reported no gaps throughout, so it read as a content problem rather than a
  config one.

  The fix at the call site is `OrderedCollection(["the_key"])` — a one-item
  *list* resolves once and then exhausts the rest of the slot, while a one-item
  collection keeps handing the same key back, which is what a strip wants.
  `example_channel.py` line ~57 shows `items="collection_80s_cartoons"` and
  has been corrected to the collection form, but the engine should either accept
  a bare string or warn on one; every other channel happens to pass a collection
  or a list, which is why this survived this long.

- [x] ~~🔴 **ErsatzTV has not re-indexed the reorganised music video collection,
  and The Beat is scheduled against paths that no longer exist.**~~
  **Verified fixed 2026-09-07** by reading the live guide. The Beat carries
  1,448 programmes on a 2026-09-07 epoch, **0** of them titled with the old
  genre buckets (`hip_hop`, `rock`, `pop`, `oldies`, `dance`), and **98% carry
  a `<date>`** — the titles are artist names, which is the reorganised shape.
  The rescan ran and the playout was rebuilt against it. The open question the
  entry raised — whether ErsatzTV indexes `<year>` from a music video `.nfo` —
  is answered yes; no fallback to `<tag>80s</tag>` is needed.
  *Original entry below.* Confirmed in
  the live guide 2026-09-02 after the reorg: The Beat still airs 751 videos whose
  `<title>` is `hip_hop` (244), `rock` (128), `pop` (120), `oldies` (64) and
  `dance` (37) — the old genre-bucket folders, **none of which exist on disk any
  more** — and 0 of the 751 carry a `<date>`. Totally 80s shows the same thing
  from the other side: its remaining gaps are exactly 04:00-06:00 on each of
  three days, precisely The Video Jukebox slot, because `eighties_music_videos`
  still resolves to nothing.

  **Two actions, in this order.** A library rescan in ErsatzTV, then a rebuild
  or reset of the affected playouts — Totally 80s *and* The Beat. A reset before
  the rescan rebuilds against the stale index and changes nothing. Until the
  rescan, The Beat's scheduled items point at dead paths and will fail to play.

  **What the guide cannot tell us** is whether a rescan has simply not run, or
  has run and ErsatzTV does not index `<year>` from a music video `.nfo` into the
  `year:` search field. Guide entries snapshot metadata at playout build time, so
  a stale playout and a stale index look identical from outside. If the gaps
  survive a rescan *and* a rebuild, it is the second case, and the fix is to key
  the block off `<tag>80s</tag>` instead of the year range.

- [x] ~~🟡 **A `Fallback` secondary must be a bare content key, never a
  wrapper.**~~ **Fixed 2026-09-08.** `Fallback.__post_init__` now rejects a
  non-string on *either* side — primary had the same hole and no one had
  looked. The lineup's only live `Fallback` (The Video Jukebox) and the one
  `pipeline.py` builds internally both already passed keys, so nothing needed
  changing at the call sites; the point is that the next one cannot be written
  wrong. *Original entry below.*
  `play_with_fallback` hands the secondary straight to `play_item`, which does not
  resolve wrappers — a `RandomCollection` there is stringified into
  `"<RandomCollection object at 0x...>"`, matches nothing, and still reports
  success. Caught 2026-09-02 while making The Video Jukebox degrade gracefully:
  the first version named a Collection and filled 04:00-06:00 with a repeated
  object repr. Same trap `dispatcher.resolve_fallback_key` documents for
  `fallback_content`, and nothing type-checks it at definition time. `Fallback`
  had no users in the lineup before this, which is why it was never hit.

- [ ] 🟡 **`fill_strategy="bridge"` cannot close a tail shorter than one item,
  and will open one.** `pad_until_exact` places only whole items and the bridge's
  trailing fill falls through to a bare `wait_until_time` when nothing fits, so
  bridging The Video Jukebox left **two minutes of dead air at 05:58 every day**
  — the exact tail the bridge exists to close. `yield` there is clean, because
  the Runner starts the next slot early instead. Bridge is right for a block
  whose neighbour is another Block; it is wrong for one whose items are shorter
  than the remainder it leaves.

**The method that found all three.** Walk the schedule summing each item's
duration and flag wherever the next item starts after the previous one ends.
The existing tools did not do this — `visualize_week` prints structure and
`collision_report` compares channels, but nothing measured continuity.

**Now a tool: `scripts/testing/continuity_check.py`** (2026-09-07). It reads the
live XMLTV export rather than a simulation, which is the important half — a
simulation shows what the current code would build, and the most common cause of
a real gap is a playout built by older code and never reset. Exits non-zero when
it finds one, so it can gate a pipeline; `--future-only` restricts it to the
gaps that can still be fixed.

### 2026-09-01 — what the live server said that the offline tools could not

Found by reading `iptv/xmltv.xml` off the running box rather than by simulating.
**Not one of these is a query defect.** `key_census` scores all 485 keys and
every key belonging to the affected channels passes; `validate_titles` is clean
on all four. The offline tools ask "can the library satisfy this query", and the
answer was yes in every case. The question they cannot ask is "is the right
thing actually on the air".

- ~~🔴 **Nightmare Theatre aired the Good Times sitcom lineup.** For a window on
  2026-08-31 the horror channel carried 171 sitcom episodes — Bob Newhart, Mary
  Tyler Moore, Fresh Prince, M\*A\*S\*H, Sanford and Son. Its 34 titles were a
  **100% subset** of Good Times' 36. A frame pulled from the live HLS stream at
  20:44 showed 30 Rock and matched the guide exactly, so stream and EPG agreed
  with each other and both were wrong.~~ Fixed by a playout refresh; the channel
  now carries 40 programmes over 35 titles, all horror. **The code was never at
  fault** — the local simulation for the same build scheduled correct horror
  (Tales from the Crypt, The Legacy, Hannibal, Twin Peaks, Ash vs Evil Dead).
  The defect lived entirely in ErsatzTV's playout wiring, which is in the
  root-owned SQLite DB and invisible to everything in `scripts/`.

  **The lesson worth keeping:** a channel can be perfectly configured, pass every
  offline check, and still broadcast another channel's content. Title *diversity*
  is not a health signal — 34 distinct titles looked healthy and was the bug.
  Only reading the actual titles catches this.

- ~~🟠 **High Noon was defined but never on air.** Channel 243 existed in
  `/api/channels` (id 20) yet appeared in no feed.~~ Fixed in two steps, which is
  the useful part: enabling the channel put it in `channels.m3u` but **not** in
  `xmltv.xml`, and it took a separate EPG enable plus a build before it
  appeared. It now carries 84 programmes over 16 titles — Gunsmoke, Bonanza,
  The Rifleman, Wanted: Dead or Alive, Rawhide. See the channel-visibility
  ladder in [ERSATZTV_API.md](ERSATZTV_API.md); the three states are distinct and
  a channel can sit in any of them.

- ~~🟡 **Logs grew without bound, and it looked like an infinite loop when it was
  not.** `logs/pond.log` reached 88MB with 983,457 lines and only 2,032 distinct
  ones, repeating `Item: Unnamed Item (17:00-20:00)` / `Fill Strategy: 'yield'.
  Stopping.` at a single timestamp.~~ There was no spin. Counting structure
  rather than repetition: 3,749 day-headers over 36,887 blocks and 258,977
  programmes is **~7 programmes per block and ~10 blocks per day, which is
  normal**. The file held **eleven complete runs** stacked between 18:07 and
  18:16, because `logging.FileHandler` opens in append mode and never rotates.
  The identical lines were consecutive ordinary days sharing a wall-clock second.

  Fixed in two places. `core/logger.py` now uses a `RotatingFileHandler` with
  `maxBytes=0` and an explicit rollover at construction — nothing rotates *during*
  a run, so one build is always one file, but each run starts clean and the last
  `LOG_BACKUP_RUNS` (default 3) are kept as `.1`/`.2`/`.3`. And
  `library/queries.py:196` now summarises the seasonal tag injection: the OR-chain
  was 409 characters a line, 55,148 times, 20.5MB per file — the single largest
  byte category, larger than the programme lines. A/B on the same one-day build
  measured **31,083 → 24,990 bytes, 19% smaller**, with the full query still
  available at DEBUG behind `LOG_FULL_TAG_QUERIES`.

  **Diagnostic note:** repetition alone is not evidence of a loop. Divide by the
  structural counts — days, blocks, programmes — before concluding anything.
  This one cost a wrong call in the first pass of the audit.

### 2026-08-30 — content-key and schedule-shape bugs

Found by the collision report and the library census, both added this session.
Every one of these was silent: the schedule built, the simulation stayed green,
and the channel aired something. What it aired was wrong.

- ~~🟠 **Cartoon Network's guide never showed an episode title.** All 21
  blocks in `library/animation.py` set `use_epg_group=True` — the only channel
  in the repo with no ungrouped airtime (disney 8/15, nickelodeon 3/10, every
  other library 0). `engines/blocks.py:99` wraps a whole block in an EPG group
  on that flag, and ErsatzTV collapses the group into one guide entry named
  after the block, so the grid read "The Vault" / "Cartoon Cartoons" /
  "Toonami" / "Adult Swim" from 06:00 to 06:00 and could never surface what was
  actually on. Nothing was wrong with the scheduling — the items played fine,
  they were just invisible.~~ Fixed: all 21 flags are now `False`. Grouping is
  kept **for marathons only**, which get it independently from
  `logic/calendar/assembly.py:122` when the marathon Block is built — so
  "DBZ Marathon" still reads as one entry, which is the case grouping is for.
  Verified against the simulator: a normal Friday went 10 groups → 0, and
  2026-07-04 / 2026-09-05 kept exactly their one marathon group each. Item
  counts drop by 2 per removed group because the mock records the start/stop
  as pseudo-items; no content was lost.

  Extended the same day to the other two channels, on the operator's call:
  disney (8 blocks) and nickelodeon (3) are now `False` as well, so **no static
  block anywhere in the repo is EPG-grouped**. Weekly groups: Disney 29 → 0,
  Nick 15 → 0, Cartoon Network 0; real item counts unchanged at 434 / 490 /
  676. The Nick removal also un-hides the nine Nick at Nite classics shared
  with Good Times, which were grouped 14x a week behind two block names.

  **The reason grouping is not worth keeping as it stands:** `playout.py:299`
  always passes `custom_title`, and on a live build that renders as one
  name-only guide entry — no artwork, no episode title, no description.
  Whether a group *without* `custom_title` would keep per-item metadata is
  open question #5 in [ERSATZTV_API.md](ERSATZTV_API.md); it needs one real
  build, and the mock explicitly does not model grouping effects. Until that is
  answered, grouping stays only where the items really are noise — marathons,
  via `logic/calendar/assembly.py:122`.

- ~~🟡 **Two Programs were named `<built-in method title of str object at
  0x...>`.** `animation._with_bumpers` did `getattr(item, "title", str(item))`,
  but `str` *has* a `.title` method, so a bare content key returned the bound
  method instead of ever reaching the fallback. It hit both string call sites
  (`animation.py:466` and `:573`, the Attack on Titan rerun bed in the two
  Midnight Run blocks), and the memory address meant the name was not even
  stable between runs.~~ Fixed with an explicit `isinstance(item, ContentItem)`
  check. Log-only while the blocks were grouped; found during the EPG fix
  above, which is exactly what would have exposed it.

- ~~🔴 **Noir November had never once aired.** Mystery Theatre's signature
  seasonal takeover lived on `PRIME_BLOCK["default"]`, behind five explicitly
  named weekdays. `PRIME_BLOCK` is only wired into `SCHEDULES["WEEKDAY"]`, and
  Saturday/Sunday have their own prime, so nothing could ever reach the default
  arm.~~ Fixed: `"NOVEMBER"` is now the first key in the dict and dict resolution
  takes the first matching label. Scoped to November rather than FALL on purpose
  — a season-level swap would delete the Mon–Fri lineup for three months.
  Verified with Dark Winds, the one title unique to the block: 0 airings in
  October, 30 in November, 0 in December. `test_03_resolution_pipeline` now
  asserts the takeover instead of asserting that *something* resolved.

- ~~🔴 **Unreachable `default` arms across two channels.** When a block's guards
  are `WEEKEND` + `WEEKDAY_A` + `WEEKDAY_B`, or all seven day names, they cover
  the week and any `default` behind them is dead.~~ Five of Other Worlds' eight
  blocks had one. `EARLY_BLOCK`'s was the only weekday fantasy on the channel, so
  it never aired at all. Fixed: no block on either channel has an unreachable
  arm now.

- ~~🔴 **`supernatural_tv` queried a genre that does not exist.** It was
  `genre:"(supernatural OR tag:paranormal)"`. There is no Supernatural genre in
  the library and `tag:paranormal` is on three shows, so a near-empty key held a
  third of a daily block.~~ Fixed: `tag:supernatural OR tag:paranormal`, which is
  12 shows. `tag:supernatural` is the tag that actually exists.

- ~~🔴 **`true_crime_tv` resolved to one show with six episodes.**
  `genre:documentary AND genre:crime`. It was in `DETECTIVE_LATE_NIGHT`, which
  covers overnight, early *and* night — six episodes carrying 47 hours a
  month.~~ Fixed: true crime dropped from Mystery Theatre; the slot went to
  Alfred Hitchcock Presents (268 episodes, previously on no channel).

- ~~🟠 **A whole-season `Swap` deleted Other Worlds' weekday prime for three
  months.** `"SPRING": Swap(MODERN_SCIFI_BLOCK)` sat at the top level of the
  seasonal dict rather than inside a day map, so it replaced all five days.
  X-Files, Babylon 5, BSG and Sarah Connor each dropped to about 45 minutes a
  week.~~ Fixed: spring is per-day, matching how summer was already written.
  **General trap:** at the top level of a `SeasonalBlock`, `Swap` replaces every
  day. Nest it in a day map unless a total takeover is the intent.

- ~~🟠 **`space_opera_tv` was the widest pool in the registry.**
  `genre:"science fiction" AND NOT tag:sitcom` — the only sci-fi key without a
  `NOT genre:fantasy` clause, so it returned everything `scifi_tv` did plus
  Stargate SG-1, Quantum Leap, Xena and Sabrina the Teenage Witch. It was
  scheduled 52 hours a week as though it were a themed block.~~ Renamed
  `scifi_all_tv` and used deliberately for one broad slot. **Do not simply add
  `NO_FANTASY` to it:** this library tags Stargate SG-1 and Quantum Leap as
  Fantasy, and that clause is exactly why the named title collections exist.

- ~~🟠 **`MYSTERY_MOVIE_WHEEL` contained no movies.** Named for the NBC wheel;
  held Columbo, Poirot, Miss Marple and Murder She Wrote, all television. It was
  Saturday evening *and* prime.~~ Fixed: the TV rotation is `WHODUNIT_WHEEL` and
  the movie wheel shows film. Mystery Theatre went from 2% film to 18%, against
  a library of 365 crime and mystery features.

- ~~🟠 **Title queries that matched the wrong thing, or nothing.**~~
  `show_by_title("Magnum P.I.")` against a folder named `Magnum, P.I.`;
  `show_title:"Star Trek"` is a phrase match and returned every Trek series,
  making Other Worlds' vault a second Trek playlist; a bare `"House"` also
  returns House of the Dragon and House Of Cosbys. Fixed by correcting the comma
  and year-bounding the other two. **Verify title queries against
  `reference/library-tv.tsv` — the simulator cannot catch these, because it
  generates a key from whatever title it is given.**

- ~~🟠 **`collision_report.base_key()` collapsed every appointment show to
  `_`.**~~ `factories.annual_show` mints `__auto_<title>_s<n>`, which matched the
  tag-injection suffix pattern the normalizer strips. Lost, Alias and Fringe all
  became the same key, which would have invented collisions between them. Fixed
  with a prefix guard.

- ~~🟡 **`golden_scifi_tv` duplicates `syndicated_scifi_tv`** byte for byte.~~
  Still both present; `golden_scifi_tv` is on no channel. Left in place rather
  than deleted, but it is a trap.

- ~~🔴 **`id()`-seeded RNG broke determinism.** Collections/list picks seeded RNG
  with memory addresses, so output changed every process run.~~ Fixed: seeds now
  use `core/identity.stable_hash()`; `OrderedCollection` is date-anchored;
  `RandomCollection` resets per day. Verified reproducible across processes.
- ~~🟠 **No `requirements.txt` / undocumented `etv_client`.**~~ Fixed: added
  `requirements.txt` (stdlib-only) and README notes (container vs. local).
- ~~🟠 **`install_mocks()` ordering footgun.**~~ Fixed: auto-installed on
  `scripts.testing` import; production-safe (real client always wins).
- ~~🟠 **Stray non-Python prototype in `channels/`** (`main.go`, `schema.sql`,
  `simple_backend.py`).~~ Removed by author.
- ~~🟡 Stale module-path header comments / `schedule.py` reference.~~ Fixed in
  `library/queries.py`, `logic/resolution/resolver.py`, `logic/resolution/pipeline.py`.
- ~~🟠 **Broken test: `test_smoke_simple_channel_run`.**~~ Fixed: it now unpacks
  the 3-tuple from `assemble_day_schedule(...)`. `test_scenarios` is 9/9.
- ~~🟠 **Module-level caches leaked across channel builds**
  (`BUMPER_FAILURE_CACHE`, `_INJECTION_CACHE`).~~ Fixed: `reset_bumper_failure_cache()`
  / `reset_injection_cache()` are called at the start of `ScheduleRunner.run()`,
  scoping both caches to a single build. Verified entries don't survive a run.

- ~~🔴 **Run-aborting crash when a content-less Program hit a Block fallback.**~~
  An off-season Appointment Program (`content=None`, no active schedule) fell
  through to static resolution, which substituted `config.fallback_content`. When
  that fallback is a `Block`/Collection (e.g. Cartoon Network's
  `fallback_content=CLASSIC_CARTOONS`), the Block was handed downstream and
  `get_query_data` did `Block in dict` → `TypeError: unhashable type`, aborting the
  entire `run()` — i.e. "the channel just stops having content." Fixed: such
  programs skip cleanly (`engines/blocks.py`), and `get_query_data` is
  type-guarded (`logic/resolution/resolver.py`). Verified: 14 continuous days of
  Cartoon Network now schedule content with no crash.

- ~~🔴 **Marathons overran their window by days.** A marathon whose content is
  unbounded (a whole show, no episode range — e.g. `simpsons_random_marathon`)
  resolved to `play_count = None`, which `_convert_marathon_to_block` replaced
  with `DEFAULT_MARATHON_LIMIT = 1000` "to ensure continuous play". That became
  a single `add_count(count=1000)`, and ErsatzTV's `AddCountInternal` applies no
  time bound at all — it commits every item in one call. `strict_window` could
  not help: it is checked *between* block items, and the marathon block held
  exactly one. A 6-hour Simpsons slot became ~14 days of playout.~~ Fixed:
  `Program.fill_window` marks unbounded marathon content, and the engine asks
  for exactly the remaining window via `add_duration` (`playout.play_for_duration`).
  Verified: the 2026-04-30 Simpsons marathon now runs 16 items inside 16:00–22:00,
  down from 1000 items spanning 13d 21h. Regression test:
  `TestMarathonWindow.test_unbounded_marathon_stays_in_window`.
- ~~🟠 **`pad_until` / `wait_until` silently did nothing across month
  boundaries.**~~ The HH:MM endpoints carry the date in a separate `tomorrow`
  flag, and ErsatzTV schedules *nothing* (no error) when the target time of day
  has passed and `tomorrow` is false. All three call sites computed it as
  `target.day > now.day`, which is False on Aug 31 → Sep 1 (`1 > 31`). That is
  the "pad under-filled" failure the safety net in `fill_to_boundary` was
  papering over. Fixed: `fill_until_time` / `wait_until_time` take a `datetime`
  and call `pad_until_exact` / `wait_until_exact`, which also avoid ErsatzTV's
  own acknowledged DST bug in the time-of-day variants.
- ~~🟠 **The simulator could not reproduce API-contract bugs.** `MockAPI.add_count`
  ignored `count`, there was no per-key enumerator, and `pad_until`/`wait_until`
  always jumped to their target.~~ Fixed: the mock now follows
  `SchedulingEngine.cs`, the build window defaults to 2 days (matching
  `PlayoutDaysToBuild`), and API round trips are counted. Pinned by
  `TestApiContract` (8 tests). See [ERSATZTV_API.md](ERSATZTV_API.md).

- ~~🟠 **Marathon random start never fired.** `simpsons_random_marathon` declares
  `start_mode="random"` with `start_season=[3, 9]`, but the guard in
  `_convert_marathon_to_block` read `play_count and play_count > 1`.
  `play_count` is `None` for unbounded content — which is exactly the content
  that declares a random start — so the branch was dead and every Simpsons
  marathon opened on the same episode. It was also the only marathon in the
  library using `start_mode="random"`.~~ Fixed: the guard is now
  `play_count != 1` (None and >1 both have room to start somewhere), and season
  selection uses `boss.pick()` instead of `random.randint()`, which reseeded per
  process and would have broken same-date reproducibility once the branch went
  live. Verified: S9/S5/S9 on three trigger dates, identical across processes.
- ~~🟠 **`skip_to_item` was orphaned by injections.** The skip was issued inside
  `_resolve_and_prepare_program_content`, before `apply_injections` could
  rewrite the content key. Seasonal injection turned
  `auto_gen_cowboy_bebop_eps_23_26_d1e246` into `..._auto_spring`, so the skip
  positioned an enumerator that was never played from and the marathon silently
  started at episode 1. The Appointment TV branch had the same shape, skipping
  the registry key while playing `resolver.resolve(key)`.~~ Fixed: both branches
  now *report* a start point and `play_program` issues the skip once the final
  key is known. Verified: orphaned skips across two years of Cartoon Network
  went 30 → 0, with all 3001 correct skips preserved.
- ~~🟠 **Redundant `get_context` on the hottest path.** Every scheduling endpoint
  already returns a `PlayoutContext`, but `playout.play_item` discarded it and
  issued a separate `get_context`, doubling round trips against ErsatzTV's 30s
  build timeout.~~ Fixed: `play_item` uses the returned context and only falls
  back to `get_context` on failure. A Cartoon Network day went 295 → 152 calls.

- ~~🔴 **`premiere_season=("SEASON", "DAY")` scheduled nothing, silently.**
  `annual_show()` passes `(year, premiere_season)` to `states.resolve_season_date`,
  which only understood `(int, str)`. Given a tuple season it returned `None`,
  `_build_season_windows` skipped every season, and `_resolve_appointment_schedule`
  bailed on the empty window list — so the Program played its `reruns` forever and
  never premiered. No warning: an appointment that never fires is indistinguishable
  from one between seasons. `loop_restart_season` had the same problem from the
  other end — it defaults to `premiere_season`, and a tuple there failed the
  `isinstance(str)` check and silently selected the immediate-loop branch instead
  of the annual restart. Six appointments were dead: The Office, Parks and Rec,
  Community and 30 Rock (`library/sitcoms.py`), True Detective and Fargo
  (`library/detective.py`).~~ Fixed at the root: `resolve_season_date` now accepts
  a `(season, weekday)` pair and moves the resolved date forward to the first
  matching weekday, so a `("FALL", "THURSDAY")` premiere lands on a Thursday
  (2026-09-17) rather than on whatever day the season's peak starts (2026-09-15);
  `states.season_label()` normalises the season half in `annual_show` and
  `_apply_schedule_looping`. All six now premiere and advance weekly. Covered by
  `TestSeasonSpecResolution` (9 tests) in `test_scenarios.py`.

- ~~🔴 **`fallback_content` was silently dead on five channels.** It reaches
  `circuit_breaker`, which hands it straight to `play_item` — and `play_item`
  stringifies anything that is not already a key. A Block fallback arrived at
  ErsatzTV as the literal text `Block(name='The Disney Afternoon', items=<...
  object at 0x7f...>)`: matching nothing, carrying a memory address so it was
  not even stable between runs, and still logging "✅ Fallback succeeded". The
  two call sites disagreed — `engines/dispatcher.py` resolved first,
  `engines/blocks.py:141` passed it raw — so the same config behaved differently
  depending on which one fired.~~ Fixed: both now go through
  `dispatcher.resolve_fallback_key()`, which resolves, returns a key or None,
  and warns when a fallback resolves to something unusable. That makes
  Collections work at both sites (british, classic_movies, sitcoms were already
  passing Collections); Blocks remain invalid per `pipeline.py:109`, so Disney
  and Nick moved to new `disney_vault_tv` / `nicktoons_vault_tv` keys —
  genre-qualified OR queries over each channel's own shows, following the
  `toonami_vault_tv` pattern. Nick's deliberately excludes the Nick at Nite
  titles, which are shared with Good Times. Covered by `TestFallbackResolution`,
  including a repo-wide test that every channel's fallback resolves to a key.

- ~~🟠 **The simulator sized content by substring, inventing a failure.**
  `MockAPI._guess_duration` matched `'movie' in key`, so the *show* Home Movies
  — key `auto_gen_home_movies_<hash>` — was treated as a two-hour film. That one
  item ate the rest of its Adult Swim block and all of the hour after it, which
  made Cartoon Network appear to drop its Friday 23:00 slot every single week
  and never air Attack on Titan Junior High. `validate_schedule` reported no
  gaps throughout, so it read as a real scheduling bug rather than an artifact.
  `intro`/`outro` were also absent from the shorts list while `bumper`/`filler`
  were present, so branding stings were sized at 20 minutes — 40 minutes of
  ident either side of a block boundary, enough to squeeze a real item out of a
  one-hour slot.~~ Fixed: a registered `type:movie` query is now authoritative,
  name matching is on whole words rather than substrings, and `intro`/`outro`/
  `ident`/`promo` are shorts. `validate_schedule` uses the duration the build
  actually recorded instead of re-deriving it. Three library titles tripped the
  old wire; only Home Movies was scheduled anywhere. Covered by
  `TestSimulatorDurationGuess`.

- [x] ~~🟠 **`ChannelLogger` binds `sys.stdout` at handler construction, which
  silently breaks multi-day log capture.**~~ **Fixed 2026-09-08.** The console
  handler is now `_StdoutHandler`, a `StreamHandler` whose `stream` is a
  property returning `sys.stdout` at emit time and whose setter discards what
  `__init__`/`setStream()` try to store. `redirect_stdout` therefore behaves
  the way every caller already assumed, and the documented workaround --
  attaching a handler by lowercased prefix after a throwaway `simulate_day` --
  is no longer needed. Regression-tested by `TestLogCaptureAcrossDays`, which
  constructs the logger *inside* the first redirect (the exact shape that
  bound the stream) and asserts each of three days lands in its own buffer.
  The 7-day, 16-channel sweep on 2026-09-08 is the first multi-day scan in
  this repo that is trustworthy for the reason it claims to be.
  *Original entry below.* `__init__` builds
  `logging.StreamHandler(sys.stdout)` behind `if not self._log.handlers`, so the
  handler is created once per channel name and keeps whatever `sys.stdout` was
  bound to at that moment. Any validation loop shaped like
  `for d in dates: with redirect_stdout(buf): sim.simulate_day(d)` therefore
  captures **day one only** — day one constructs the logger while the redirect is
  active, and days 2..N write into that same first buffer while the caller reads
  an empty one. A 365-day error scan built this way is a one-day scan, and it
  reports clean because it saw nothing. Found 2026-08-31 while validating Across
  the Pond, where it produced a confident "0 errors over 365 days" from a single
  day of log. **Workaround:** attach a `logging.Handler` to the channel's named
  logger — the prefix lowercased with brackets stripped, so `[POND]` is `pond`,
  `[CARTOONS]` is `cartoons`, `[HIGH NOON]` is `high noon` — after one throwaway
  `simulate_day` has constructed it. **Fix:** resolve `sys.stdout` at emit time
  rather than construction, or put a `capture()` context manager on the class so
  callers stop reaching for `redirect_stdout`.
- [ ] 🟡 **A local simulation still writes to the same log file name a real
  build would.** `ChannelLogger` attaches its file handler to
  `LOG_DIR/<name>.log` regardless of who is running. The unbounded-growth half of
  this was fixed 2026-09-01 (see Resolved) — each run now rotates, so a file
  holds one run rather than eleven — but rotation makes the *provenance* problem
  slightly worse, not better: a local sim run now pushes the previous file to
  `.1`, so a build's log can be aged out by simulations. **Check timestamps
  before reading `logs/` as evidence that a deployment happened**, and remember
  that local logs were never proof of a real build. The durable evidence is
  `iptv/xmltv.xml` on the server.

- [ ] 🟡 **Casablanca (1943) airs on Be Kind Rewind, which is 1980-to-now.**
  Found 2026-08-31 by cross-referencing the live EPG against
  `reference/library-movies.tsv`. It is the only violation in the channel's
  35-film lineup — every other title the manifest can date is 1980+ — and the
  channel is otherwise clean (35 films, 35 distinct titles, zero repeats over a
  68-hour span). The era line is Cabes Classic Cinema pre-1980, Be Kind Rewind
  1980+, so this belongs on CCC.

- [ ] 🟠 **`the_office_tv` matches two different shows, and Across the Pond is
  airing one of them.** `key_census` flags it BROAD: two shows, 224 episodes,
  both titled "The Office". The British channel currently schedules it, and
  nothing in the key distinguishes the UK original from the US remake — this is
  the phrase-match trap `library/horror.py` documents, and the fix is the same,
  bound it by year. Until then Across the Pond can serve the American version.

- [ ] 🟠 **Nothing checks for shows that are on disk and have no registry key.**
  `key_census` resolves every key in the registry, so a show no key names is
  invisible to it — it is not an empty key, it is an absent one. Diffing
  `reference/library-tv.tsv` against every title mentioned anywhere in
  `library/` found **five 1980s shows in this state**: Murphy Brown (244
  episodes), Roseanne (221), In Living Color (126), The Kids in the Hall (101),
  Pee-wee's Playhouse (46) and Police Squad! (6). All six are registered and on
  Totally 80s as of 2026-09-01, but **the same diff has not been run for any
  other era or channel**, and the 1980s were only checked because that channel
  was being rebuilt. The one-liner is in the 2026-09-01 session notes; it wants
  to be a tool next to `key_census`. Also note the four PBS/DIY shows the same
  diff surfaced — The Joy of Painting (403), The Woodwright's Shop (479), This
  Old House (234), The New Yankee Workshop (151) — 1,267 episodes with no key
  and no channel, which is most of a daytime schedule for Travelers Table.

- [x] ~~🔴 **Totally 80s and Cabes Classic Cinema are running 2026-03-17
  playouts and have never been reset.**~~
  **Verified fixed 2026-09-07.** No channel on the lineup carries a March
  epoch any longer. All 18 channels in the live `xmltv.xml` start between
  2026-08-30 and 2026-09-07; Totally 80s and Cabes Classic Cinema are both
  2026-09-02, and Nickelodeon has moved off its 2026-08-30 epoch. The resets
  were done. **A narrower version of the same rule survives** — see the
  pre-rescan playout entry at the top of Open.
  *Original entry below.* Found 2026-09-02 by reading the live
  `xmltv.xml` after Good Times and Corncob were deployed: every other channel
  carries an August or September epoch, those two carry March. Consequences are
  live now — Totally 80s has **26 hours of future gaps** (10.5 h from Thu 03
  Sep 10:04, 9 h from Fri 04 Sep 08:13) and is broadcasting its *pre-redesign*
  grid, airing Full House at 09:11 in a slot the 2026-09-01 redesign
  deliberately cleared because Good Times holds that title. Cabes Classic
  Cinema has 5 gaps totalling 497 minutes.

  **Not a config defect.** The current code simulates 60 days of Totally 80s
  with 2,596 programme plays and no gaps, overlaps or circuit breakers. This is
  the rule from the deployment notes biting: *a plain rebuild only extends the
  playout forward; already-built items keep their old guide entries.* Fix is a
  reset, not an edit.

  **Nickelodeon (247) is the mild version** — a 2026-08-30 epoch, so it has not
  picked up the `addams_family_tv` query fix and its Nick at Nite block is
  still playing six shows where seven are declared.

- [ ] 🟠 **Mystery Theatre and Totally 80s both air Magnum, P.I. at midday.**
  Found 2026-09-02 by diffing the **live** `xmltv.xml` off the server rather than
  by simulating. `detective.RETRO_PI_STRIP` is Mystery Theatre's midday block
  (10:00-12:00 weekdays) and names Magnum by title;
  `eighties.FALL_WINTER_DAYTIME_WHEEL` draws `eighties_crime_tv` over the same
  two hours and again at 14:00-17:00, which returns him, and
  `eighties.PI_WEDNESDAY_COLLECTION` names him by key at prime.

  **The Miami Vice half is fixed** (2026-09-02): it is off `RETRO_PI_STRIP`,
  replaced by Remington Steele. The channel's own identity settled it before the
  collision did — every other title in that hour is a case show and
  `reference/library-tv.tsv` tags Magnum, Moonlighting and Remington Steele
  `Mystery` while Miami Vice is `Crime; Drama` and nothing else. Totally 80s
  keeps it, and has the stronger claim: it names the show by key as a Wednesday
  prime appointment.

  **Magnum is the harder half and is still live.** He is a P.I. case show tagged
  `Mystery`, so Mystery Theatre's claim is real; he is also 1980 and central to
  Totally 80s' P.I. Wednesday. The hours only truly collide through the genre
  pool — Wednesday prime (20:00-23:00) and Retro P.I. (10:00-12:00) do not
  overlap — so the narrow fix is excluding him from `eighties_crime_tv`'s
  *daytime* draw while P.I. Wednesday keeps him by name.

  **Why no offline tool caught it.** `collision_report` section 1 groups by
  *key name*. Mystery Theatre names Miami Vice in an inline `{"title": ...}`
  dict and Totally 80s reaches it through `eighties_crime_tv`, a genre pool --
  two different keys, one show, so the pairing never appears. This is the exact
  failure mode channel-plan.md described for the duplicate `eighties_sitcom_*`
  keys, in the other direction: there, one pool wore two names; here, one show
  is reachable through a pool and through a title.

  **The lead worth following is the method, not the fix.** `xmltv.xml` is
  ground truth and the check is cheap -- parse it, group programmes by title,
  flag overlapping windows on different channels. Run over the live guide it
  found **8 distinct same-title pairings across 20 overlapping airings**, of
  which only this one is between two *scripted* channels; the rest involve
  Lucy TV, Japanorama, Travelers Table and Nickelodeon, which `collision_report`
  cannot see at all because they have no channel module to simulate. One of the
  eight -- I Love Lucy on Lucy TV against Nick at Nite -- is the lineup's
  written exemption (C5) and is correct.

  Also live and undocumented: **The Great British Bake Off** (Across the Pond /
  Travelers Table), **Attack on Titan**, **The Boondocks** and **Cowboy Bebop**
  (Cartoon Network / Japanorama), **Street Hawk** (Mystery Theatre / Other
  Worlds) and **Laid-Back Camp** (Japanorama / Travelers Table).

- [x] ✅ **FIXED 2026-09-01 (Good Times rebuild). Good Times declares no
  `evening` in its `WEEKEND` schedule.** All seven days now declare all ten
  slots, and the weekend arms are gone entirely -- the channel is keyed by
  weekday name, one arm per network. Original report:
  `channels/sitcoms.py:53` covers overnight, early, morning, midday, noon,
  afternoon, prime and night, and skips `evening` — so 17:00–20:00 on Saturday
  and Sunday falls through to `fallback_content`, which is
  `sitcoms.LATE_NIGHT_SYNDICATION`. The hours are not dead, but they are
  unprogrammed, and the pool they land in is the late-night one: Cheers, The
  Wonder Years, Married... with Children, Coach, Newsradio, Drew Carey, Wings,
  Mad About You, 3rd Rock, The Nanny. **Found from the outside**, when Totally
  80s' new weekend evening strip collided on Married... with Children and The
  Wonder Years against a channel whose declared grid said those hours were
  empty. Totally 80s works around it with a separate `WEEKEND_EVENING`
  collection; the fix belongs on Good Times. Worth checking every channel for
  the same shape — a named slot missing from one day-group reads as deliberate
  and is usually an omission.

- [ ] 🟡 **1980s film is on two channels between 22:00 and 23:00 on Friday and
  Sunday.** Totally 80s' prime runs to 23:00 and both those nights are films
  (`eighties_blockbuster_movie`, `eighties_drama_movie`); Be Kind Rewind's The
  Late Show starts at 22:00 and draws `eighties_cult_movie` and
  `80s_pure_movie`. The era line puts the decade on Totally 80s by day and Be
  Kind Rewind from 22:00, and this is the one hour where that is not true.
  Pre-existing — Totally 80s' prime ran 17:00–23:00 before the 2026-09-01
  redesign, so the overlapping hour is the same one — and deliberately not
  fixed there, because both candidate fixes (move The Late Show, or split
  Totally 80s' prime so film nights end at 22:00) change a channel the pass was
  not scoped to. `same_title_check` scores it POSSIBLE rather than CONFIRMED
  only because `tag:cult` and `tag:blockbuster` are not columns in the TSV.

- [x] ✅ **FIXED 2026-09-01 (Good Times rebuild). Must See Thursday replays
  each episode two or three times a night.** The Office, Parks and Recreation,
  Community and 30 Rock are single-camera and moved to Corncob TV with the
  Thursday they anchor, so the stacked `DailyOrderedCollection` is gone. Good
  Times' prime is now one named night per weekday, gated by a weekday arm of
  `SCHEDULES` -- verified over three simulated years, each night on its own
  day and nowhere else. Original report:
  `sitcoms.MUST_SEE_THURSDAY` is a four-item `DailyOrderedCollection` in a
  three-hour prime slot (20:00–23:00), so the collection wraps and each
  appointment resolves to the same episode again: The Office S1E1 airs at 20:00,
  21:20 and 22:40. Structural and pre-existing — the block has always been four
  items in a ~six-slot window — but it was invisible while the appointments were
  dead, because the wrap landed on four different rerun collections instead. Now
  that they premiere, it shows. `detective.SUNDAY_PRESTIGE_BLOCK` has a mild
  version of the same thing (one wrap at the tail, 2026-09-20). Fix is a
  programming decision, not a code one: give the block a syndication tail so the
  wrap lands on reruns rather than back on the appointment, or shorten the slot.
  Note that any tail added here has to respect the Nick at Nite sharing rule —
  the block reaches 23:00, and Good Times stays clear of 21:00–02:00 for the nine
  shared classics.

### 🟠 Correctness / robustness

- [x] ~~**`frequency` paces an appointment, it does not gate the airing.**~~
  **Fixed 2026-09-08 in the resolver**, which was the first of the two options
  this entry offered. `_find_active_episode` now returns `None` when the
  airing date's weekday is not in an explicitly declared `frequency` list, so
  the slot falls to the program's `reruns` bed — where a rerun belongs — and
  the day-gated block variants become belt-and-braces rather than load-bearing.

  **Gated on an explicit list only.** `"weekly"` infers its day from the season
  window start, which in Broadcast Mode is a seasonal *peak date* the caller
  never chose; gating on that would silently confine a show to whatever weekday
  the ramp table happened to land on — the same class of silent failure this
  change exists to remove. `"daily"` normalises to every day, so gating it is a
  no-op. All 26 appointments in the library declare explicit day lists.

  > **The trap, worth writing down.** The first version gated on the date
  > `_find_active_episode` receives — which `_apply_schedule_looping` has
  > already rewritten into the season window, landing on an arbitrary weekday.
  > That dropped Rurouni Kenshin from Toonami's **Thursday**, a day it plainly
  > declares. The real airing date now travels separately as `airing_date`.
  > **Nothing caught this but the diff**: 48 unit tests stayed green, and it
  > surfaced only because 14 days of all 16 channels were snapshotted before
  > and after and compared item by item. For a behaviour change in a resolver,
  > diff the schedule — the tests cover what you thought of.

  Verified a no-op on the current lineup: **0 changed channel-days out of 224**
  after the correction, which confirms this entry's claim that every
  appointment was already saved by its block. Regression-tested by
  `TestFrequencyGatesTheAiring` — off-frequency days resolve to nothing, the
  episode index still steps by one across consecutive airings (gating must not
  break pacing), and a *looped* strip keeps every day it declares.
  `_find_active_episode` returns the current episode for *any* date inside the
  season window; `frequency` only controls how fast the episode index advances.
  So an `annual_show()` with `frequency=["FRIDAY"]` sitting in a block that runs
  seven nights a week airs the same episode all seven of them — a premiere that
  premieres every night. Every appointment in the library gets away with it
  today only because its block happens to be day-gated: Disney's four Saturday
  events live in a Saturday-only slot, and Cartoon Network's Attack on Titan
  Junior High needed a Friday-only block variant
  (`animation.MIDNIGHT_RUN_PREMIERE`) for the same reason. Either the resolver
  should return `None` off-frequency, or `annual_show()` should refuse a
  frequency the caller cannot honour. Found in the CN restructure.

- [x] ~~**`circuit_breaker` never resolves `fallback_content`.**~~ **Closed
  2026-09-08.** Two halves, and only one was still open. **The resolution half
  was already done** -- `dispatcher.resolve_fallback_key` exists and *both*
  call sites (`engines/dispatcher.py` and `engines/blocks.py`) route through
  it. **The entry's claim that "nick, disney, detective and sitcoms all still
  pass Blocks or Collections" was stale**: every channel in the lineup passes
  a bare key except Corncob and Good Times, which pass a `RandomCollection` --
  and a Collection is *valid*, since `resolve_fallback_key` resolves it to a
  key. Only a `Block` cannot. So the fix taken is the other one the entry
  proposed: **`ScheduleConfig` now rejects a `Block` fallback at
  construction**, the guard that fires before a channel ever runs. The runtime
  defence stays, and `test_scenarios` covers both -- the constructor raising,
  and `resolve_fallback_key` still returning `None` if a Block is assigned
  past it. *Original entry below.*
  `playout.circuit_breaker` hands `config.fallback_content` straight to
  `play_item`, which requires a string key — so a `Block` or a Collection logs
  "play_item received non-string content", advances nothing, and the breaker
  still reports "✅ Fallback succeeded". Cartoon Network now passes a key
  (`"animated_classic_tv"`); **nick, disney, detective and sitcoms all still
  pass Blocks or Collections** and have a fallback that cannot fire. Fix either
  end: resolve in the breaker, or make `ScheduleConfig` reject a non-key
  fallback at construction rather than at the worst possible moment.

- [x] ~~**A Contiguous-Mode strip goes dark waiting for autumn.**~~ **Fixed
  2026-09-08**, exactly as this entry proposed: `loop_restart_season` now
  defaults to `False` whenever `start_date` was used. A contiguous strip has no
  premiere season to restart in — the caller passed a date and never named
  one, so the old default took `premiere_season`'s untouched `"FALL"`.
  Confirmed against the failure: a weekday strip of 20 episodes from 2026-03-02
  resolved to nothing on 10 Jun, 20 Jul and 5 Aug under the old default and
  stays on air under the new one. Cartoon Network's six Toonami strips pass
  `loop_restart_season=False` by hand and are unaffected.
  `annual_show()` defaults `loop_restart_season` to the season half of
  `premiere_season`, which is `"FALL"` — including in Contiguous Mode, where the
  caller passed `start_date` and never named a premiere season at all. A weekday
  strip that finishes its run in June then resolves to nothing until
  mid-September, the block skips the item, time does not advance, and the slot
  falls through to the circuit breaker. Cartoon Network's six Toonami strips now
  pass `loop_restart_season=False` and a `reruns=` bed explicitly; the default
  should probably be `False` whenever `start_date` was used.


- [ ] **Errors swallowed into dead air.** `playout.play_item` catches all
  exceptions and returns an unadvanced context; pre-registration and several
  helpers `except Exception` → warn; the circuit breaker then force-skips time. A
  genuine config error (typo'd content key, bad Lucene) can surface as a silent
  gap rather than a clear error. Fix: add a strict/validate mode that fails loudly
  on unknown keys, ideally during pre-registration.

### 🟡 Quality / maintainability

- [x] ~~**Unescaped title interpolation.**~~ **Fixed 2026-09-08, and the entry
  was half wrong.** `play_smart_bumper` did interpolate an unescaped title into
  a `tag_full:` phrase, so a title carrying a double quote (`"Weird Al"
  Yankovic`) closed the phrase early and the show lost its bumper silently.
  That half is fixed: the helper is now public as `queries.escape_quotes` and
  the dispatcher uses it for both the title and the tag values.

  > **Correction.** The `inject_tag` half was a misdiagnosis. `tag_query` there
  > is not a value to be escaped — it is a hand-authored Lucene *expression*
  > (`"tag:Christmas"`, and the OR-chains in `SEASONAL_TAG_QUERIES`). Escaping
  > it would break every seasonal injection in the library. The distinction is
  > the general one: escape values, never expressions.

  Two function-level imports went with it — `escape_quotes` and
  `extract_title_from_query` are now module-level in `dispatcher.py`, which is
  safe because `library/queries.py` imports nothing but `settings`.
- [ ] **Doc reconciliation (partial).** `ARCHITECTURE.md` structure + determinism
  sections are current, but the "Key Files Deep Dive", "Data Flow Examples", and
  "Configuration Objects" prose still use historical names
  (`resolve_schedule_target`, `collections.py`, `run_marathon`, etc.).
  `CONCEPTS.md` and `IMPORTS.md` likely drifted too — audit and update.
- [ ] **The collision report's SAME COLLECTION tier attributes through
  unscheduled collections.** `collection_membership()` maps keys to every named
  collection that lists them, including ones no channel airs, so findings read
  as "via `movies.TIME_TRAVEL_SPOTLIGHT`" when that spotlight is scheduled
  nowhere. The underlying clash is real; the attribution is misleading. Either
  restrict the tier to referenced collections or label dead ones. Related:
  `CYBERPUNK_SPOTLIGHT`, `TIME_TRAVEL_SPOTLIGHT` and `ALIEN_INVASION_SPOTLIGHT`
  in `library/movies.py` are all defined and used by nothing.
- [x] ~~**`test_imports.py` is broken, and is not in the repository.**~~
  **Deleted 2026-09-08.** All four of its import paths were dead, not just the
  first — `channels`, `scripts.schedule`, `scripts.engines.run_marathon` and
  `scripts.resolvers`. `scripts.testing.test_refactor` covers what it was for.
  *Original entry below.* It does
  `from channels import cartoon_network`, which has not been the module path
  since the `scripts/` package reorganisation — confirmed 2026-09-07,
  `ModuleNotFoundError: No module named 'channels'`. Corrected detail: it sits
  in the *parent* directory, one level above the git root, so it is tracked by
  neither repo and will not ship. Delete it or fix it to
  `from scripts.channels import cartoon_network`; `scripts.testing.test_refactor`
  already covers what it was for.
- [ ] **Thin automated tests.** `testing/test_comprehensive.py` is print-based
  (no asserts). `test_scenarios.py` does use `unittest`. Add assertion coverage
  for date math (leap years, year wraparound), determinism (same date → same
  output across runs), and the Appointment-TV episode math in
  `logic/resolution/pipeline.py`.
- [ ] **Circular-dependency smell.** Runtime imports inside functions
  (`dispatcher.play_schedule_slot` imports `play_block`; `calendar/assembly.py`
  locally imports `ContentResolver`) indicate `logic`↔`engines` coupling that the
  layering claims to forbid.
- [x] ~~**`sys.path` manipulation in `testing/` and `example_channel.py`.**~~
  **Fixed 2026-09-08.** All eleven `sys.path.insert` lines are gone, along with
  the nine `import os` and three `import sys` that existed only to serve them.
  Everything under `testing/` runs as `python3 -m scripts.testing.<tool>`, which
  the README already documented; verified by running each one (`same_title_check`
  exits 1 on findings, which is its gate behaviour, not a failure).

  > **The shipped example was worse than this entry recorded.** It did not just
  > *teach* the hack, it shipped a broken one: its insert pointed at `scripts/`
  > (`'..'`) rather than the project root (`'../..'`), so running it as a loose
  > script raised `No module named 'scripts'` — the very error the line was
  > there to prevent. And `-m scripts.channels.example_channel` cannot work off
  > a real `etv_client` either, because `channels/__init__.py` imports all 16
  > channels eagerly and several import `etv_client` at module level, so the
  > package chain runs before the example can install a mock. A module inside a
  > package cannot fix its own package's import order. **`scripts/testing/run_example.py`**
  > is that one line of ordering, and the example's docstring now points at a
  > command that actually runs.

  *Original entry below.* Eleven
  modules under `scripts/testing/` and `channels/example_channel.py` open with
  `sys.path.insert(0, .../'..')` so they can be run as loose scripts. It works,
  but it means the package can be imported two different ways and the shipped
  example teaches the hack. `filler/` and `nfo/` were cleaned of this on
  2026-09-07 when they moved to `python3 -m scripts.filler.<tool>`; the same
  treatment applies here, and `testing/` already has the `__init__.py` it needs.
- [ ] **`Any` overuse.** `api`, `context`, and `boss` are typed `Any` in most
  helpers, erasing the value of the otherwise-good hints. Consider a `Protocol`
  for the ErsatzTV API and concrete `DayDirector` hints.
- [x] ~~**Duplication.** `ContentResolver.resolve` repeats the
  `auto_gen_<title>_<hash>` key-generation block across its `ContentItem` and
  `dict` branches — unify into one helper.~~ **Fixed 2026-09-08**: both
  branches call `_auto_gen_key(title, query)`. Verified behaviour-preserving —
  a `ContentItem` and a `dict` naming the same show still produce the same key
  (`auto_gen_magnum__p_i__af2418`), and two queries under one title still
  produce different ones.
- [x] ~~**Dead params.** `playout.wait_until_time` takes `context`/`logger` "for
  signature consistency" but ignores them.~~ **Closed 2026-09-08 by making
  them real, not by deleting them.** The signature parity turned out to be
  load-bearing: `fill_until_time` has the identical shape, *falls through to*
  `wait_until_time`, and the dispatcher picks between them by fill strategy —
  dropping the parameters would have broken that. Instead both now do
  something. `wait_until_time` logs the dead air it is about to create
  (`⏳ Dead air: N min to HH:MM`, at debug), measured from `context`. That is
  the one event this framework has repeatedly failed to notice: every gap the
  checkers ever found was a wait nobody saw being issued, because the build
  log recorded the block that ended and never the hole after it.
- [x] ~~**Readability.** `calendar/assembly.py:find_active_marathon` resolves the
  collection in one ~6-branch nested ternary — expand to an `if/elif` ladder.~~
  **Fixed 2026-09-08**: extracted as `_resolve_marathon_collection`, a four-case
  ladder with the precedence written down (collection picks for itself,
  MarathonSequence passes through whole because its order *is* the marathon,
  list is picked deterministically by date, anything else is already content).
- [x] ~~**Import side effect.** `settings.py` runs `os.makedirs(LOG_DIR)` at import
  time; it will raise on a read-only filesystem. Defer to first log write.~~
  **Fixed 2026-09-08.** `core/logger.py` is the only consumer of `LOG_DIR`, so
  the `mkdir` moved there, inside the `try/except` that already handles an
  unusable log path. Importing `scripts.settings` — which sits under every
  module in the framework — no longer touches the disk at all, and the now-unused
  `import os` went with it. Verified both directions: a missing nested log
  directory is still created on the first write.
