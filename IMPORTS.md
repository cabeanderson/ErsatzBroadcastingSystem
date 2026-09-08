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
    get_seasonal_strength,   # Get 0.0-1.0 seasonal strength
    resolve_seasonal_block,  # Resolve block to content key
    feather,                 # Helper for partial blending
    swap                     # Helper for full takeover
)

# Usage
block = SeasonalBlock(
    base="classic_movies",
    seasonal={"WINTER": feather("winter_movies", 0.4)},
    blend_ratio=1.0
)
```

### Timeslots
```python
from scripts.logic.calendar.timeslots import (
    DEFAULT_TIMESLOTS,   # Standard broadcast timeslots
    ALT_TIMESLOTS,       # Genre-specific presets
    hour_in_window,      # Check if hour in window (handles wraparound)
    expand_timeslots     # Convert named slots to hour tuples
)

# Usage
if hour_in_window(hour, 19, 22):  # 7pm-10pm
    ...
```

### Triggers
```python
from scripts.logic.triggers import (
    Trigger,               # Base class
    ProbabilityTrigger,    # Daily probability
    DateRangeTrigger,      # Date range
    LabelTrigger,          # Label-based
    CompositeTrigger,      # Combine triggers
    # Convenience factories:
    chance,
    on_date_range,
    when_has,
    combine
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
from scripts.logic.playback import (
    is_approaching_hour_boundary, # Check if near hour
    hour_in_window                # Check time window
)

from scripts.engines.slots import (
    handle_single_play_slot       # Single-play slot logic
)
```

### Programming Objects
```python
from scripts.logic.models import (
    Marathon,           # Dataclass for marathon config
    Marathon,      # Dataclass for multi-day events
    BrandedBlock,       # Dataclass for branded blocks
    CommercialBreak     # Dataclass for commercial breaks
)

from scripts.logic.structures import (
    AppointmentBlock,   # Absolute date scheduling
    SeriesRelay,        # Relative sequential scheduling
    annual_show,        # Helper for annual appointments
    alternating_seasons # Helper for alternating shows
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
    ContentResolver,         # Main resolver class
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
```python
from scripts.engines.blocks import (
    BrandedBlock,          # Block configuration
    play_branded_block     # Execute branded block
)

# Usage
tgif = BrandedBlock(
    name="TGIF",
    content=structures.FAMILY_SITCOMS,
    intro="tgif_intro",
    bumpers="tgif_bumpers"
)
```

### Multi-Day Events
```python
from scripts.engines.blocks import (
    Marathon,        # Event configuration
    get_active_events,    # Check which events are active
    apply_event_overrides # Apply event overrides to target
)

# Usage
shark_week = Marathon(
    name="Shark Week",
    trigger=on_date_range(7, 15, 7, 21),
    duration_days=7,
    content=structures.SHARK_MOVIES
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