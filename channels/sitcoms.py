"""
Sitcoms Channel - Laughter Through the Decades

Features:
- TGIF Branded Block (Friday Prime)
- Seasonal Prime Time (Summer Teen / Winter Classics)
- Era-based Dayparts (70s Morning, 90s Daytime)
- Holiday Comedy Events
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Feather
from scripts.logic.structures import RandomCollection
from scripts.library import sitcoms, common
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "FRIDAY": {
        "overnight": sitcoms.CLASSIC_SITCOMS_60s_70s,
        "early": sitcoms.SEVENTIES_MORNING,
        "morning": sitcoms.SEVENTIES_MORNING,
        "midday": sitcoms.NINETIES_DAYTIME, # Changed from classics
        "noon": sitcoms.NINETIES_DAYTIME,   # Changed from lunch
        "afternoon": sitcoms.NINETIES_FAMILY,
        "evening": sitcoms.NINETIES_PRIMETIME, # Changed from early_evening
        "prime": sitcoms.TGIF_BLOCK, # Our branded block from 19:00 - 22:00
        "night": sitcoms.LATE_NIGHT_SYNDICATION
    },
    "WEEKDAY": {
        "overnight": sitcoms.CLASSIC_SITCOMS_60s_70s,
        "early": sitcoms.SEVENTIES_MORNING,
        "morning": {
            "WEEKDAY_A": sitcoms.SEVENTIES_MORNING,
            "WEEKDAY_B": sitcoms.CLASSIC_SITCOMS_60s_70s,
            "default": sitcoms.SEVENTIES_MORNING
        },
        "midday": sitcoms.NINETIES_DAYTIME,
        "noon": sitcoms.NINETIES_DAYTIME,
        "afternoon": sitcoms.SITCOM_AFTERNOON_SEASONAL,
        "evening": sitcoms.NINETIES_PRIMETIME,
        "prime": {
            "THURSDAY": sitcoms.MUST_SEE_THURSDAY,
            "default": sitcoms.SITCOM_WEEKDAY_PRIME
        },
        "night": sitcoms.LATE_NIGHT_SYNDICATION
    },
    "WEEKEND": {
        "overnight": sitcoms.CLASSIC_SITCOMS_60s_70s,
        "early": sitcoms.NINETIES_FAMILY,
        "morning": sitcoms.NINETIES_FAMILY,
        "midday": sitcoms.NINETIES_DAYTIME,
        "noon": sitcoms.NINETIES_DAYTIME,
        "afternoon": sitcoms.NINETIES_PRIMETIME,
        "prime": sitcoms.SITCOM_WEEKEND_PRIME,
        "night": sitcoms.LATE_NIGHT_SYNDICATION
    }
}

# ==============================================================================
# 4. HOLIDAY SCHEDULES (For Ramps)
# ==============================================================================

# These blocks will probabilistically replace the regular schedule
# as the holiday approaches.

CHRISTMAS_AFTERNOON_MOVIES = RandomCollection([
    "christmas_80s_movie",
    "christmas_90s_movie"
])

HALLOWEEN_SCHEDULE = {
    "overnight": common.HALLOWEEN_TV_EVENT,
    "early": common.HALLOWEEN_TV_EVENT,
    "morning": common.HALLOWEEN_TV_EVENT,
    "midday": common.HALLOWEEN_TV_EVENT,
    "noon": common.HALLOWEEN_TV_EVENT,
    "afternoon": common.HALLOWEEN_TV_EVENT,
    "evening": common.HALLOWEEN_TV_EVENT,
    "prime": common.HALLOWEEN_TV_EVENT,
    "night": common.HALLOWEEN_TV_EVENT
}

CHRISTMAS_SCHEDULE = {
    "midday": common.CHRISTMAS_TV_EVENT,
    "afternoon": CHRISTMAS_AFTERNOON_MOVIES,
    "prime": common.CHRISTMAS_TV_EVENT,
    "night": "christmas_classic_movie",
}

# Reuse Christmas logic for others for now, or create specific collections
THANKSGIVING_SCHEDULE = {k: common.THANKSGIVING_COMEDY_EVENT for k in HALLOWEEN_SCHEDULE}
#VALENTINES_SCHEDULE = {k: common.VALENTINES_COMEDY_EVENT for k in HALLOWEEN_SCHEDULE}

# ==============================================================================
# 5. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00", 
        tomorrow=False, 
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset="default",
        holiday_schedules={
            "HALLOWEEN": HALLOWEEN_SCHEDULE,
            "THANKSGIVING": THANKSGIVING_SCHEDULE,
            "CHRISTMAS": CHRISTMAS_SCHEDULE,
         #   "VALENTINES_DAY": VALENTINES_SCHEDULE,
        },
        block_profiles={},
        # filler_content="commercials_spot", # TODO: Add collections.BUMPERS when available
        logger=ChannelLogger(prefix="[SITCOMS]"),
        # Not CLASSIC_SITCOMS_60s_70s: a fallback firing after 21:00 would
        # put the shared classics up against Nick at Nite.
        fallback_content=sitcoms.LATE_NIGHT_SYNDICATION,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
        enable_bumpers=True
    )
    
    return run_daily_schedule(api, context, build_id, config)