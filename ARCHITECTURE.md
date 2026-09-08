# ErsatzTV Scheduling Framework - Architecture Reference

## Overview

A declarative, feature-rich scheduling system for ErsatzTV that enables professional-grade broadcast programming with minimal code. Channels are defined as pure configuration (60-130 lines), while all complexity lives in a reusable framework.

---

## Directory Structure
```
scripts/
├── playout.py               # THE ENGINEER - ErsatzTV API utilities, circuit breaker, EPG
├── settings.py              # Global defaults & feature flags
├── requirements.txt         # (stdlib-only; etv_client ships inside ErsatzTV)
│
├── core/                    # THE FOUNDATION - Temporal primitives (no business logic)
│   ├── director.py          # DayDirector - Main temporal interface (labels, signals, RNG)
│   ├── registry.py          # HOLIDAYS, SEASONS, SEASONAL_RAMPS, FLOATING_RULES (data)
│   ├── states.py            # Date math: derive_labels, is_in_date_range, days_until/since
│   ├── signals.py           # Probability curves: get_parabolic_surge, season strength
│   ├── identity.py          # stable_hash() - process-stable RNG seeds (determinism)
│   └── logger.py            # ChannelLogger
│
├── logic/                   # THE BRAIN - Scheduling decisions
│   ├── models.py            # Dataclasses: Marathon, Fallback, Swap, Feather,
│   │                        #   CommercialBreak, ContentItem, ResolutionResult, profiles
│   ├── structures.py        # Collections (Random/Ordered/Weighted/Daily) + Block, Program
│   ├── triggers.py          # Trigger helpers (chance, when_has, combine, ...)
│   ├── factories.py         # Helpers for building Programs/collections (e.g. episode_list)
│   ├── profiles.py          # HOLIDAY_PROFILES (universal ramp logic)
│   │
│   ├── calendar/            # Time → schedule shape
│   │   ├── assembly.py      # assemble_day_schedule() + marathon→Block conversion
│   │   ├── holidays.py      # HolidayContext, with_holidays, get_holiday_target
│   │   ├── seasonal.py      # SeasonalBlock, resolve_seasonal_block
│   │   ├── timeslots.py     # Timeslot presets + expansion
│   │   └── triggers.py      # Calendar-aware trigger building blocks
│   │
│   └── resolution/          # target → playable content key
│       ├── pipeline.py      # resolve_content() (main pipeline) + injections + appointment math
│       ├── resolver.py      # ContentResolver - registers queries with ErsatzTV
│       ├── playback.py      # hour_in_window, boundary math
│       └── config_utils.py  # resolve_feature() cascade (Program > Block > Channel)
│
├── library/                 # THE VAULT - Content definitions
│   ├── sources.py           # MASTER_SOURCES - all Lucene queries
│   ├── queries.py           # Query builders, tag injection, parsing utilities
│   ├── filters.py           # SEASONAL_TAG_QUERIES, INJECTION_RULES
│   ├── branding.py          # Bumper/intro/outro definitions
│   ├── marathons.py         # Marathon content definitions
│   └── <genre>.py           # sitcoms, scifi, fantasy, detective, animation, british, ...
│
├── engines/                 # THE STRATEGIES - Playback behaviors
│   ├── blocks.py            # PlayoutSession, play_block, play_program (+ marathon blocks)
│   └── dispatcher.py        # play_schedule_slot, commercials, bumpers, fill/bridge
│
├── scheduling/              # ORCHESTRATION
│   ├── runner.py            # ScheduleRunner - the main daily loop ("THE ARCHITECT")
│   ├── config.py            # ScheduleConfig
│   └── pre_registration.py  # Pre-register all content before the loop
│
├── channels/                # THE PERSONALITIES - Channel configs (pure data)
│   ├── cartoon_network.py   # Kids programming with marathons
│   ├── detective.py         # Mystery/detective programming
│   └── sitcoms, scifi, eighties, british, classic_movies, ...
│
├── testing/                 # Simulator and checkers. All run as
│   │                        #   python3 -m scripts.testing.<tool>
│   ├── simulator.py         # Mock API + ChannelSimulator (auto-installs etv_client mock)
│   ├── run_example.py       # Simulate channels/example_channel.py (import ordering)
│   ├── visualize_week.py    # CLI weekly schedule visualizer (one channel)
│   ├── collision_report.py  # CLI cross-channel lineup report (all channels)
│   ├── same_title_check.py  # CLI same-title-at-the-same-hour check (all channels)
│   ├── same_show_check.py   # CLI same-show check, incl. different keys for one show
│   ├── validate_titles.py   # CLI check that every scheduled title resolves
│   ├── key_census.py        # CLI check that every registry key resolves (offline)
│   ├── key_airing_check.py  # CLI check that a scheduled key actually airs (live guide)
│   ├── continuity_check.py  # CLI dead-air/gap finder against the live XMLTV export
│   ├── library_census.py    # CLI census of the media on disk -> reference/library-*
│   ├── media_inventory.py   # CLI registry inventory -> reference/registry-inventory.md
│   ├── metadata_census.py   # CLI metadata coverage census
│   ├── list_content.py      # CLI content key lister
│   ├── scan_library.py      # CLI media source scanner
│   └── test_*.py            # Smoke / scenario / refactor tests
│
├── filler/                  # WORKSTATION TOOLS - acquire, cut and tag interstitials.
│   │                        #   Not imported by the scheduler; needs ffmpeg/ffprobe.
│   │                        #   python3 -m scripts.filler.<tool>
│   ├── scout_archive.py     # Find candidate reels
│   ├── fetch_archive.py     # Download them
│   ├── split_reels.py       # Cut a reel into segments
│   ├── split_promos.py      # Cut promos out of a segment
│   ├── analyze_spots.py     # Transcribe + classify spots (faster-whisper)
│   ├── transcript_gate.py   # Filter on transcript content
│   ├── dedupe_bumpers.py    # Perceptual-hash de-duplication
│   ├── contact_sheet.py     # Visual review sheets
│   ├── file_us_commercials.py, recategorize_commercials.py
│   ├── sort_bumper_positions.py, sync_interstitials.py
│   └── generate_filler_nfo.py
│
└── nfo/                     # Sidecar metadata tools (needs lxml)
    └── normalize_tag_case.py
```

> **Naming note.** `schedule.py` is now `scheduling/runner.py` (class
> `ScheduleRunner`, entry point `run_daily_schedule`). The old flat `logic/*.py`
> files moved under `logic/calendar/` and `logic/resolution/`, and the marathon
> and sequential engines were folded into `engines/blocks.py` — a marathon is
> converted to an ordinary `Block` before it reaches an engine, and Appointment
> TV is episode math in the resolution pipeline. The prose below was reconciled
> to these names on 2026-09-08.

---

## Architectural Layers

### Layer 1: Core (Foundation)
**Purpose:** Temporal primitives with zero business logic  
**Dependencies:** None  
**Principle:** "What is the current temporal state?"

- `director.py` - Temporal interface for querying date/time state
- `registry.py` - Static data definitions (holidays, seasons)
- `states.py` - Pure date math functions
- `signals.py` - Pure probability curve mathematics

### Layer 2: Logic (Decision Making)
**Purpose:** Scheduling features built on core primitives  
**Dependencies:** Core  
**Principle:** "What should we do about it?"

- `calendar/holidays.py` - Holiday detection and content overrides
- `calendar/seasonal.py` - Seasonal content blending strategies
- `calendar/timeslots.py` - Time block definitions and expansion
- `calendar/assembly.py` - Day shape: `assemble_day_schedule()` + marathon->Block
- `profiles.py` - Universal holiday ramp profiles
- `triggers.py` - Composable event trigger system
- `resolution/pipeline.py` - Content resolution pipeline (THE BRAIN)
- `resolution/playback.py` - Playback strategies and utilities
- `models.py` - Dataclass definitions for config objects
- `structures.py` - Collections + the `Block`/`Program` containers
- `factories.py` - `annual_show()` and friends

### Layer 3: Library (Content Organization)
**Purpose:** Content definitions and resolution  
**Dependencies:** Core  
**Principle:** "What content exists and how do we access it?"

- `sources.py` - All Lucene queries in MASTER_SOURCES dict
- `queries.py` - Query builders, tag injection, parsing utilities
- `filters.py` - `SEASONAL_TAG_QUERIES`, `INJECTION_RULES`
- `<genre>.py` - Blocks and collections per genre (sitcoms, horror, animation, ...)

> Collections and `Block`/`Program` live in `logic/structures.py`, not here;
> the resolver that registers keys with ErsatzTV is
> `logic/resolution/resolver.py`.

### Layer 4: Engines (Complex Behaviors)
**Purpose:** Specialized playback behaviors  
**Dependencies:** Core, Logic, Library  
**Principle:** "How do we execute complex programming?"

- `blocks.py` - `PlayoutSession`, `play_block`, `play_program`. Branded blocks
  with intro/outro/bumpers, and marathons -- which arrive here already converted
  to ordinary Blocks, so there is no separate marathon engine.
- `dispatcher.py` - `play_schedule_slot`, commercials, bumpers, fill/bridge

> Appointment TV has no engine either: the episode math is
> `logic/resolution/pipeline.py::resolve_scheduled_content` and `play_program`
> executes it.

### Layer 5: Orchestration (Top Level)
**Purpose:** Main execution loop  
**Dependencies:** All layers  
**Principle:** "Coordinate everything to build a schedule"

- `scheduling/runner.py` - `ScheduleRunner`, the main daily loop; entry point
  `run_daily_schedule()`
- `scheduling/config.py` - `ScheduleConfig`
- `scheduling/pre_registration.py` - Pre-register all content before the loop
- `playout.py` - API utilities, circuit breaker, EPG grouping

### Layer 6: Configuration (Channels)
**Purpose:** Declarative channel definitions  
**Dependencies:** All layers  
**Principle:** "Pure data configuration, minimal logic"

- Each channel is 60-130 lines of pure configuration
- No complex logic - just schedules, marathons, overrides

---

## Dependency Graph
```
core/
  ↓
logic/ ──┐
  ↓      │
library/ │
  ↓      │
engines/ ←┘
  ↓
scheduling/
  ↓
channels/
```

**Rules:**
- Core has NO dependencies
- Logic depends only on Core
- Library depends only on Core
- Engines depend on Core, Logic, Library
- Channels depend on everything but contain NO logic

---

## Key Files Deep Dive

### `scheduling/runner.py` - THE ARCHITECT
**Responsibility:** Orchestrate daily schedule execution
**Key API:**
- `ScheduleRunner(api, context, build_id, config)` - the loop object
- `ScheduleRunner.run()` - executes one build
- `run_daily_schedule(api, context, build_id, config)` - the entry point a
  channel's `build_playout()` calls; wraps the two above

**Flow:**
1. Detect day type (weekday/Saturday/Sunday)
2. Check for marathon takeovers
3. For each hour:
   - Find matching time window
   - Resolve content (day-of-week → seasonal → holiday → variants)
   - Play content
   - Handle circuit breaker
   - Handle filler if needed


### `core/director.py` - THE INTERFACE
**Responsibility:** Main temporal intelligence interface. `DayDirector` is the
one object that answers "what day is it, and what does that imply" — every
trigger and every probabilistic choice goes through it.
**Key Methods:**
- `DayDirector(context)` - constructed once per build from the playout context
- `pick(key, items)` / `pick_weighted(key, items_with_weights)` - deterministic
  daily selection (same date → same choice, across processes)
- `roll(probability, key)` - deterministic dice
- `has` / `has_any` / `has_all` / `had` - label tests
- `window(event, before, after)`, `days_until`, `days_since`
- `signal(event, window, hangover)` - the ramp strength curve
- `season_vibe` - Current seasonal blend (WINTER/SPRING/SUMMER/FALL)

**Labels Auto-Generated:**
- Day names: MONDAY, TUESDAY, WEDNESDAY, etc.
- WEEKEND, WEEKDAY, WEEKDAY_A, WEEKDAY_B
- Seasons: WINTER, SPRING, SUMMER, FALL
- Seasonal periods: WINTER_PEAK, WINTER_ACTIVE, etc.
- Holidays: HALLOWEEN, CHRISTMAS, THANKSGIVING, etc.
- Dayparts: PRIMETIME, LATE_NIGHT, etc.
- Positional: FIRST_MONDAY, SECOND_SATURDAY, etc.


### `logic/resolution/pipeline.py` - THE BRAIN
**Responsibility:** Resolve schedule targets to final content keys
**Key Functions:**
- `resolve_content(target, boss, holiday_ctx, config, resolver, logger)` - the
  full pipeline; returns a `ResolutionResult` carrying either a `key` or a
  `wrapper` (Block/Program/Fallback) plus the `source` that won
- `apply_injections(...)` - seasonal + thematic tag injection over a resolved key
- `extract_primary_content(...)` - reach the underlying key through a wrapper
- `resolve_scheduled_content(program, current_date)` - Appointment TV episode
  math: which episode of a dated run airs today, or `None` off-frequency

**Resolution Order (ENFORCED):**
1. Inner dict resolution (day-of-week labels)
2. Fallback to "default" if dict remains
3. SeasonalBlock resolution (probabilistic blending)
4. Holiday override application
5. Seasonal block variant resolution (string references)
6. Final resolver.resolve() to content key

**Example:**
```python
# Input: Schedule target (could be nested dict with overrides)
target = {
    "default": SeasonalBlock(
        base=collections.CLASSIC_TV,
        seasonal={"WINTER": collections.COZY_TV}
    ),
    "TUESDAY": collections.MOVIE_NIGHT,
    "halloween": collections.HALLOWEEN_TV
}

# Output: Final content key string
result = resolve_content(target, boss, holiday_ctx, config, resolver, logger)
final_key = result.resolved_content
# → "halloween_tv" (if Halloween active)
# → "movie_night_tv" (if Tuesday and no holiday)
# → "cozy_tv" (if winter peak and not Tuesday)
# → "classic_tv" (fallback)
```

---

### `library/sources.py` - THE SOURCE OF TRUTH
**Responsibility:** All content query definitions  
**Key Structure:**
```python
MASTER_SOURCES = {
    # Simple queries
    "simpsons_tv": 'show_title:"The Simpsons"',
    
    # With order
    "friends_tv": {
        "query": 'show_title:"Friends"',
        "order": "Chronological"
    },
    
    # Marathon metadata
    "dbz_saiyan_saga_tv": {
        "title": "DBZ: Saiyan Saga",
        "description": "Goku faces the invading Saiyan warriors.",
        "query": 'show_title:"Dragon Ball Z" AND season_number:1 AND episode_number:[21 TO 36]',
        "order": "Chronological"
    }
}
```

---

### `logic/structures.py` - THE ORGANIZERS
**Responsibility:** Smart collection objects, plus the `Block` and `Program`
containers themselves.
**Key Classes:**
- `RandomCollection` - Random selection each time
- `OrderedCollection` - Cycles through list in order
- `DailyOrderedCollection` - Cycles, but resets to the top each day
- `WeightedCollection` - Weighted random selection
- `MarathonSequence` - An ordered run whose order *is* the marathon
- `Block`, `Program` - the schedulable containers

> `Block.items` must be a list or a collection, **never a bare content key**.
> A string cannot be iterated, so `items="some_key"` plays nothing at all —
> the constructor rejects it and names the fix.

**Example:**
```python
DBZ_SAGAS = OrderedCollection([
    "dbz_saiyan_saga_tv",
    "dbz_frieza_saga_tv",
    "dbz_cell_games_tv"
])

# First call returns "dbz_saiyan_saga_tv"
# Second call returns "dbz_frieza_saga_tv"
# Etc.
```

---

### `engines/blocks.py` - THE MARATHON RUNNER
**Responsibility:** Execute multi-episode marathons. There is no separate
marathon engine: `logic/calendar/assembly.py` converts an active `Marathon`
into an ordinary `Block` of `Program`s (`_convert_marathon_to_block`), and
`play_block` runs it like any other block.
**Key Functions:**
- `find_active_marathon(config, boss, holiday_ctx)` - which marathon, if any
- `_convert_marathon_to_block(...)` - marathon → Block
- `play_block(session, item, start_hour, end_hour, ...)` - runs it

**Features:**
- Auto-detects starting episode from query
- EPG grouping with custom title
- Time-bounded execution
- Episode counting and completion detection
- Safety checks (circuit breaker)

**Flow:**
1. Get metadata (title, description)
2. Register content with ErsatzTV
3. Extract starting episode from query
4. Skip to starting episode
5. Start EPG group (TV guide branding)
6. Play episodes in loop until time limit or exhaustion
7. Stop EPG group
8. Return updated context

---

### Appointment TV - THE SCHEDULER
**Responsibility:** Execute date-based sequential programming. Also has no
engine of its own. A `Program` carries a `scheduling` dict (built by
`logic/factories.py::annual_show`), `logic/resolution/pipeline.py::resolve_scheduled_content`
works out which episode is due, and `engines/blocks.py::play_program` plays it.
**Key Functions:**
- `annual_show(...)` - builds the scheduled `Program` (Broadcast or Contiguous mode)
- `resolve_scheduled_content(program, current_date)` - episode due today, or `None`
- `play_program(...)` - plays it, falling back to the `reruns` bed when `None`

**Features:**
- Date-based season resolution
- Automatic looping for long-term schedules
- Off-season fallback content
- Daily reset for anchor slots (DailyOrderedCollection)

## Configuration Objects

### ScheduleConfig
```python
ScheduleConfig(
    schedules={...},                    # Required: Dict of day types to hourly schedules
    marathons=[...],                    # Optional: List of Marathon objects
    seasonal_blocks={...},              # Optional: Dict of block variants
    timeslot_preset="default",          # Optional: "default", "kids", "movies", or custom dict
    custom_timeslots={...},             # Optional: Override specific timeslots
    global_holiday_overrides={...},     # Optional: Dict of holiday to content
    holiday_schedules={...},            # Optional: Dict of holiday to full schedule
    block_profiles={...},               # Optional: Dict of slot profiles (or HOLIDAY_PROFILES)
    filler_content=None,                # Optional: Filler for hour boundaries
    log_prefix="[TV]",                  # Optional: Log prefix
    logger=None,                        # Optional: ChannelLogger instance
    fallback_content=None               # Optional: Fallback if no schedule match
)
```

### Marathon (Dataclass)
```python
Marathon(
    name="DBZ Marathon",                # Display name
    trigger=with_probability(0.05),     # Trigger function
    collection=collections.DBZ_SAGAS,   # Content to play
    hours=(10, 24),                     # Time window (10am-midnight)
    priority=1                          # Priority (higher = more important)
)
```

### SeasonalBlock
```python
SeasonalBlock(
    base="classic_movies",              # Evergreen content
    seasonal={                          # Seasonal variants
        "WINTER": feather("winter_movies", 0.4),
        "SUMMER": swap("summer_movies")
    },
    blend_ratio=1.0                     # Default max proportion
)
```

---

## Data Flow Examples

### Example 1: Simple Schedule Entry
```
SCHEDULES = {"WEEKDAY": {"prime": collections.FOX_PRIMETIME}}
         ↓
run_daily_schedule() detects hour=19 (7pm)
         ↓
Finds matching window (19, 22) → "prime"
         ↓
resolve_schedule_target(collections.FOX_PRIMETIME, ...)
         ↓
resolver.resolve(collections.FOX_PRIMETIME)
         ↓
collections.FOX_PRIMETIME.pick() → "simpsons_tv"
         ↓
resolver checks MASTER_SOURCES["simpsons_tv"]
         ↓
Registers with ErsatzTV if needed
         ↓
Returns "simpsons_tv"
         ↓
play_item(api, build_id, "simpsons_tv")
```

### Example 2: Complex Resolution
```
target = {
    "default": SeasonalBlock(base="classic", seasonal={"WINTER": "cozy"}),
    "TUESDAY": "movies",
    "halloween": "scary"
}
         ↓
resolve_schedule_target(target, boss, holiday_ctx, ...)
         ↓
Step 1: Check inner dict for day-of-week labels
  boss.has("TUESDAY")? → Yes
  target = "movies"
         ↓
Step 2: Check if None → No, skip
         ↓
Step 3: Is SeasonalBlock? → No, skip
         ↓
Step 4: Apply holiday overrides
  get_holiday_target(holiday_ctx, "movies", global_overrides)
  holiday_ctx.is_active("halloween")? → Yes
  global_overrides["halloween"] exists? → Yes
  target = "halloween_movies"
         ↓
Step 5: Check seasonal_blocks dict → Not found, skip
         ↓
Step 6: resolver.resolve("halloween_movies")
         ↓
Returns "halloween_movies"
```

### Example 3: Marathon Trigger
```
MARATHONS = [Marathon(
    trigger=with_probability(0.05, "dbz"),
    collection=collections.DBZ_SAGAS,
    hours=(10, 24)
)]
         ↓
run_daily_schedule() checks marathons
         ↓
trigger(boss) → boss.roll(0.05, "dbz")
         ↓
Deterministic RNG based on date: seed = "2026-01-14::roll:dbz"
         ↓
Returns True (5% chance, succeeded today)
         ↓
marathon_to_run = this marathon
         ↓
At 10am, hour_in_window(10, 10, 24)? → Yes
         ↓
collection.pick() → "dbz_saiyan_saga_tv"
         ↓
run_marathon(api, ..., "dbz_saiyan_saga_tv", ...)
         ↓
Plays all episodes from 10am until midnight or exhaustion
         ↓
Returns to regular schedule
```

---

## Design Principles

### 1. Separation of Concerns
- **Core** = State ("What is?")
- **Logic** = Decisions ("What should?")
- **Engines** = Behaviors ("How to?")
- **Channels** = Configuration ("What when?")

### 2. Declarative over Imperative
Channels are 90% data, 10% logic. All complexity hidden in framework.

### 3. Composability
Features combine cleanly:
- `with_holidays(SeasonalBlock(...), halloween=...)`
- `combine(when_has("SATURDAY"), with_probability(0.25))`

### 4. Determinism
Same date always produces the same schedule, **including across process restarts**
(rebuilding the container does not change the output). This is enforced by:

- **Date-seeded RNG.** All randomness flows through `DayDirector`, seeded by
  `date + key`. A fresh `DayDirector` is created per day, so RNG state never
  leaks between days.
- **Content-stable seeds, not `id()`.** Collections and list picks seed their RNG
  via `core/identity.stable_hash(...)` (a hash of the items), never a memory
  address. Memory addresses change every run, so seeding on `id()` would silently
  break reproducibility — `stable_hash` does not.
- **Date-anchored sequential collections.** `OrderedCollection` derives its
  position from `(date − epoch)` rather than a free-running counter, so a given
  calendar date maps to a fixed position and the rotation "moves on" while the
  server is offline (matching the appointment-TV philosophy below). The epoch is
  `settings.DEFAULT_APPOINTMENT_START_DATE`.
- **Per-day reset of transient state.** `RandomCollection` resets its no-repeat
  set each day, so a day's picks depend only on that date — not on how many picks
  happened on earlier days.

> **Trade-offs of true determinism:** `RandomCollection`'s no-repeat memory is
> per-day only (cross-day no-repeat is incompatible with "same date → same
> output"). An `OrderedCollection` used for *strict* episode order inside a
> multi-item block can repeat one item across a day boundary — use the
> calendar-driven `scheduling=` (Appointment TV) path for strict sequencing.

### 5. Progressive Enhancement
Start simple, add features as needed:
- Basic: Static schedules
- +Overrides: Day-of-week variants
- +Seasons: Seasonal blending
- +Holidays: Holiday takeovers
- +Marathons: Special events
- +Blocks: Branded programming

### 6. Fail-Safe
Multiple fallback layers:
- Fallback content if no schedule match
- Circuit breaker if content stalls
- Default values in all configs

---

## 8. Appointment TV (Sequential Scheduling)

### What It Is
A system for simulating "Event Television" where shows premiere on specific dates and air sequentially (weekly or daily).

**Example:**
> "Lost Season 1 premieres in Fall 2026. Season 2 premieres in Fall 2027."

### What It Is Not
- It is **not** a watch-state tracker. It does not care if *you* have watched Episode 3.
- It is **not** a playlist. It is a calendar calculation.

### Core Principles

#### 1. Calendar-Driven (Absolute Time)
The episode to play is calculated mathematically from the current date.

```python
# Logic:
weeks_since_premiere = (current_date - premiere_date).days // 7
episode_to_play = weeks_since_premiere + 1
```

**Why?**
If your server is offline for a week, the schedule "moves on" without you, just like real broadcast TV. When you tune back in, you've missed an episode. This preserves the global timeline.

#### 2. Statelessness
The system stores **zero state** about what played last week.
- **Pros:** Robust. Rebuilding the container doesn't break the schedule.
- **Cons:** Requires precise date math.

#### 3. Holiday Exclusion
Appointment Blocks are **immune** to holiday overrides.
- **Why?** Narrative continuity. You don't want a random "Halloween Special" interrupting the serialized plot of *Breaking Bad* or *Lost*.
- **Implementation:** The `AppointmentBlock` engine bypasses the standard resolution pipeline where holiday injection happens.

#### 4. Frequency Gates the Airing, Not Just the Pace
`frequency` says *which days the show airs*, and is enforced. On any other day
`resolve_scheduled_content()` returns `None` and the slot falls through to the
program's `reruns` bed.

```python
annual_show(
    show_title="Yellowstone",
    episodes_per_season=[9, 10, 10],
    start_date=date(2026, 1, 5),
    frequency=["FRIDAY"],       # airs Fridays -- and only Fridays
    reruns="modern_western_tv", # every other night in this slot
)
```

**This used to only pace, not gate.** `frequency` controlled how fast the
episode index advanced, so a show declared `["FRIDAY"]` inside a block that
ran seven nights aired the *same episode* all seven of them — a premiere that
premieres every night. Channels worked around it by day-gating the block
instead, which is no longer necessary (though it does no harm).

Two details worth knowing:

- **Only an explicit day list gates.** `"weekly"` infers its day from the
  season window start, which in Broadcast Mode is a seasonal *peak date* the
  caller never chose — gating on that would silently confine a show to
  whatever weekday the ramp table landed on. `"daily"` means every day, so
  gating it is a no-op.
- **The gate reads the real broadcast date**, not the looped one. When a
  looping schedule wraps, the date is rewritten back into the season window
  and lands on an arbitrary weekday; testing *that* date drops a strip from
  days it genuinely airs.

#### 5. Loop Restart Depends on the Mode
`loop_restart_season` defaults to the premiere season in Broadcast Mode, and to
`False` — restart immediately — whenever `start_date` was used. A contiguous
strip has no premiere season to wait for; taking one meant a weekday strip that
finished its run in June went dark until mid-September.

#### 6. Filler Drift
When a show is off-season, the slot is filled by a `SeriesRelay` (a rotating list of filler shows).

**Behavior:**
- Filler shows (e.g., *Seinfeld*) track their own progress based on a fixed anchor date.
- They do **not** reset when the main show returns.
- **Result:** If *Lost* runs for 25 weeks, *Seinfeld* pauses. When *Lost* ends, *Seinfeld* picks up exactly where it left off (e.g., Episode 42), ensuring you eventually see every episode of the filler, even if it takes years.

### Data Structures

**AppointmentBlock:**
```python
LOST_BLOCK = annual_show(
    show_title="Lost",
    seasons=6,
    premiere_year=2026,
    premiere_season="FALL",
    reruns=LOST_FILLERS,  # SeriesRelay
    loop=True             # Loops back to S1 in 2032
)
```

---

## Performance Considerations

### Pre-Registration
All content is registered with ErsatzTV BEFORE the schedule loop begins. This prevents repeated API calls.

### Deterministic RNG
Using date-seeded RNG means no state persistence needed. Same schedule regenerates identically.

### Content Resolution Caching
ContentResolver tracks `active_keys` to avoid duplicate registrations.

---

## Testing Strategy

### Unit Testing
- Core functions are pure (easy to test)
- Logic functions use dependency injection (mock DayDirector)
- Engines can be tested with mock API

### Integration Testing
Use `testing/simulator.py` to test channels without ErsatzTV:
```python
from scripts.testing.simulator import test_channel
from datetime import date

# Test Halloween schedule
test_channel(cartoon_network, date(2026, 10, 31))
```

### Validation
- Channel files have minimal logic (hard to break)
- Framework handles edge cases
- Type hints + dataclasses catch config errors early

---

## Extension Points

### Adding New Features

**New Holiday:**
1. Add to `core/registry.py` HOLIDAYS
2. Add signal in `logic/holidays.py` if needed
3. Use in channels with `with_holidays()`

**New Trigger Type:**
1. Add class to `logic/triggers.py`
2. Inherit from `Trigger` base class
3. Implement `__call__(self, boss)`

**New Engine:**
1. Create file in `engines/`
2. Follow pattern: `run_<name>(api, build_id, context, ...)`
3. Return updated context

**New Channel:**
1. Copy `channels/cartoon_network.py` as template
2. Define schedules, marathons, blocks
3. Configure ScheduleConfig
4. Done!

---

## Troubleshooting

### "Content not playing"
1. Check if key exists in MASTER_SOURCES
2. Verify query syntax (Lucene)
3. Check ErsatzTV logs for "invalid content"
4. Ensure content is tagged/exists in Jellyfin

### "Schedule not changing"
1. Verify date ranges in registry
2. Check trigger logic (add logging)
3. Test with simulator at specific dates
4. Confirm labels with `boss.debug()`

### "Infinite loop / Circuit breaker"
1. Content source exhausted (add more)
2. Invalid query (returns no results)
3. Time advancement issue (check play_item)

### "Wrong content playing"
Resolution order may be unexpected:
1. Add logging to `resolve_target`
2. Check each resolution step
3. Verify priority (holiday > day-of-week > seasonal > default)

---

**Total Framework:** ~2,500 lines  
**Total Channels:** ~100 lines each  
**Ratio:** 25:1 framework to channel code

This means adding a new channel is ~100 lines vs ~2,500 lines if built from scratch.

---

## Version History

- **v1.0** - Initial framework with basic scheduling
- **v1.5** - Added seasonal blending and holiday overrides
- **v2.0** - Marathon system with EPG grouping
- **v3.0** - Current: Full feature set, production-ready

---

## Future Enhancements

**Potential additions:**
- Rotation tracking across days (prevent recent repeats)
- "On this day" anniversary programming
- Stunt programming weeks (Shark Week, etc.)
- Graphics engine integration (overlays, bugs)
- Pre-roll/post-roll support
- Content pacing strategies
- Advanced filler management

**Not planned:**
- Web UI (use ErsatzTV's interface)
- Database (stateless by design)
- Multi-channel coordination (each channel independent)