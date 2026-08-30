"""
Classic Movies Channel - Timeless Cinema

Programming Philosophy:
- Overnight: Film noir and dark classics
- Morning: Golden Age Hollywood (1930s-1950s)
- Afternoon: Seasonal themed classics
- Prime: Era-specific seasonal showcases

Seasonal Strategy:
- Summer: New Hollywood, unswapped (modern blockbusters are not this channel's)
- Fall: Noir and mystery take over
- Winter: Return to Golden Age classics
- Spring: Musicals and romantic comedies

Holiday Events:
- Halloween: Marathon event programming
- Christmas: Festival programming (afternoon + prime)
- Christmas in July: Special marathon (July 25)
"""
from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.models import Marathon, Swap, Feather
from scripts.logic import triggers
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.library import movies
from scripts.logic.factories import themed_marathon
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. MARATHONS - Special event programming
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Christmas in July",
        trigger=triggers.on_date(7, 25),
        collection=movies.CHRISTMAS_FESTIVAL_EVENT,
        hours=(12, 24)
    ),
    Marathon(
        name="Groundhog Day Marathon",
        trigger=triggers.has_label("GROUNDHOGS_DAY"),
        collection=themed_marathon(
            show_title="Groundhog Day",
            title="Groundhog Day Marathon",
            is_movie=True
        ),
        hours=(6, 24) # All day
    )
]

# ==============================================================================
# 2. HOLIDAY SCHEDULES
# ==============================================================================

HALLOWEEN_SCHEDULE = {
    "prime": movies.HALLOWEEN_MARATHON_EVENT
}

CHRISTMAS_SCHEDULE = {
    "afternoon": movies.CHRISTMAS_FESTIVAL_EVENT,
    "prime": movies.CHRISTMAS_FESTIVAL_EVENT
}

# ==============================================================================
# 4. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "overnight": movies.NOIR_NIGHT,
        "morning": movies.GOLDEN_AGE_CINEMA,
        "afternoon": movies.MOVIE_AFTERNOON_FEATURE,
        "prime": movies.MOVIE_PRIMETIME_FEATURE
    },
    "WEEKEND": {
        "overnight": movies.NOIR_NIGHT,
        "morning": movies.SILENT_CINEMA,
        "afternoon": movies.WESTERN_MATINEE,
        # Was SCI_FI_SHOWCASE, which Other Worlds also hands its Saturday prime.
        # Neither channel ever drew the same key -- they picked different arms
        # of the same collection -- so both ran sci-fi features 20:00-24:00
        # every Saturday without anything flagging it.
        "prime": movies.WEEKEND_MARQUEE
    }
}

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
        marathons=MARATHONS,
        holiday_schedules={
            "HALLOWEEN": HALLOWEEN_SCHEDULE,
            "CHRISTMAS": CHRISTMAS_SCHEDULE
        },
        block_profiles={},
        timeslot_preset="movies",
        logger=ChannelLogger(prefix="[MOVIES]"),
        fallback_content=movies.GOLDEN_AGE_CINEMA,
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)