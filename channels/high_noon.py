"""
High Noon - Westerns

The black-and-white network western, stripped, plus a film shelf and a modern
appointment at eight.

Days are the spine: three half-hour shows through the morning, the noon feature
the channel is named after, then Bonanza all afternoon and the hour-longs into
the evening. Nights are the six serialized modern westerns, one a night, one
season a year each, with a western feature on the bed between seasons.

Saturday drops the appointment for a four-hour film night; Sunday keeps Bass
Reeves and gives the afternoon to a matinee double bill.

The channel owns `western_movie` outright. Cabes Classic Cinema ran all 46
films across both weekend afternoons and handed the pool back when this was
built -- the same eviction Other Worlds got for science fiction. Its
`classic_hollywood_pure_movie` key now excludes westerns too, which keeps The
Searchers and the Leone trilogy off its weekday afternoon.

No filler and no bumpers: there are no western assets on disk.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic import triggers, Marathon
from scripts.library import western
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# The channel carries its own map for two reasons.
#
# Prime is 20:00-22:00, not the default 20:00-23:00. The appointment is two
# episodes of a 45-minute cable drama; a three-hour slot leaves an hour of bed
# behind it every night and the block stops reading as an appointment.
#
# And the default's `night: (23, 2)` wraps midnight. A wrapping slot is entered
# twice under two different day labels, so "Saturday night" resolves to two
# different nights and a collection replays its first items across the
# boundary -- the bug Cartoon Network, Nick and Disney each carry their own map
# to avoid. Here `late` is 22-24 and `night` is 00-02, each with its own slot.

HIGH_NOON_TIMESLOTS = {
    "night":     (0, 2),     # film
    "overnight": (2, 6),     # The Long Ride
    "early":     (6, 8),     # Wanted: Dead or Alive
    "morning":   (8, 10),    # The Rifleman
    "midday":    (10, 12),   # Gunsmoke
    "noon":      (12, 14),   # HIGH NOON -- the feature
    "afternoon": (14, 17),   # Bonanza
    "evening":   (17, 20),   # the hour-longs
    "prime":     (20, 22),   # the appointment
    "late":      (22, 24),   # film
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    Marathon(
        name="The Dollars Trilogy",
        trigger=triggers.chance(0.02, "dollars_trilogy"),
        collection=western.DOLLARS_TRILOGY,
        hours=(18, 24),
        priority=1
    ),
    Marathon(
        name="Fourth of July Westerns",
        trigger=triggers.has_label("JULY_4"),
        collection=western.PATRIOTIC_WESTERNS,
        hours=(12, 24),
        priority=2
    ),
    Marathon(
        name="Memorial Day Westerns",
        trigger=triggers.has_label("MEMORIAL_DAY"),
        collection=western.PATRIOTIC_WESTERNS,
        hours=(12, 24),
        priority=2
    )
]

# ==============================================================================
# 3. BLOCK DEFINITIONS
# ==============================================================================

# One appointment per night, gated by the weekday label rather than by the
# appointment's own `frequency` -- `frequency` paces an episode index, it does
# not stop the show airing on other days. Saturday is deliberately absent and
# falls through to the Saturday schedule's own film night.
PRIME_BLOCK = {
    "MONDAY":    western.MONDAY_NIGHT,
    "TUESDAY":   western.TUESDAY_NIGHT,
    "WEDNESDAY": western.WEDNESDAY_NIGHT,
    "THURSDAY":  western.THURSDAY_NIGHT,
    "FRIDAY":    western.FRIDAY_NIGHT,
    "SUNDAY":    western.SUNDAY_NIGHT,
    "default":   western.SATURDAY_NIGHT_FEATURE
}

# ==============================================================================
# 4. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "night":     western.LATE_FEATURE,
        "overnight": western.THE_LONG_RIDE,
        "early":     western.WANTED_DEAD_OR_ALIVE,
        "morning":   western.THE_RIFLEMAN,
        "midday":    western.DODGE_CITY,
        "noon":      western.HIGH_NOON_FEATURE,
        "afternoon": western.THE_PONDEROSA,
        "evening":   western.THE_TRAIL_DRIVE,
        "prime":     PRIME_BLOCK,
        "late":      western.LATE_FEATURE
    },
    # Saturday is the film day. The morning keeps the half-hour strip -- it is
    # the closest this library gets to a Saturday-morning show -- Brisco County
    # takes the evening, and 20:00 through midnight is four unbroken hours of
    # feature rather than an appointment plus a bed.
    "SATURDAY": {
        "night":     western.LATE_FEATURE,
        "overnight": western.THE_LONG_RIDE,
        "early":     western.HALF_HOUR_WEST,
        "morning":   western.HALF_HOUR_WEST,
        "midday":    western.THE_RIFLEMAN,
        "noon":      western.HIGH_NOON_FEATURE,
        "afternoon": western.WEEKEND_MATINEE,
        "evening":   western.BRISCO_COUNTY,
        "prime":     western.SATURDAY_NIGHT_FEATURE,
        "late":      western.SATURDAY_NIGHT_FEATURE
    },
    "SUNDAY": {
        "night":     western.LATE_FEATURE,
        "overnight": western.THE_LONG_RIDE,
        "early":     western.HALF_HOUR_WEST,
        "morning":   western.DODGE_CITY,
        "midday":    western.WANTED_DEAD_OR_ALIVE,
        "noon":      western.HIGH_NOON_FEATURE,
        "afternoon": western.WEEKEND_MATINEE,
        "evening":   western.THE_PONDEROSA,
        "prime":     PRIME_BLOCK,
        "late":      western.LATE_FEATURE
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
        timeslot_preset=HIGH_NOON_TIMESLOTS,
        logger=ChannelLogger(prefix="[HIGH NOON]"),
        # The spine, not the film shelf. A stall at 08:00 should drop into
        # another half-hour western, not open a two-hour feature mid-morning.
        fallback_content="classic_western_tv",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
