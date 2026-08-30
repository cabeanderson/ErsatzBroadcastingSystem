"""
Disney - the afternoon, the morning, and Star Wars after dark

Three eras of one studio plus Lucasfilm, dayparted so they never argue. The
1990 syndication block owns 15:00-17:00 and nothing else on the channel is
allowed to be an appointment in daylight; everything before it is bench.

Schedule shape:
- After hours (00-02): Disney After Dark -- Gargoyles and the modern shows
- Overnight  (02-06): monthly bench
- Early      (06-08): Disney Morning, the ABC cartoons
- Morning    (08-10): monthly bench
- Midday     (10-12): monthly bench, one pool along
- Noon       (12-15): Disney Toons -- everything the Afternoon is not
- Afternoon  (15-17): THE DISNEY AFTERNOON
- Evening    (17-19): the Disney Channel strip -- chronological weekdays
- Prime      (19-21): Star Wars; Tales on Saturday, the movie on Sunday
- Late       (21-24): the Star Wars vault

No sharing rules. Cartoon Network handed back DISNEY_MORNING, DISNEY_AFTERNOON,
Gargoyles and the Star Wars Day marathon in its restructure, so every title here
airs on this channel and nowhere else. Other Worlds draws the Star Wars vault at
06:00 through this channel's `star_wars_animation_tv` key -- different hours from
the 19:00-24:00 strip. See reference/channel-plan.md.
"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework - Orchestration
from scripts.scheduling import run_daily_schedule, ScheduleConfig

# Framework - Logic
from scripts.logic import triggers
from scripts.logic.models import Marathon

# Framework - Content
from scripts.library import disney, common
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================

# The default preset puts afternoon at 14-17 and prime at 20-23. The Disney
# Afternoon is a two-hour block ending at 17:00, and Star Wars wants the two
# hours after it that a kid is still awake for, so the channel carries its own
# map: a 12-15 noon, a 15-17 afternoon, and the night split at 21:00.
DISNEY_TIMESLOTS = {
    "after_hours": (0, 2),
    "overnight":   (2, 6),
    "early":       (6, 8),
    "morning":     (8, 10),
    "midday":      (10, 12),
    "noon":        (12, 15),
    "afternoon":   (15, 17),
    "evening":     (17, 19),
    "prime":       (19, 21),
    "late":        (21, 24),
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Star Wars Day",
        trigger=triggers.has_label("STAR_WARS_DAY"),
        collection=disney.STAR_WARS_MARATHON,
        hours=(8, 22),
        priority=2
    )
]

# ==============================================================================
# 3. BLOCK VARIANTS
# ==============================================================================

# Saturday gets the morning cartoons for four hours instead of two -- the one
# concession the bench makes to the day it was named for.
MORNING_BLOCK = {
    "SATURDAY": disney.DISNEY_MORNING,
    "default": disney.MORNING_BENCH,
}

# Prime is the channel's only three-way split: Saturday is the Star Wars event
# night, Sunday is the movie, and the rest of the week is the strip.
PRIME_BLOCK = {
    "SATURDAY": disney.STAR_WARS_EVENT_NIGHT,
    "SUNDAY": disney.WONDERFUL_WORLD_OF_DISNEY,
    "default": disney.STAR_WARS_STRIP,
}

# ==============================================================================
# 4. HOLIDAY SCHEDULES
# ==============================================================================

# The channel is kid-safe at every hour, so Halloween never reaches for the
# adult collections -- it just gets older as the day goes on, and hands the
# evening to Gravity Falls and The Owl House, which are the two shows on the
# channel that were built for it.
HALLOWEEN_SCHEDULE = {
    "overnight":   common.HALLOWEEN_KIDS_SPOOKFEST,
    "early":       common.HALLOWEEN_KIDS_SPOOKFEST,
    "morning":     common.HALLOWEEN_KIDS_SPOOKFEST,
    "midday":      common.HALLOWEEN_KIDS_SPOOKFEST,
    "noon":        common.HALLOWEEN_KIDS_SPOOKFEST,
    "afternoon":   disney.DISNEY_HALLOWEEN,
    "evening":     disney.DISNEY_HALLOWEEN,
    "prime":       disney.DISNEY_HALLOWEEN,
    "late":        disney.DISNEY_HALLOWEEN,
    "after_hours": disney.DISNEY_HALLOWEEN,
}

CHRISTMAS_SCHEDULE = {
    "morning":     common.CHRISTMAS_TV_EVENT,
    "midday":      common.CHRISTMAS_TV_EVENT,
    "noon":        common.CHRISTMAS_TV_EVENT,
    "afternoon":   common.CHRISTMAS_TV_EVENT,
    "evening":     common.CHRISTMAS_TV_EVENT,
    "prime":       "christmas_animated_movie",
    "late":        common.CHRISTMAS_TV_EVENT,
    "after_hours": common.CHRISTMAS_TV_EVENT,
}

HOLIDAY_SCHEDULES = {
    "HALLOWEEN": HALLOWEEN_SCHEDULE,
    "CHRISTMAS": CHRISTMAS_SCHEDULE,
}

# ==============================================================================
# 5. SCHEDULE
# ==============================================================================

DAILY_SCHEDULE = {
    "after_hours": disney.DISNEY_AFTER_DARK,
    "overnight":   disney.OVERNIGHT_BENCH,
    "early":       disney.DISNEY_MORNING,
    "morning":     MORNING_BLOCK,
    "midday":      disney.MIDDAY_BENCH,
    "noon":        disney.DISNEY_TOONS,
    "afternoon":   disney.THE_DISNEY_AFTERNOON,
    "evening":     disney.DISNEY_CHANNEL_STRIP,
    "prime":       PRIME_BLOCK,
    "late":        disney.STAR_WARS_VAULT,
}

SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
    "WEEKEND": DAILY_SCHEDULE,
}

# ==============================================================================
# 6. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    """ErsatzTV content definition hook (unused in scripted mode)."""
    pass

def reset_playout(api, context, build_id):
    """Reset playout to midnight with rewind."""
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00",
        tomorrow=False,
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    """Build the daily playout schedule."""
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        timeslot_preset=DISNEY_TIMESLOTS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        block_profiles={},
        # No filler: `filler/bumpers/` has cartoon network and fox kids trees
        # and nothing else, and there are no Disney shorts in the library to
        # stand in. See reference/bumper-inventory.md.
        fallback_content=disney.THE_DISNEY_AFTERNOON,
        logger=ChannelLogger(prefix="[DISNEY]"),
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
    )

    return run_daily_schedule(api, context, build_id, config)
