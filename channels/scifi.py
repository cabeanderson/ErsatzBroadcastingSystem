"""
Other Worlds - Science Fiction

Science fiction only. Fantasy moved to library/fantasy.py and horror to
Nightmare Theatre; what used to be a three-genre channel kept colliding with
everything around it and had no identity of its own.

Strands:
- The Vault      overnight and early -- Twilight Zone, TOS, Street Hawk
- Retro Action   Knight Rider, Quantum Leap
- Trek           mornings, Sunday, and Monday prime
- Space Opera    Babylon 5, Stargate SG-1, Farscape
- Investigation  The X-Files, Fringe
- Modern Epic    Battlestar Galactica, The Expanse, For All Mankind
- Gritty         Sarah Connor, Orphan Black, The Man in the High Castle
- Cult           Firefly, Dollhouse, Dark Angel

Named collections do the work rather than genre keys, because this library tags
Stargate SG-1 and Quantum Leap as Fantasy -- every sci-fi genre key carries a
NOT genre:fantasy clause and so cannot reach them.

Appointment TV: Sunday night (Lost, Alias, Fringe) runs on annual seasons.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.library import animation, scifi
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Marathon
from scripts.logic import triggers
from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. MARATHONS - Special event programming
# ==============================================================================

MARATHONS = [
    # Star Wars Day - May 4th
    Marathon(
        name="Star Wars Day Marathon",
        trigger=triggers.has_label("STAR_WARS_DAY"),
        collection="star_wars_saga_chronological",
        hours=(8, 23),
        priority=2
    ),
    
    # Random Star Trek Marathon - 1% chance any day
    Marathon(
        name="Star Trek Marathon",
        trigger=triggers.chance(0.01, "star_trek_surprise"),
        collection="star_trek_all_playlist",
        hours=(10, 23),
        priority=1
    ),
]

# ==============================================================================
# 2. BLOCK DEFINITIONS (Chronological)
# ==============================================================================

SCIFI_PRIME_SEASONAL = SeasonalBlock(
    base={
        "MONDAY": "star_trek_all_playlist",
        "TUESDAY": scifi.SCIFI_INVESTIGATION,
        "WEDNESDAY": scifi.SCIFI_SPACE_OPERA,
        "THURSDAY": scifi.SCIFI_MODERN_EPIC,
        "FRIDAY": scifi.SCIFI_GRITTY,
        "default": scifi.MODERN_SCIFI_BLOCK
    },
    seasonal={
        # Both swaps are per-day. Spring's used to sit at the top level, where a
        # bare Swap replaces every day at once -- so for three months a year the
        # whole Mon-Fri lineup became one two-key random pool and X-Files,
        # Babylon 5, BSG and Sarah Connor dropped to about 45 minutes a week
        # each. Summer had it right; spring now matches.
        "SUMMER": {
            "FRIDAY": Swap(scifi.SCI_FI_SHOWCASE)   # Blockbuster Friday
        },
        "SPRING": {
            "WEDNESDAY": Swap(scifi.MODERN_SCIFI_BLOCK)  # Discovery Season
        }
    }
)

# Every block below is keyed on WEEKEND / WEEKDAY_A / WEEKDAY_B or the individual
# days, which between them cover all seven. A "default" arm behind those is
# unreachable -- five of the eight blocks had one, and EARLY_BLOCK's was the only
# weekday fantasy on the channel, which meant it never aired at all. None of them
# are defaults now; where two day-groups genuinely share content they say so.

# Overnight (02:00 - 06:00)
OVERNIGHT_BLOCK = scifi.SCIFI_VAULT

# Early Block (06:00 - 08:00)
EARLY_BLOCK = {
    "WEEKEND": scifi.SCIFI_VAULT,
    "WEEKDAY_B": "classic_scifi_movie",       # Tue/Thu
    "WEEKDAY_A": scifi.SCIFI_RETRO_ACTION     # Mon/Wed/Fri -- Knight Rider, Quantum Leap
}

# Morning Block (08:00 - 10:00)
MORNING_BLOCK = {
    "SATURDAY": scifi.SCIFI_MYTHS,
    "SUNDAY": "star_trek_all_playlist",
    "WEEKDAY_A": "action_scifi_movie",
    "WEEKDAY_B": scifi.TREK_MORNING           # was HERCULES_XENA, which is fantasy
}

# Midday Block (10:00 - 12:00)
MIDDAY_BLOCK = {
    "SATURDAY": "comedy_scifi_movie",         # was CREATURE_FEATURE (horror)
    "SUNDAY": scifi.SCIFI_SPACE_OPERA,
    "WEEKDAY_A": scifi.MODERN_SCIFI_BLOCK,
    # The broad pool, deliberately: mid-morning is where an undifferentiated
    # hour belongs, and this is the only key that reaches Stargate SG-1 and
    # Quantum Leap past the NOT genre:fantasy clause the named strands avoid.
    # Was the Trek playlist, which sat directly after TREK_MORNING.
    "WEEKDAY_B": "scifi_all_tv"
}

# Noon Block (12:00 - 14:00)
NOON_BLOCK = {
    "SATURDAY": "action_scifi_movie",         # was CREATURE_FEATURE (horror)
    "SUNDAY": scifi.SCIFI_SPACE_OPERA,
    "WEEKDAY_A": scifi.SCIFI_SPACE_OPERA,
    "WEEKDAY_B": Block(
        name="Sci-Fi Noon Movie",
        items=["comedy_scifi_movie"],
        fill_strategy="bridge",
        strict_window=False
    )
}

# Afternoon Block (14:00 - 17:00)
AFTERNOON_BLOCK = {
    "WEEKEND": scifi.MODERN_SCIFI_BLOCK,      # Sat was FANTASY_ADVENTURE
    "WEEKDAY_A": scifi.SCIFI_INVESTIGATION,   # was PARANORMAL_FILES (horror TV)
    "WEEKDAY_B": scifi.SCIFI_GRITTY           # was scifi_fantasy_tv
}

# Evening Block (17:00 - 20:00)
EVENING_BLOCK = {
    "SATURDAY": scifi.SCIFI_INVESTIGATION,    # was PARANORMAL_FILES
    "SUNDAY": scifi.SCIFI_MODERN_EPIC,        # was PARANORMAL_FILES
    "WEEKDAY_A": scifi.SCIFI_MODERN_EPIC,     # was space_opera_tv, the un-narrowed pool
    "WEEKDAY_B": scifi.SCIFI_CULT             # Firefly/Dollhouse/Dark Angel, was WHEDONVERSE
}

# Prime Block (20:00 - 23:00)
PRIME_BLOCK = {
    "SATURDAY": scifi.SCI_FI_SHOWCASE,
    "SUNDAY": scifi.SCIFI_SUNDAY_BLOCK,
    "WEEKDAY": SCIFI_PRIME_SEASONAL
}

# Night Block (23:00 - 02:00)
NIGHT_BLOCK = {
    "SATURDAY": "modern_scifi_movie",         # was UNDEAD_CINEMA (horror)
    "SUNDAY": scifi.SCIFI_VAULT,
    "WEEKDAY": scifi.SCI_FI_SHOWCASE
}

# ==============================================================================
# 3. SCHEDULE DEFINITIONS
# ==============================================================================

DAILY_SCHEDULE = {
    "overnight": OVERNIGHT_BLOCK,
    "early": EARLY_BLOCK,
    "morning": MORNING_BLOCK,
    "midday": MIDDAY_BLOCK,
    "noon": NOON_BLOCK,
    "afternoon": AFTERNOON_BLOCK,
    "evening": EVENING_BLOCK,
    "prime": PRIME_BLOCK,
    "night": NIGHT_BLOCK
}

SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
    "WEEKEND": DAILY_SCHEDULE
}

# ==============================================================================
# 4. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        timeslot_preset="default",
        logger=ChannelLogger(prefix="[SCIFI]"),
        fallback_content="scifi_tv",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)