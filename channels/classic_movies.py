"""
Cabes Classic Cinema - Hollywood before the blockbuster, 1920-1979

The day walks forward through film history and resets at midnight:

    00-03  Noir Alley          the pre-1980 crime shelf
    03-06  The Small Hours     the whole library, shuffled
    06-09  Silent Cinema       silents over early sound
    09-12  The Golden Age      1930-49
    12-17  The Matinee         1950-69, seasonally tilted
    17-20  The Big Picture     epics, war, musicals
    20-24  New Hollywood       the 1970s -- the appointment

That is the channel's organizing idea, and it is the answer to the question
this file could not previously answer: **what is Cabes Classic Cinema?** It is
everything before 1980, arranged so the hour of the day tells you the decade.

It carries its own timeslot map for the same reason High Noon and Nightmare
Theatre do. The "movies" preset's four six-hour blocks cannot express a grid
that changes character seven times, and running that preset is a large part of
why the channel read as a residue: four slots is not enough structure to have
an identity, only enough to hold content.

The 1980s are gone -- to Totally 80s, whose theme they are, and to Be Kind
Rewind, whose oldest shelf they are. See `library/movies.py` for what that
cost and why it was worth it.
"""
from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic.models import Marathon
from scripts.logic import triggers
from scripts.library import movies
from scripts.logic.factories import themed_marathon, monthly_rotation
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Seven slots, none shorter than three hours, because the mean running time on
# this channel is around 110 minutes and a two-hour daypart cuts a feature in
# half. No slot wraps midnight: a wrapping slot is entered twice under two day
# labels, which is the bug every hand-built map on this lineup exists to avoid.

CLASSIC_TIMESLOTS = {
    "night":     (0, 3),     # Noir Alley
    "overnight": (3, 6),     # The Small Hours
    "early":     (6, 9),     # Silent Cinema
    "morning":   (9, 12),    # The Golden Age
    "afternoon": (12, 17),   # The Matinee
    "evening":   (17, 20),   # The Big Picture
    "prime":     (20, 24),   # New Hollywood
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    # Kept from the channel's earlier configuration. It is the one piece of
    # deliberate silliness on a channel that is otherwise entirely straight,
    # and the pool it draws is pre-1980 Christmas film, so it stays in era.
    Marathon(
        name="Christmas in July",
        trigger=triggers.on_date(7, 25),
        collection=movies.CHRISTMAS_FESTIVAL_EVENT,
        hours=(12, 24),
        priority=2
    ),
    Marathon(
        name="Groundhog Day Marathon",
        trigger=triggers.has_label("GROUNDHOGS_DAY"),
        collection=themed_marathon(
            show_title="Groundhog Day",
            title="Groundhog Day Marathon",
            is_movie=True,
        ),
        hours=(6, 24),
        priority=2
    )
]

# ==============================================================================
# 3. BLOCK DEFINITIONS
# ==============================================================================

# The Big Picture, Sunday only: the evening becomes a director spotlight that
# alternates by month. Hitchcock is twelve films and Kubrick four, so a month
# each is roughly a full pass through Hitchcock and three passes through
# Kubrick -- which is why the wide block sits underneath them the rest of the
# week rather than the spotlights carrying the slot seven nights.
SUNDAY_EVENING = monthly_rotation([
    movies.HITCHCOCK_SPOTLIGHT,
    movies.THE_BIG_PICTURE,
    movies.KUBRICK_SPOTLIGHT,
    movies.THE_BIG_PICTURE,
])

# ==============================================================================
# 4. HOLIDAY SCHEDULES
# ==============================================================================

HALLOWEEN_SCHEDULE = {
    "evening": movies.HALLOWEEN_MARATHON_EVENT,
    "prime": movies.HALLOWEEN_MARATHON_EVENT
}

CHRISTMAS_SCHEDULE = {
    "afternoon": movies.CHRISTMAS_FESTIVAL_EVENT,
    "evening": movies.CHRISTMAS_FESTIVAL_EVENT,
    "prime": movies.CHRISTMAS_FESTIVAL_EVENT
}

# ==============================================================================
# 5. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "night":     movies.NOIR_ALLEY,
        "overnight": movies.THE_SMALL_HOURS,
        "early":     movies.SILENT_CINEMA,
        "morning":   movies.GOLDEN_AGE_CINEMA,
        "afternoon": movies.MATINEE_BLOCK,
        "evening":   movies.THE_BIG_PICTURE,
        "prime":     movies.PRIME_BLOCK,
    },
    "SATURDAY": {
        "night":     movies.NOIR_ALLEY,
        "overnight": movies.THE_SMALL_HOURS,
        "early":     movies.SILENT_CINEMA,
        "morning":   movies.GOLDEN_AGE_CINEMA,
        "afternoon": movies.MATINEE_BLOCK,
        "evening":   movies.THE_BIG_PICTURE,
        # Saturday night is the big canvas rather than another 1970s feature --
        # the one night the channel programmes for scale instead of for era.
        "prime":     movies.WEEKEND_MARQUEE,
    },
    "SUNDAY": {
        "night":     movies.NOIR_ALLEY,
        "overnight": movies.THE_SMALL_HOURS,
        "early":     movies.SILENT_CINEMA,
        "morning":   movies.GOLDEN_AGE_CINEMA,
        "afternoon": movies.MATINEE_BLOCK,
        "evening":   SUNDAY_EVENING,
        "prime":     movies.WEEKEND_MARQUEE,
    }
}

# ==============================================================================
# 6. ERSATZTV INTEGRATION
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
        timeslot_preset=CLASSIC_TIMESLOTS,
        logger=ChannelLogger(prefix="[CLASSIC]"),
        # The wide pre-1980 shelf, not an era. A stall anywhere on the grid
        # should drop into a classic feature; the individual era keys are each
        # thin enough that leaning on one would repeat inside a day.
        fallback_content="classic_cinema_movie",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
