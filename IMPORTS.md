# Import Reference Guide

Quick reference for importing from the ErsatzTV scheduling framework.

---

## Core Imports (Foundation)

### DayDirector - Main Interface
```python
from scripts.core import DayDirector

# Usage in schedule
boss = DayDirector(context)
if boss.has("SATURDAY"):
    ...
```

### Registry Data
```python
from scripts.core.registry import (
    HOLIDAYS,           # Dict of (month, day) to holiday name
    SEASONS,            # Dict of season to month list
    SEASONAL_PERIODS,   # Dict of season to peak/active windows
    DAYPARTS,           # Dict of hour range to daypart name
    WEEKDAY_GROUPS      # Dict of group name to weekday set
)
```

### Date Functions
```python
from scripts.core.states import (
    derive_labels,      # Get all labels for a datetime
    is_in_date_range,   # Check if date in range (handles wraparound)
    days_until,         # Days until next occurrence
    days_since,         # Days since last occurrence
    in_window           # Check if within N days of event
)
```

### Math Functions
```python
from scripts.core.signals import (
    get_parabolic_surge,  # Exponential ramp (0.0 to 1.0)
    get_decay_signal,     # Rapid falloff (1.0 to 0.0)
    get_linear_ramp       # Steady linear transition
)
```

---

## Logic Imports (Features)

### Holiday System
```python
from scripts.logic.calendar.holidays import (
    HolidayContext,      # Main holiday detection class
    with_holidays,       # Helper for creating override blocks
    get_holiday_target   # Apply holiday overrides to target
)

# Usage
holiday_ctx = HolidayContext(boss)
if holiday_ctx.is_active("halloween"):
    ...

# In schedules
"prime": with_holidays(
    structures.REGULAR_SHOWS,
    halloween=structures.HALLOWEEN_EVENT,
    christmas=structures.CHRISTMAS_EVENT
)
```

### Seasonal System
```python
from scripts.logic.calendar.seasonal import (
    SeasonalBlock,           # Blends base + seasonal content
    resolve_seasonal_block,  # Resolve block to content key
    Feather,                 # Partial blend -- some of the seasonal pool
    Swap                     # Full takeover for the season
)

# Usage
block = SeasonalBlock(
    base="classic_movies",
    seasonal={"WINTER": Feather("winter_movies", 0.4)},
    blend_ratio=1.0
)
```

### Timeslots
```python
from scripts.logic.calendar.timeslots import (
    DEFAULT_TIMESLOTS,   # Standard broadcast timeslots
    ALT_TIMESLOTS,       # Genre-specific presets
    expand_timeslots,    # Convert named slots to hour tuples
    get_timeslot_map     # Resolve a channel's preset to its slot map
)

# Usage -- `hour_in_window` lives in logic.resolution.playback, not here.
# get_timeslot_map takes the preset *name*, not the dict.
slots = get_timeslot_map("movies")
```

### Triggers
```python
from scripts.logic.triggers import (
    chance,         # Deterministic daily probability
    has_label,      # Fires when the day carries a label
    on_date,        # A single calendar date
    in_range,       # A date range
    day_of_month,   # The Nth of the month
    all_of,         # Every trigger must fire
    any_of          # Any one of them
)

# Usage
trigger = combine(
    when_has("SATURDAY"),
    chance(0.25, "special")
)
```

### Resolution
```python
from scripts.logic.resolution.pipeline import resolve_content

# Usage in schedule loop
final_key = resolve_content(
    target, boss, holiday_ctx, config, resolver
)
```

### Playback Strategies
```python
from scripts.logic.resolution.playback import (
    is_approaching_hour_boundary, # Check if near hour
    hour_in_window,               # Check time window
    calculate_boundary_dt         # The next boundary as a datetime
)
```

### Programming Objects
```python
from scripts.logic.models import (
    Marathon,           # Dataclass for a multi-day / triggered event
    Branding,           # intro / outro / bumpers for a block
    CommercialBreak,    # Dataclass for commercial breaks
    Fallback            # Primary key with a secondary behind it
)

from scripts.logic.structures import (
    Block,              # A named container of slots
    Program             # A scheduled item with its own rules
)

from scripts.logic.factories import (
    annual_show,          # One season a year, chronological
    alternating_seasons,  # Interleave several shows annually
    monthly_rotation,     # A month per item, up to twelve
    multiyear_rotation    # A month per item, across up to five years
)

# Usage
marathon = Marathon(
    name="DBZ Marathon",
    trigger=chance(0.05),
    collection=structures.DBZ_SAGAS,
    hours=(10, 24)
)
```

---

## Library Imports (Content)

### Collections
```python
from scripts.logic import structures

# Access collections
structures.FOX_PRIMETIME
structures.CLASSIC_CARTOONS
structures.DBZ_SAGAS
```

### Sources
```python
from scripts.library import sources
from scripts.library.sources import MASTER_SOURCES

# Access source definitions
MASTER_SOURCES["simpsons_tv"]
```

### Resolver
```python
from scripts.logic.resolution.resolver import (
    ContentResolver          # Main resolver class
)

from scripts.library.queries import (
    extract_episode_range,   # Extract season/episode from query
    count_episodes_in_range  # Count episodes in query range
)

# Usage
resolver = ContentResolver(api, build_id, MASTER_SOURCES)
key = resolver.resolve(target)
```

---

## Engine Imports (Complex Behaviors)

### Marathon
```python
from scripts.logic.calendar.assembly import find_active_marathon

# Usage
context = run_marathon(
    api, build_id, context,
    marathon_key="dbz_saiyan_saga_tv",
    sources_registry=MASTER_SOURCES,
    start_hour=10,
    end_hour=24,
    title="DBZ Marathon",
    log_func=logger.info
)
```

### Branded Blocks

There is no `BrandedBlock`. Branding is a field on an ordinary `Block`, and the
engine plays it around the block's contents.

```python
from scripts.logic.structures import Block
from scripts.logic.models import Branding

from scripts.engines.blocks import (
    play_block,            # Execute a block, branding included
    play_block_intro,      # The pieces, if you need them directly
    play_block_outro,
    play_generic_branding
)

# Usage
tgif = Block(
    name="TGIF",
    items=structures.FAMILY_SITCOMS,
    intro="tgif_intro",
    bumpers="tgif_bumpers"
)
```

### Multi-Day Events
```python
from scripts.logic.models import Marathon
from scripts.logic.calendar.assembly import find_active_marathon

# Usage -- a marathon takes an hour window, not a duration in days, and the
# trigger decides which days it fires on.
shark_week = Marathon(
    name="Shark Week",
    trigger=in_range(7, 15, 7, 21),
    collection=structures.SHARK_MOVIES,
    hours=(10, 24),
    priority=1
)
```

---

## Top-Level Imports (Orchestration)

### Schedule
```python
from scripts.scheduling import (
    run_daily_schedule,    # Main orchestration function
    ScheduleConfig,        # Configuration dataclass
    ScheduleRunner         # The loop object run_daily_schedule wraps
)

# Usage
config = ScheduleConfig(
    schedules=SCHEDULES,
    marathons=MARATHONS,
    log_prefix="[CARTOONS]"
)

context = run_daily_schedule(api, context, build_id, config)
```

### Playout
```python
from scripts.playout import (
    play_item,                  # Add N items (add_count) -- NO time bound
    play_for_duration,          # Add items until a datetime (add_duration)
    play_with_fallback,         # Play content, handling Fallback objects
    wait_until_time,            # Dead air until a datetime (wait_until_exact)
    fill_until_time,            # Pad with filler until a datetime (pad_until_exact)
    fill_until_next_hour,       # Pad to the next hour boundary
    circuit_breaker,            # Prevent infinite loops
    toggle_epg_group,           # EPG group control
    epg_group                   # EPG group context manager
)
```

`wait_until_time` and `fill_until_time` take an absolute `datetime`, not an
`"HH:MM"` string -- see [ERSATZTV_API.md](ERSATZTV_API.md) for why the
time-of-day endpoints are avoided.

Related helpers live elsewhere:

```python
from scripts.core.logger import ChannelLogger              # Structured logging
from scripts.logic.resolution.playback import (
    is_approaching_hour_boundary,  # Check if near hour
    calculate_boundary_dt,         # End-of-slot datetime (handles midnight wrap)
    hour_in_window                 # Slot membership test
)

# Usage
logger = ChannelLogger(prefix="[CARTOONS]", verbose=True)
context = play_item(api, build_id, content_key)
```

---

## ErsatzTV API Models
```python
from etv_client.models import (
    # Content
    PlayoutCount,            # Play N items
    PlayoutDuration,         # Play for N hours
    ContentSearch,           # Search-based content
    
    # Control
    ControlWaitUntil,        # Jump to time
    ControlSkipToItem,       # Skip to episode
    ControlStartEpgGroup,    # Start EPG group
    
    # Padding
    PlayoutPadUntil,         # Pad to time with filler
    PlayoutPadUntilExact,    # Pad to exact time
)
```

---

## Common Import Patterns

### Minimal Channel
```python
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.calendar.holidays import with_holidays
from scripts.logic import structures
from etv_client.models import ControlWaitUntil
```

### Channel with Marathons
```python
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.calendar.holidays import with_holidays
from scripts.logic.triggers import chance
from scripts.logic.models import Marathon
from scripts.logic import structures
from etv_client.models import ControlWaitUntil
```

### Channel with Seasonal Blending
```python
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.calendar.holidays import with_holidays
from scripts.logic import structures
from etv_client.models import ControlWaitUntil
```

### Full-Featured Channel
```python
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.calendar.holidays import with_holidays
from scripts.logic.triggers import chance, has_label, any_of
from scripts.logic.models import Marathon, Marathon
from scripts.playout import ChannelLogger
from scripts.logic import structures
from etv_client.models import ControlWaitUntil
```

---

## Re-Exports

Only three packages re-export anything, and this is the complete list. Anything
not named here must be imported from the module that defines it — in particular
`SeasonalBlock` and `DayDirector` are **not** re-exported, despite what earlier
revisions of this file claimed.

```python
# scripts.core
from scripts.core import DayDirector, stable_hash

# scripts.logic
from scripts.logic import (
    with_holidays,
    Marathon, Branding, Fallback, Swap, Feather, CommercialBreak,
    ContentResolver,
)

# scripts.scheduling
from scripts.scheduling import run_daily_schedule, ScheduleConfig, ScheduleRunner
```

Everything else comes from its defining module:
```python
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.structures import Block, Program, OrderedCollection
from scripts.core.logger import ChannelLogger
```

---

## Import Anti-Patterns

### ❌ Don't Import Internal Functions
```python
# Bad
from scripts.logic.resolution.pipeline import _unwrap_nested_structure
from scripts.logic.resolution.pipeline import _finalize_content_resolution

# Good - use public APIs
from scripts.scheduling import run_daily_schedule
from scripts.logic.resolution.pipeline import resolve_content
```

### ❌ Don't Import Across Layers
```python
# Bad - bypasses abstraction
from scripts.core.states import derive_labels
labels = derive_labels(datetime.now())

# Good - use DayDirector
from scripts.core import DayDirector
boss = DayDirector(context)
if boss.has("SATURDAY"):
    ...
```

### ❌ Don't Import *
```python
# Bad
from scripts.logic.structures import *

# Good
from scripts.logic import structures
structures.FOX_PRIMETIME
```

---

## IDE Configuration

### VS Code
Add to `settings.json`:
```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}/scripts"
    ]
}
```

### PyCharm
Mark `scripts/` as "Sources Root"

---

## Type Hints Reference
```python
from scripts.core import DayDirector
from scripts.logic.calendar.holidays import HolidayContext
from scripts.logic.resolution.resolver import ContentResolver
from scripts.scheduling import ScheduleConfig
from typing import Callable, Dict, List, Tuple, Optional

def my_trigger(boss: DayDirector) -> bool:
    return boss.has("SATURDAY")

def my_schedule() -> Dict[str, Dict]:
    return {
        "WEEKDAY": {
            "prime": "some_content"
        }
    }
```