"""
Classic Movies Channel - Timeless Cinema

Programming Philosophy:
- Overnight: Film noir and dark classics
- Morning: Golden Age Hollywood (1930s-1950s)
- Afternoon: Seasonal themed classics
- Prime: Era-specific seasonal showcases

Seasonal Strategy:
- Summer: Modern blockbusters dominate prime time
- Fall: Noir and mystery take over
- Winter: Return to Golden Age classics
- Spring: Musicals and romantic comedies

Holiday Events:
- Halloween: Marathon event programming
- Christmas: Festival programming (afternoon + prime)
- Christmas in July: Special marathon (July 25)
"""
from etv_client.models import ControlWaitUntil
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.logic.models import Marathon, Swap, Feather
from scripts.logic import triggers
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic.profiles import CHRISTMAS_PROFILES, STANDARD_PROFILES # TODO: Use specific profiles
from scripts.library import collections
from scripts.playout import ChannelLogger

# 1. SPECIAL EVENTS
MARATHONS = [
    Marathon(
        name="Christmas in July",
        trigger=triggers.on_date(7, 25),
        collection=collections.CHRISTMAS_FESTIVAL_EVENT,
        hours=(12, 24)
    )
]

# 2. SEASONAL BLOCKS
PRIMETIME_FEATURE = SeasonalBlock(
    base=collections.NEW_HOLLYWOOD_CINEMA,
    seasonal={
        "SUMMER": Swap(collections.MODERN_BLOCKBUSTERS),
        "FALL": Swap(collections.NOIR_NIGHT),
        "WINTER": Swap(collections.GOLDEN_AGE_CINEMA),
        "SPRING": Swap(collections.MUSICAL_MARQUEE),
    }
)

AFTERNOON_FEATURE = SeasonalBlock(
    base="classic_hollywood_movie",
    seasonal={
        "WINTER": Feather("classic_hollywood_winter_movies", 0.4),
        "SUMMER": Feather("classic_hollywood_summer_movies", 0.4),
        "SPRING": Feather("musical_movie", 0.3),
        "FALL": Feather("classic_noir_movie", 0.3)
    }
)

# 3. HOLIDAY SCHEDULES
HALLOWEEN_SCHEDULE = {
    "prime": collections.HALLOWEEN_MARATHON_EVENT
}

CHRISTMAS_SCHEDULE = {
    "afternoon": collections.CHRISTMAS_FESTIVAL_EVENT,
    "prime": collections.CHRISTMAS_FESTIVAL_EVENT
}

# 4. SCHEDULES
SCHEDULES = {
    "WEEKDAY": {
        "overnight": collections.NOIR_NIGHT,
        "morning": collections.GOLDEN_AGE_CINEMA,
        "afternoon": AFTERNOON_FEATURE,
        "prime": PRIMETIME_FEATURE
    },
    "WEEKEND": {
        "overnight": collections.NOIR_NIGHT,
        "morning": collections.SILENT_CINEMA,
        "afternoon": collections.WESTERN_MATINEE,
        "prime": collections.SCI_FI_SHOWCASE
    }
}

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
        marathons=MARATHONS,
        holiday_schedules={
            "HALLOWEEN": HALLOWEEN_SCHEDULE,
            "CHRISTMAS": CHRISTMAS_SCHEDULE
        },
        block_profiles={
            "HALLOWEEN": STANDARD_PROFILES, # TODO: Use specific Halloween profile
            "CHRISTMAS": CHRISTMAS_PROFILES
        },
        timeslot_preset="movies",
        logger=ChannelLogger(prefix="[MOVIES]"),
        fallback_content=collections.GOLDEN_AGE_CINEMA
    )
    return run_daily_schedule(api, context, build_id, config)