"""
Sci-Fi Channel - Imagination Unleashed

Features:
- Genre-based scheduling (Space Opera, Fantasy, Paranormal)
- Weekend Creature Features
- Modern vs Classic Sci-Fi blocks
- Cross-pollination with Animation (Superhero Hour)
- Appointment TV (Sequential playback for major series in Fall/Winter)
"""

from etv_client.models import ControlWaitUntil
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.library import collections, blocks
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic.models import Swap, PlayOnce, Marathon
from scripts.logic import triggers
from scripts.playout import ChannelLogger

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
# 1. BLOCK DEFINITIONS (Chronological)
# ==============================================================================

# Sunday Appointment Block: Lost -> Alias -> Fringe
SCIFI_SUNDAY_BLOCK = collections.DailyOrderedCollection([
    blocks.LOST_APPOINTMENT_BLOCK,
    "alias_chronological_tv",
    "fringe_chronological_tv"
])

SCIFI_PRIME_SEASONAL = SeasonalBlock(
    base={
        "MONDAY": "star_trek_all_playlist",
        "TUESDAY": collections.SCIFI_INVESTIGATION,
        "WEDNESDAY": collections.SCIFI_SPACE_OPERA,
        "THURSDAY": collections.SCIFI_MODERN_EPIC,
        "FRIDAY": collections.SCIFI_GRITTY,
        "default": collections.MODERN_SCIFI_BLOCK
    },
    seasonal={
        "SUMMER": {
            "FRIDAY": Swap(collections.SCI_FI_SHOWCASE) # Blockbuster Summer on most days...
        },
        "SPRING": Swap(collections.MODERN_SCIFI_BLOCK)    # Discovery Season
    }
)

# Early Block (06:00 - 08:00)
EARLY_BLOCK = {
    "WEEKEND": collections.SCIFI_CLASSICS_TV,
    "WEEKDAY_B": "classic_scifi_movie", # Tue/Thu
    "WEEKDAY_A": {                      # Mon/Wed/Fri
        "WEDNESDAY": collections.RandomCollection(["orville_tv", "farscape_chronological_tv"]),
        "default": collections.STAR_WARS_ANIMATION
    },
    "default": collections.FANTASY_ADVENTURE
}

# Morning Block (08:00 - 10:00)
MORNING_BLOCK = {
    "SATURDAY": collections.SCIFI_MYTHS,
    "SUNDAY": "star_trek_all_playlist",
    "WEEKDAY_A": "action_scifi_movie",
    "WEEKDAY_B": collections.HERCULES_XENA,
    "default": collections.SCIFI_CLASSICS_TV
}

# Midday Block (10:00 - 12:00)
MIDDAY_BLOCK = {
    "SATURDAY": collections.CREATURE_FEATURE,
    "SUNDAY": "space_opera_tv",
    "WEEKDAY_A": collections.MODERN_SCIFI_BLOCK, # Mon/Wed/Fri
    "WEEKDAY_B": "star_trek_all_playlist",  # Tue/Thu
    "default": "scifi_fantasy_tv"
}

# Noon Block (12:00 - 14:00)
NOON_BLOCK = {
    "SATURDAY": collections.CREATURE_FEATURE,
    "SUNDAY": "space_opera_tv",
    "WEEKDAY_A": collections.OrderedCollection(["knight_rider_tv", "quantum_leap_chronological_tv"]),
    "default": PlayOnce("comedy_scifi_movie")
}

# Afternoon Block (14:00 - 18:00)
AFTERNOON_BLOCK = {
    "SATURDAY": collections.FANTASY_ADVENTURE,
    "SUNDAY": collections.MODERN_SCIFI_BLOCK,
    "WEEKDAY_A": collections.PARANORMAL_FILES,
    "WEEKDAY_B": "scifi_fantasy_tv",
    "default": collections.PARANORMAL_FILES
}

# Evening Block (18:00 - 20:00)
EVENING_BLOCK = {
    "WEEKEND": collections.PARANORMAL_FILES,
    "WEEKDAY_A": "space_opera_tv",
    "WEEKDAY_B": collections.WHEDONVERSE_SAGA,
    "default": "space_opera_tv"
}

# Prime Block (20:00 - 23:00)
PRIME_BLOCK = {
    "SATURDAY": collections.SCI_FI_SHOWCASE,
    "SUNDAY": SCIFI_SUNDAY_BLOCK,
    "default": SCIFI_PRIME_SEASONAL
}

# Night Block (23:00 - 02:00)
NIGHT_BLOCK = {
    "SATURDAY": collections.UNDEAD_CINEMA,
    "SUNDAY": collections.SCIFI_CLASSICS_TV,
    "default": collections.SCI_FI_SHOWCASE
}

# ==============================================================================
# 2. SCHEDULE DEFINITIONS
# ==============================================================================

DAILY_SCHEDULE = {
    "overnight": collections.SCIFI_CLASSICS_TV,
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
        fallback_content="classic_scifi_tv"
    )
    return run_daily_schedule(api, context, build_id, config)