# Core Concepts & Data Flows

Understanding how the scheduling framework thinks and operates.

---

## The Big Picture
```
Channel Config → Schedule Loop → Content Resolution → ErsatzTV API → Playout
     (Data)         (Logic)          (Translation)       (Execution)
```

**Metaphor:** You're programming a TV station that knows about time, holidays, and seasons.

---

## 1. Temporal Intelligence (The Calendar System)

### Labels
**Concept:** Every datetime has a set of string labels that describe it.

**Examples** — the full set `derive_labels` returns, not a selection:
```python
# January 14, 2026 (Wednesday), checked at 20:00
labels = {
    "WEDNESDAY",           # Day of week
    "WEEKDAY",             # Weekday grouping
    "WEEKDAY_A",           # Mon/Wed/Fri group
    "WINTER",              # Meteorological season
    "WINTER_PEAK",         # Seasonal content plateau
    "PRIMETIME",           # Daypart, from the hour
    "SECOND_WEDNESDAY",    # Positional
    "JANUARY",             # Month
    "YEAR_OF_2_0", "YEAR_OF_3_1",   # Year-cycle phase
    "YEAR_OF_4_2", "YEAR_OF_5_1",
}

# October 31, 2026 (Saturday), checked at 20:00
labels = {
    "SATURDAY",
    "WEEKEND",
    "FALL",
    "HALLOWEEN",           # Static holiday
    "FIFTH_SATURDAY",
    "OCTOBER",
    "PRIMETIME",
    "YEAR_OF_2_0", "YEAR_OF_3_1",
    "YEAR_OF_4_2", "YEAR_OF_5_1",
}
```

**Usage:**
```python
boss = DayDirector(context)
if boss.has("SATURDAY"):
    # It's Saturday
if boss.has_any("HALLOWEEN", "CHRISTMAS"):
    # It's a major holiday
```

**The year-cycle labels are the only ones that tell one year from the next.**
Every other label above is a function of month, day, weekday and hour, so two
Wednesdays two years apart are otherwise indistinguishable — which meant any
block keyed on labels repeated identically every year, and a month-keyed
rotation was a twelve-slot loop no matter how much content sat behind it.

`YEAR_OF_<n>_<r>` reads "year `r` of an `n`-year cycle", where `r` is
`year % n`. Phase is absolute rather than anchored to a start date, so a
rotation cannot drift and two channels on the same cycle length stay in step.
`registry.YEAR_CYCLES` sets which lengths get a label; 2, 3, 4 and 5 today.

You rarely name one of these directly — `multiyear_rotation()` builds the
dict for you. See **Rotations** below.

---

### Signals
**Concept:** Gradual ramps from 0.0 to 1.0 as you approach/leave events.

**Types:**
1. **Parabolic Surge** - Builds slowly, then explodes near event
2. **Decay Signal** - Drops rapidly after event
3. **Linear Ramp** - Steady transition

**Example:**
```python
# Halloween signal (7-day window)
Oct 24: 0.0  (too far)
Oct 25: 0.25 (entering window)
Oct 28: 0.64 (building)
Oct 30: 0.92 (almost there)
Oct 31: 1.0  (HALLOWEEN!)
Nov 1:  0.0  (over)

# Christmas signal (21-day window)
Dec 4:  0.0
Dec 10: 0.16
Dec 15: 0.36
Dec 20: 0.64
Dec 24: 0.96
Dec 25: 1.0
Dec 26: 0.75 (hangover mode)
```

**Usage:**
```python
boss = DayDirector(context)
halloween_strength = boss.signal("HALLOWEEN", window=7)

if halloween_strength > 0.7:
    # Strong Halloween vibe - use spooky content
```

---

### Deterministic Selection
**Concept:** Same date always produces same random result.

**How It Works:**
```python
# Hashed from: "2026-01-14::marathon"  (SHA-256 -> uniform float)
boss.roll(0.05, "marathon")  # 5% daily chance

# Always returns same result for Jan 14
# Different result for Jan 15
# Same result again on Jan 14, 2027
```

**Why This Matters:**
- Schedule is reproducible
- No state to save
- Testing is predictable
- Rebuild produces identical schedule

---

## 2. Content Organization

### Three-Level System
```
Collection (Smart Playlist)
    ↓
Content Key (String Identifier)
    ↓
Source Query (Lucene Search)
```

**Example:**
```python
# Level 1: Collection
DBZ_SAGAS = OrderedCollection([
    "dbz_saiyan_saga_tv",
    "dbz_frieza_saga_tv"
])

# Level 2: Content Key
"dbz_saiyan_saga_tv"

# Level 3: Source Query
MASTER_SOURCES = {
    "dbz_saiyan_saga_tv": {
        "query": 'show_title:"Dragon Ball Z" AND season_number:1 AND episode_number:[21 TO 36]',
        "order": "Chronological"
    }
}
```

**Flow:**
```python
# In schedule
target = collections.DBZ_SAGAS

# Resolution
key = target.pick()  # → "dbz_saiyan_saga_tv"

# Registration
query = MASTER_SOURCES[key]["query"]
api.add_search(build_id, ContentSearch(key=key, query=query, order="Chronological"))

# Playback
api.add_count(build_id, PlayoutCount(content=key, count=1))
```

---

### Collection Types

**RandomCollection:**
```python
SITCOMS = RandomCollection([
    "seinfeld_tv",
    "friends_tv",
    "frasier_tv"
])

# Each pick() returns random item
```

**OrderedCollection:**
```python
WEEKLY_ROTATION = OrderedCollection([
    "monday_show",
    "tuesday_show",
    "wednesday_show"
])

# First pick() returns monday_show
# Second pick() returns tuesday_show
# Cycles back after reaching end
```

**WeightedCollection:**
```python
MOVIES = WeightedCollection([
    ("blockbuster", 0.5),    # 50% chance
    ("indie_film", 0.3),     # 30% chance
    ("classic", 0.2)         # 20% chance
])
```

### Rotations

**Concept:** a slot whose content changes on a calendar period rather than on
every play — a decade a month, a director a month, a shelf a year.

A rotation is not a collection type. It is a plain dict keyed on labels, which
the resolution pipeline already unwraps, so a rotation can go anywhere a block
or a content key can. Two factories build them:

```python
from scripts.logic.factories import monthly_rotation, multiyear_rotation

DECADE_AFTERNOON = monthly_rotation(["90s_pure_movie", "00s_pure_movie",
                                     "10s_pure_movie", "20s_pure_movie"])
# Jan -> 90s, Feb -> 00s, Mar -> 10s, Apr -> 20s, May -> 90s, ...

DIRECTORS_CHAIR = multiyear_rotation([SPIELBERG, SCORSESE, ...36 items],
                                     start_year=2027)
# 2027 -> the first twelve, 2028 -> the next twelve, 2029 -> the last twelve
```

**Pick by how long you want the cycle to be, not by list length.**
`monthly_rotation` expresses at most a year and refuses more.
`multiyear_rotation` reaches five years — `registry.YEAR_CYCLES` — and
delegates downward below thirteen items, so it is the safe default for a list
that might grow.

Two properties worth knowing:

- **Cycle length is derived, not declared.** 13–24 items is a two-year
  rotation, 25–36 a three-year. A partly-filled final year repeats from the
  front of the list rather than going dark.
- **Phase is absolute** — year `r` of an `n`-year cycle is the year where
  `year % n == r` — so a rotation cannot drift the way an appointment anchored
  on a raw day count did. The cost is that the front of the list lands wherever
  the modulo puts it, which for a curated rotation matters; `start_year` pins
  it. Only the residue is used, so `2027` and `2030` are the same instruction
  for a three-year cycle.

Sizing is a real constraint and the factory cannot check it: a monthly
spotlight in a two-film prime slot gets roughly nine plays a month, so a list
shorter than that repeats within its own month. That may be exactly what you
want — a month-long season of one filmmaker — but decide it rather than
discover it.

---

### Shapes That Are Refused

Four configurations used to resolve perfectly and then play nothing — or play
less than they said. Each named real content, passed every offline checker, and
left the channel looking healthy with the block behind it never having run. All
four now raise where they are written, in the channel file, rather than failing
silently hours into a build.

**A `Block` iterates. A content key does not.**
```python
Block(name="Frieren Night", items="frieren_tv")            # ValueError

Block(name="Frieren Night", items=OrderedCollection(["frieren_tv"]))  # ✅ strip
Block(name="Frieren Night", items=["frieren_tv"])                     # ✅ plays once
```
A string is neither a list nor a collection, so the engine's first pick returns
`None`, which the loop reads as "exhausted": `0 items played`, no time
advanced, no warning. Pick the collection form for a strip — it keeps handing
the same key back for the whole slot — and the list form to play one item and
yield the rest.

**Both sides of a `Fallback` are bare keys.**
```python
Fallback(primary="eighties_music_videos", secondary=SOME_COLLECTION)  # ValueError
Fallback(primary="eighties_music_videos", secondary="eighties_action_tv")  # ✅
```
`play_with_fallback` hands them straight to `play_item`, which resolves
nothing — a wrapper is stringified into `"<RandomCollection object at 0x...>"`,
matches no content, and still reports success.

**`fallback_content` takes a key or a Collection, never a `Block`.**
```python
ScheduleConfig(..., fallback_content=SOME_BLOCK)          # ValueError
ScheduleConfig(..., fallback_content="horror_movie")      # ✅
ScheduleConfig(..., fallback_content=RandomCollection([...]))  # ✅
```
The circuit breaker plays a single content key. A Collection resolves down to
one; a Block is a container of slots with no single key to reach, so the
breaker would skip ahead instead and the channel would have a fallback that
could never fire.

**A year has twelve months, and `monthly_rotation` holds twelve items.**
```python
monthly_rotation([A, B, ... 36 items])           # ValueError
multiyear_rotation([A, B, ... 36 items])         # ✅ three-year cycle
```
This one did not play nothing — it played *less than it was told to*, which is
harder to notice. The returned dict has one key per month, so items 13 and
beyond could never be indexed and never aired, and the dict itself looked
perfectly well-formed. Be Kind Rewind ran eight directors for months while its
module was believed to hold more. `multiyear_rotation` delegates here below
thirteen items, so switching costs nothing.

> The shared lesson: **a gap is a loud failure, a fallback is a silent one.**
> When a misconfiguration can only show up as "the right thing never aired",
> the guard belongs at construction, not at build time. What construction
> cannot see — a branch that is well-formed but unreachable — is what
> `testing/unaired_check.py` sweeps for.

---

## 3. Schedule Resolution Pipeline

### The Resolution Stack

**Input:** Schedule target (can be complex nested structure)  
**Output:** Final content key (string)

**Resolution Order (CRITICAL):**
```
1. Day-of-week override
       ↓
2. Fallback to "default"
       ↓
3. SeasonalBlock resolution
       ↓
4. Holiday override
       ↓
5. Seasonal variant reference
       ↓
6. Final resolver.resolve()
```

---

### Example Flows

#### Flow 1: Simple String
```python
# Input
target = "simpsons_tv"

# Resolution
Step 1-5: Not applicable (already a string)
Step 6: resolver.resolve("simpsons_tv")
        → Looks up in MASTER_SOURCES
        → Registers with ErsatzTV if needed
        → Returns "simpsons_tv"

# Output
"simpsons_tv"
```

#### Flow 2: Collection
```python
# Input
target = collections.FOX_PRIMETIME  # OrderedCollection

# Resolution
Step 1-5: Not applicable
Step 6: resolver.resolve(collections.FOX_PRIMETIME)
        → Calls FOX_PRIMETIME.pick()
        → Returns "simpsons_tv" (or next in rotation)
        → Registers with ErsatzTV
        → Returns "simpsons_tv"

# Output
"simpsons_tv"
```

#### Flow 3: Day-of-Week Override
```python
# Input
target = {
    "default": collections.SITCOMS,
    "TUESDAY": collections.MOVIES
}

# Resolution
Step 1: boss.has("TUESDAY")? → Yes
        target = collections.MOVIES
Step 2-5: Not applicable
Step 6: resolver.resolve(collections.MOVIES)
        → Returns "jaws_movie"

# Output
"jaws_movie"
```

#### Flow 4: Seasonal + Holiday
```python
# Input
target = {
    "default": SeasonalBlock(
        base="classic_tv",
        seasonal={"WINTER": feather("cozy_tv", 0.5)}
    ),
    "halloween": "spooky_tv"
}

# Resolution (Winter, no Halloween)
Step 1: No day-of-week keys match
Step 2: target = SeasonalBlock(...)
Step 3: Is SeasonalBlock? → Yes
        boss.season_vibe = "WINTER"
        strength = 1.0 (peak winter)
        ratio = 0.5
        Random(0.75) < 0.5? → Yes
        target = "cozy_tv"
Step 4: holiday_ctx.is_active("halloween")? → No
        target = "cozy_tv" (unchanged)
Step 5: Not in seasonal_blocks dict
Step 6: resolver.resolve("cozy_tv")

# Output
"cozy_tv"

# Resolution (Winter, Halloween active)
Steps 1-3: Same as above → "cozy_tv"
Step 4: holiday_ctx.is_active("halloween")? → Yes
        Halloween not in target dict at this point
        Check global_holiday_overrides["halloween"]
        target = "halloween_tv"
Step 5-6: Same
        
# Output
"halloween_tv"
```

#### Flow 5: Complete Kitchen Sink
```python
# Input (Tuesday, Winter Peak, Halloween)
target = {
    "default": SeasonalBlock(
        base="classic_tv",
        seasonal={"WINTER": feather("cozy_tv", 0.5)}
    ),
    "TUESDAY": "movie_night",
    "halloween": "spooky_tv"
}

# Resolution
Step 1: boss.has("TUESDAY")? → Yes
        target = "movie_night"
Step 2: Not a dict anymore
Step 3: Not a SeasonalBlock
Step 4: holiday_ctx check
        Is target a dict? → No
        Check global_holiday_overrides
        global_holiday_overrides["halloween"] = "halloween_movies"
        target = "halloween_movies"
Step 5: Not in seasonal_blocks
Step 6: resolver.resolve("halloween_movies")

# Output
"halloween_movies"

# Key insight: TUESDAY matched FIRST, then Halloween overrode it
```

---

## 4. Time Management

### Hour Windows
**Concept:** Programming blocks defined by hour ranges.
```python
SCHEDULES = {
    "WEEKDAY": {
        (7, 10): "morning_shows",     # 7am-10am
        (19, 22): "primetime",         # 7pm-10pm
        (22, 2): "late_night"          # 10pm-2am (wraps midnight!)
    }
}
```

**Wraparound Handling:**
```python
hour_in_window(23, 22, 2)  # → True (11pm is in late_night)
hour_in_window(1, 22, 2)   # → True (1am is in late_night)
hour_in_window(3, 22, 2)   # → False (3am is not)
```

---

### Named Timeslots
**Concept:** Reusable named blocks instead of hour tuples.
```python
# Define once
DEFAULT_TIMESLOTS = {
    "midday": (10, 12),
    "noon": (12, 14),
    "evening": (17, 19),
    "prime": (19, 22),
    "night": (22, 2)
}

# Use everywhere
SCHEDULES = {
    "WEEKDAY": {
        "prime": "good_shows",
        "night": "cheap_shows"
    }
}

# Auto-expands to:
{
    (19, 22): "good_shows",
    (22, 2): "cheap_shows"
}
```

**Genre-Specific Presets:**
```python
# Kids channel
timeslot_preset="kids"
# Gives you: morning at 6am, prime at 3pm, etc.

# Movie channel
timeslot_preset="movies"
# Gives you: longer blocks for films
```

---

### Single-Play Slots
**Concept:** Play one item, then fill rest of slot with next block.

**Use Case:** Lunch special - one specific show, then regular programming
```python
SCHEDULES = {
    "WEEKDAY": {
        (12, 13): "elsbeth_tv",        # Lunch special
        (13, 17): collections.SITCOMS  # Afternoon block
    }
}

ScheduleConfig(
    schedules=SCHEDULES,
    single_play_slots=[(12, 13)]  # Mark as single-play
)
```

**What Happens:**
```
12:00 - Play Elsbeth (42 minutes)
12:42 - Start afternoon sitcoms early (fills gap)
13:00 - Continue afternoon sitcoms normally
```

---

## 5. Special Programming

### Marathons
**Concept:** Multi-episode takeover during specific hours.

**Trigger:**
```python
trigger = with_probability(0.05, "dbz_marathon")
# 5% daily chance
# Deterministic (same date = same result)
```

**Flow:**
```
1. Daily check: Does trigger fire?
2. If yes, mark marathon_to_run
3. At marathon start hour:
   - Override normal schedule
   - Pick marathon from collection
   - Convert to a Block of Programs
4. Marathon plays until:
   - Its window ends, OR
   - Episodes exhausted
5. Return to normal schedule
```

**Bounded vs. unbounded content**

How a marathon is committed to the playout depends on whether its query has a
known length. This matters: ErsatzTV's `add_count` has *no* time bound, so a
guessed count is not a safe way to express "play until the slot ends".

| Content | Example | How it plays |
|---|---|---|
| Bounded — query names a season/episode range | `dbz_frieza_saga_tv` (S3 E1-33) | `play_count` = 33, one `add_count` |
| Unbounded — query is a whole show | `simpsons_random_marathon` | `fill_window=True`, one `add_duration` for the remaining window |

An unbounded marathon must never be given a large `play_count`; ErsatzTV commits
every item in a single call and the slot overruns by days. See
[ERSATZTV_API.md](ERSATZTV_API.md) and the resolved entry in
[KNOWN_ISSUES.md](KNOWN_ISSUES.md).

**Features:**
- Auto-detects starting episode from query
- Skips to starting episode (once, before playback -- the cursor then advances
  on its own)
- EPG grouping (shows "DBZ Marathon" instead of individual episodes)
- Episode counting
- Safety checks

---

### Branded Blocks
**Concept:** Programming with intro/outro/bumpers.

**Components:**
- **Intro:** Plays once at start
- **Main Content:** Plays repeatedly
- **Bumpers:** Play between content items
- **Outro:** Plays once at end

**Flow:**
```
8:00 PM - TGIF Intro (30 sec)
8:01 PM - Full House (22 min)
8:23 PM - TGIF Bumper (15 sec)
8:24 PM - Family Matters (22 min)
8:46 PM - TGIF Bumper (15 sec)
8:47 PM - Step by Step (22 min)
9:09 PM - TGIF Outro (30 sec)
```

**Graceful Degradation:**
If intro/outro/bumpers don't exist in MASTER_SOURCES, just plays content normally.

---

### Multi-Day Events
**Concept:** Themed programming that lasts multiple days.

**Examples:**
- "13 Days of Halloween" (Oct 19-31)
- "Shark Week" (7 days in July)
- "25 Days of Christmas"

**Structure:**
```python
event = MultiDayEvent(
    name="13 Days of Halloween",
    trigger=on_date_range(10, 19, 10, 31),  # Oct 19-31
    duration_days=13,
    content=collections.HALLOWEEN_MOVIES,
    timeslots=["prime", "late_night"],  # Only override these
    priority=2  # Higher = more important
)
```

**Priority System:**
```
Priority 3: Shark Week (takes over everything)
Priority 2: 13 Days of Halloween
Priority 1: Regular marathons
```

---

## 6. Holiday System

### Detection
**HolidayContext** provides multiple ways to check holidays:
```python
holiday_ctx = HolidayContext(boss)

# Signal strength (0.0-1.0)
holiday_ctx.halloween  # 0.8 (strong)
holiday_ctx.christmas  # 0.2 (weak)

# Boolean checks
holiday_ctx.is_active("halloween", threshold=0.7)  # True
holiday_ctx.is_active("christmas", threshold=0.7)  # False

# Any major holiday?
holiday_ctx.is_holiday_season  # True

# List active holidays
holiday_ctx.active_holidays  # ["halloween"]
```

---

### Override System

**Two Levels:**

**1. Block-Level Overrides:**
```python
"prime": with_holidays(
    collections.REGULAR_TV,           # Default
    halloween=collections.SPOOKY_TV,  # Halloween override
    christmas=collections.XMAS_TV     # Christmas override
)
```

**2. Global Overrides:**
```python
ScheduleConfig(
    schedules=SCHEDULES,
    global_holiday_overrides={
        "halloween": collections.HALLOWEEN_CHANNEL_TAKEOVER,
        "christmas": collections.CHRISTMAS_CHANNEL_TAKEOVER
    }
)
```

**Priority:** Block-level > Global > Default

---

### Ramp Windows

**Each holiday has a ramp period:**
```python
# Halloween (7-day window)
Oct 24: Signal starts ramping
Oct 31: Peak (1.0)

# Christmas (21-day window)
Dec 4:  Signal starts ramping
Dec 25: Peak (1.0)
Dec 28: Hangover mode (0.75)
```

**Threshold System:**
```python
if holiday_ctx.is_active("halloween", threshold=0.7):
    # Strong Halloween vibe (last ~3 days)

if holiday_ctx.is_active("christmas", threshold=0.5):
    # Moderate Christmas vibe (last ~10 days)
```

---

## 7. Seasonal System

### Three-Level Strength

**Seasonal periods defined in registry:**
```python
"WINTER": {
    "peak": (12, 15, 1, 15),    # Mid-Dec to Mid-Jan (4 weeks)
    "active": (11, 15, 2, 15)   # Mid-Nov to Mid-Feb (12 weeks)
}
```

**Strength Calculation:**
```
In peak period:   1.0 (100% seasonal)
In active period: 0.5 (50% seasonal)
Off-season:       0.0 (0% seasonal)
```

---

### Blending Strategy

**SeasonalBlock uses probabilistic selection:**
```python
block = SeasonalBlock(
    base="classic_movies",
    seasonal={"WINTER": "cozy_movies"},
    blend_ratio=0.5
)

# During peak winter:
strength = 1.0
actual_ratio = 1.0 * 0.5 = 0.5
random() < 0.5? → 50% chance of cozy_movies

# During active winter:
strength = 0.5
actual_ratio = 0.5 * 0.5 = 0.25
random() < 0.25? → 25% chance of cozy_movies

# Off-season:
strength = 0.0
actual_ratio = 0.0
→ 0% chance of cozy_movies (always base)
```

---

### Season Crossfading

**season_vibe property:**
```python
boss.season_vibe  # Returns: "WINTER", "SPRING", "SUMMER", or "FALL"

# Uses linear ramp to next season's peak
May 15:  "SPRING" (100%)
June 10: "SPRING" (75%) or "SUMMER" (25%)
June 15: "SUMMER" (50%) or "SPRING" (50%)
July 10: "SUMMER" (75%) or "SPRING" (25%)
July 15: "SUMMER" (100%)
```

**Creates smooth transitions instead of hard switches.**

---

## 8. Error Handling & Safety

### Circuit Breaker
**Problem:** Content exhausted, time not advancing, infinite loop

**Solution:**
```python
if context.current_time <= last_time:
    # Time didn't advance!
    log("Circuit breaker: Content exhausted")
    # Skip forward 30 minutes
    api.wait_until(build_id, new_time)
```

**Prevents:**
- Infinite loops
- Empty content sources causing hangs
- API rate limiting from rapid calls

---

### Fallback Chain

**Multiple fallback layers:**
```
1. Schedule entry exists? Use it
       ↓ No
2. Fallback content defined? Use it
       ↓ No
3. Use hardcoded default ("classic_content")
```

**Every resolution step has safe defaults:**
- Dict without matching key → "default"
- SeasonalBlock without season → base
- Holiday override not defined → original target
- Collection.pick() on empty → returns None (caught by resolver)

---

### Pre-Registration Safety

**All content registered BEFORE playback:**
```python
_pre_register_all_content(resolver, config)
# Walks entire config tree
# Registers every possible content key
# Happens once at start
```

**Benefits:**
- Catches missing content early
- No mid-schedule registration failures
- Optimizes API calls (register once, play many)

---

## 9. Testing & Debugging

### Simulator
**Test channels without ErsatzTV:**
```python
from scripts.testing.simulator import test_channel
from datetime import date

# Test specific date
test_channel(cartoon_network, date(2026, 10, 31))

# Output shows full day schedule
```

---

### Debug Methods

**DayDirector:**
```python
boss.debug()
# Returns:
{
    "now": "2026-01-14 19:30",
    "labels": ["WEDNESDAY", "WEEKDAY", "PRIMETIME", ...],
    "season_vibe": "WINTER",
    "anniversary": "1996-01-14"
}

boss.debug_print()
# Prints formatted debug info
```

**Logging:**
```python
logger = ChannelLogger(prefix="[DEBUG]", verbose=True)
logger.debug("Detailed info here")
logger.info("Normal info")
logger.warn("Warning!")
logger.event("Marathon starting")
```

---

### Common Issues

**"Wrong content playing":**
1. Add logging to `resolve_content()` in `logic/resolution/pipeline.py`
2. Check each resolution step -- the returned `ResolutionResult` carries a
   `source` field naming which rule won (schedule / seasonal / holiday / ...)
3. Verify priority order

**"Marathon not triggering":**
1. Check trigger logic
2. Test trigger with specific date
3. Verify collection.pick() returns valid key

**"Circuit breaker firing":**
1. Content source empty (no results)
2. Query syntax error
3. Missing content in Jellyfin

---

## 10. Best Practices

### Channel Design

**DO:**
- Keep channels declarative (data > logic)
- Use collections for reusability
- Define timeslots once, reuse everywhere
- Use named timeslots for readability
- Group related content in collections

**DON'T:**
- Put complex logic in channels
- Duplicate content definitions
- Hardcode hour tuples everywhere
- Create one-off collections
- Mix concerns (holiday logic in channels)

---

### Content Organization

**DO:**
- One MASTER_SOURCES dict
- Descriptive content keys ("show_season_tv")
- Organized collections (by genre, theme, etc.)
- Metadata in sources (title, description)

**DON'T:**
- Multiple source dicts
- Cryptic keys ("s1", "ep1")
- Duplicate queries
- Metadata in channels

---

### Schedule Structure

**DO:**
- Use resolution order intentionally
- Layer overrides (day → seasonal → holiday)
- Provide fallbacks
Ensure `fallback_content` is a **Collection** or **String Key**.
- Test edge cases (midnight wraparound, etc.)

**DON'T:**
- Fight the resolution order
- Create circular dependencies
- Forget fallbacks
- Assume specific time behavior

---

## Summary

**The framework thinks in:**
1. **Time** - Labels, signals, windows
2. **Content** - Collections, keys, queries
3. **Resolution** - Layered decision pipeline
4. **Execution** - Marathons, blocks, events
5. **Safety** - Circuit breakers, fallbacks, pre-registration

**The framework gives you:**
- Declarative channel configs
- Temporal intelligence
- Content organization
- Special programming
- Error resilience

**You provide:**
- Content in Jellyfin
- Queries in MASTER_SOURCES
- Collections for grouping
- Schedule configs
- Marathon/event triggers

**Result:** Professional broadcast schedules in ~100 lines per channel.