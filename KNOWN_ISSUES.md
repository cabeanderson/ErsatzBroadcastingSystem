# Known Issues & Tech Debt

A living checklist of findings from the codebase review. Severity: 🔴 high ·
🟠 medium · 🟡 low. Resolved items are kept (struck through) for history.

## Resolved

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

## Open

- [ ] 🟠 **Must See Thursday replays each episode two or three times a night.**
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

- [ ] **`frequency` paces an appointment, it does not gate the airing.**
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

- [ ] **`circuit_breaker` never resolves `fallback_content`.**
  `playout.circuit_breaker` hands `config.fallback_content` straight to
  `play_item`, which requires a string key — so a `Block` or a Collection logs
  "play_item received non-string content", advances nothing, and the breaker
  still reports "✅ Fallback succeeded". Cartoon Network now passes a key
  (`"animated_classic_tv"`); **nick, disney, detective and sitcoms all still
  pass Blocks or Collections** and have a fallback that cannot fire. Fix either
  end: resolve in the breaker, or make `ScheduleConfig` reject a non-key
  fallback at construction rather than at the worst possible moment.

- [ ] **A Contiguous-Mode strip goes dark waiting for autumn.**
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

- [ ] **Unescaped title interpolation.** `dispatcher.play_smart_bumper` builds
  `tag:"{title}"` and `pipeline`/`queries.inject_tag` concatenate `tag_query`
  directly, unlike the `queries.py` builders which use `_escape_quotes`. A title
  containing a quote breaks the query. (Operator-authored input, so robustness —
  not security.)
- [ ] **Doc reconciliation (partial).** `ARCHITECTURE.md` structure + determinism
  sections are current, but the "Key Files Deep Dive", "Data Flow Examples", and
  "Configuration Objects" prose still use historical names
  (`resolve_schedule_target`, `collections.py`, `run_marathon`, etc.).
  `CONCEPTS.md` and `IMPORTS.md` likely drifted too — audit and update.
- [ ] **Thin automated tests.** `testing/test_comprehensive.py` is print-based
  (no asserts). `test_scenarios.py` does use `unittest`. Add assertion coverage
  for date math (leap years, year wraparound), determinism (same date → same
  output across runs), and the Appointment-TV episode math in
  `logic/resolution/pipeline.py`.
- [ ] **Circular-dependency smell.** Runtime imports inside functions
  (`dispatcher.play_schedule_slot` imports `play_block`; `calendar/assembly.py`
  locally imports `ContentResolver`) indicate `logic`↔`engines` coupling that the
  layering claims to forbid.
- [ ] **`Any` overuse.** `api`, `context`, and `boss` are typed `Any` in most
  helpers, erasing the value of the otherwise-good hints. Consider a `Protocol`
  for the ErsatzTV API and concrete `DayDirector` hints.
- [ ] **Duplication.** `ContentResolver.resolve` repeats the
  `auto_gen_<title>_<hash>` key-generation block across its `ContentItem` and
  `dict` branches — unify into one helper.
- [ ] **Dead params.** `playout.wait_until_time` takes `context`/`logger` "for
  signature consistency" but ignores them.
- [ ] **Readability.** `calendar/assembly.py:find_active_marathon` resolves the
  collection in one ~6-branch nested ternary — expand to an `if/elif` ladder.
- [ ] **Import side effect.** `settings.py` runs `os.makedirs(LOG_DIR)` at import
  time; it will raise on a read-only filesystem. Defer to first log write.
