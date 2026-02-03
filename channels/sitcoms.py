"""
Sitcoms Channel - Laughter Through the Decades

Features:
- TGIF Branded Block (Friday Prime)
- Seasonal Prime Time (Summer Teen / Winter Classics)
- Era-based Dayparts (70s Morning, 90s Daytime)
- Holiday Comedy Events
"""

from etv_client.models import ControlWaitUntil
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.logic.seasonal import SeasonalBlock
from scripts.library import collections, blocks
from scripts.playout import ChannelLogger

# 2. SEASONAL BLOCKS
# Weekday Prime: Must See TV normally, but Summer brings Teen shows
WEEKDAY_PRIME = SeasonalBlock(
    base=collections.MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN), # Saved by the Bell, etc.
        "WINTER": Feather(collections.CLASSIC_SITCOMS_60s_70s, ratio=0.4) # 40% chance of Classics in Winter
    },
    blend_ratio=1.0 # Default to full swap for Summer
)

AFTERNOON_SEASONAL = SeasonalBlock(
    base=collections.NINETIES_FAMILY,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN),
        "FALL": Feather(collections.WORKING_CLASS_SITCOMS, ratio=0.6)
    }
)

WEEKEND_PRIME = SeasonalBlock(
    base=collections.MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN),
        "WINTER": Swap(collections.CLASSIC_SITCOMS_60s_70s)
    },
    blend_ratio=1.0
)

# 2. SCHEDULES
SCHEDULES = {
    "FRIDAY": {
        "overnight": collections.CLASSIC_SITCOMS_60s_70s,
        "early": collections.SEVENTIES_MORNING,
        "morning": collections.SEVENTIES_MORNING,
        "midday": collections.NINETIES_DAYTIME, # Changed from classics
        "noon": collections.NINETIES_DAYTIME,   # Changed from lunch
        "afternoon": collections.NINETIES_FAMILY,
        "evening": collections.NINETIES_PRIMETIME, # Changed from early_evening
        "prime": blocks.TGIF_BLOCK, # Our branded block from 19:00 - 22:00
        "night": collections.NICK_AT_NITE    # Changed from late_night
    },
    "WEEKDAY": {
        "overnight": collections.CLASSIC_SITCOMS_60s_70s,
        "early": collections.SEVENTIES_MORNING,
        "morning": {
            "WEEKDAY_A": collections.SEVENTIES_MORNING,
            "WEEKDAY_B": collections.CLASSIC_SITCOMS_60s_70s,
            "default": collections.SEVENTIES_MORNING
        },
        "midday": collections.NINETIES_DAYTIME,
        "noon": collections.NINETIES_DAYTIME,
        "afternoon": AFTERNOON_SEASONAL,
        "evening": collections.NINETIES_PRIMETIME,
        "prime": WEEKDAY_PRIME, # Use the seasonal block
        "night": collections.NICK_AT_NITE
    },
    "WEEKEND": {
        "overnight": collections.CLASSIC_SITCOMS_60s_70s,
        "early": collections.NINETIES_FAMILY,
        "morning": collections.NINETIES_FAMILY,
        "midday": collections.NINETIES_DAYTIME,
        "noon": collections.NINETIES_DAYTIME,
        "afternoon": collections.NINETIES_PRIMETIME,
        "prime": WEEKEND_PRIME,
        "night": collections.NICK_AT_NITE
    }
}

# 3. HOLIDAY SCHEDULES (For Ramps)
# These blocks will probabilistically replace the regular schedule
# as the holiday approaches.

HALLOWEEN_SCHEDULE = {
    "overnight": collections.HALLOWEEN_TV_EVENT,
    "early": collections.HALLOWEEN_TV_EVENT,
    "morning": collections.HALLOWEEN_TV_EVENT,
    "midday": collections.HALLOWEEN_TV_EVENT,
    "noon": collections.HALLOWEEN_TV_EVENT,
    "afternoon": collections.HALLOWEEN_TV_EVENT,
    "evening": collections.HALLOWEEN_TV_EVENT,
    "prime": collections.HALLOWEEN_TV_EVENT,
    "night": collections.HALLOWEEN_TV_EVENT
}

CHRISTMAS_SCHEDULE = {
    "overnight": collections.CHRISTMAS_TV_EVENT,
    "early": collections.CHRISTMAS_TV_EVENT,
    "morning": collections.CHRISTMAS_TV_EVENT,
    "midday": collections.CHRISTMAS_TV_EVENT,
    "noon": collections.CHRISTMAS_TV_EVENT,
    "afternoon": collections.CHRISTMAS_TV_EVENT,
    "evening": collections.CHRISTMAS_TV_EVENT,
    "prime": collections.CHRISTMAS_TV_EVENT,
    "night": collections.CHRISTMAS_TV_EVENT
}

# Reuse Christmas logic for others for now, or create specific collections
THANKSGIVING_SCHEDULE = {k: collections.THANKSGIVING_COMEDY_EVENT for k in HALLOWEEN_SCHEDULE}
VALENTINES_SCHEDULE = {k: collections.VALENTINES_COMEDY_EVENT for k in HALLOWEEN_SCHEDULE}

# 3. BUILD FUNCTION
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
            "VALENTINES_DAY": VALENTINES_SCHEDULE,
        },
        block_profiles=HOLIDAY_PROFILES,
        # filler_content="commercials_spot", # TODO: Add collections.BUMPERS when available
        logger=ChannelLogger(prefix="[SITCOMS]"),
        fallback_content=collections.CLASSIC_SITCOMS_60s_70s
    )
    
    return run_daily_schedule(api, context, build_id, config)