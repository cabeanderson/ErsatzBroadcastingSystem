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

## Open

### 🟠 Correctness / robustness

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
