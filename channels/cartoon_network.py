"""
Cartoon Network - the vault, the cartoons, Toonami, Adult Swim

Four brands on one dial position, in the order the day actually ran them. The
restructure that produced this grid is written up in
reference/cartoon-network-review.md; the short version is that the channel was
giving 27 hours a week to Disney and 13 to Nickelodeon while Cartoon Network's
own originals held five, and that Adult Swim was running 20:00-02:00 with
Hanna-Barbera behind it until 06:00 -- the exact inverse of the real thing.

Schedule shape:
- Overnight (02-06): Adult Swim, the acquisitions -- Toonami on Saturday
- Early     (06-08): The Vault
- Morning   (08-10): Cartoon Cartoons -- Saturday Morning, Scooby on Sunday
- Midday    (10-12): Cartoon Network, the modern shows
- Noon      (12-14): The Vault -- Syndication Hour Saturday, a film Sunday
- Afternoon (14-17): Action Hour, Marvel-led in spring
- Evening   (17-20): TOONAMI -- Cartoon Cartoon Fridays, Toonami Saturday
- Prime     (20-23): Adult Swim, originals -- FOX Primetime on Sunday
- Night     (23-24): The Midnight Run -- its premiere hour on Friday
- After hrs (00-02): The Midnight Run, the deeper cuts

Summer (June-August) hands 08:00-14:00 on weekdays to CN's own shows and takes
the vault out of the lunchtime slot -- the one seasonal change the channel most
wanted and the only season that had no variant at all.

No sharing rules. Everything this channel used to hold for Disney or Nick has
gone back: DISNEY_MORNING, DISNEY_AFTERNOON, Gargoyles, the Star Wars Day
marathon, the Nicktoons Vault, Daria, Animaniacs and Pinky and the Brain. The
Halloween schedule no longer reaches for Gravity Falls either -- it has its own
collection now. See reference/channel-plan.md.
"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework - Orchestration
from scripts.scheduling import run_daily_schedule, ScheduleConfig

# Framework - Logic
from scripts.logic.models import Marathon
from scripts.logic import triggers

# Framework - Content
from scripts.library import animation, common
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================

# The default preset wraps the night as a single 23:00-02:00 slot, which this
# channel cannot use for two reasons.
#
# A wrapping slot is entered twice -- once at 23:00 under one day's label and
# again at 00:00 under the next -- so "Sunday night" resolves to Sunday 00:00
# and Sunday 23:00, two different nights, and a DailyOrderedCollection resets
# across the boundary and replays its first items. Splitting at midnight names
# the two halves separately: night is the last hour of the evening, after_hours
# is the first two of the morning, and each carries its own block.
#
# Nick and Disney carry their own maps for the same reason.
CARTOON_NETWORK_TIMESLOTS = {
    "after_hours": (0, 2),
    "overnight":   (2, 6),
    "early":       (6, 8),
    "morning":     (8, 10),
    "midday":      (10, 12),
    "noon":        (12, 14),
    "afternoon":   (14, 17),
    "evening":     (17, 20),
    "prime":       (20, 23),
    "night":       (23, 24),
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

# Date-anchored, with a small random chance kept on top. Previously all five
# were pure chance at 1-2%, which is about one marathon every three weeks
# spread over five different events -- often enough to be an accident, never
# often enough to be a tradition. Real CN ran these as appointments.
#
# The Simpsons marathon is gone. It held 16:00-22:00, and The Simpsons is Fox
# and never aired on Cartoon Network; six hours of it was the wrong flag on
# this channel. Star Wars Day is gone too -- it is Disney's, and used to run
# against Disney's own.
MARATHONS = [
    Marathon(
        name="Toonami Thanksgiving",
        trigger=triggers.any_of(
            triggers.has_label("THANKSGIVING"),
            triggers.chance(0.01, "toonami_takeover")
        ),
        collection=animation.TOONAMI_MARATHON,
        hours=(10, 24),
        priority=3
    ),
    Marathon(
        name="Toonami New Year's Eve",
        trigger=triggers.has_label("NEW_YEARS_EVE"),
        collection=animation.TOONAMI_MARATHON,
        hours=(12, 24),
        priority=3
    ),
    Marathon(
        name="DBZ Marathon",
        trigger=triggers.any_of(
            triggers.has_label("JULY_4"),
            triggers.chance(0.02, "dbz_takeover")
        ),
        collection=animation.DBZ_SAGAS,
        hours=(10, 24),
        priority=2
    ),
    Marathon(
        name="Cowboy Bebop",
        trigger=triggers.any_of(
            triggers.has_label("MEMORIAL_DAY"),
            triggers.chance(0.01, "bebop_marathon")
        ),
        collection=animation.COWBOY_BEBOP_COMPLETE,
        hours=(10, 24),
        priority=2
    ),
    # Daytime only, and the lowest priority of the five: it gives up the slot
    # to any of the anime marathons above and never touches Adult Swim.
    Marathon(
        name="Cartoon Network Marathon",
        trigger=triggers.has_label("FIRST_SATURDAY"),
        collection=animation.CN_MARATHON,
        hours=(10, 17),
        priority=1
    ),
]

# ==============================================================================
# 3. BLOCK VARIANTS
# ==============================================================================

# Everything from 23:00 on is labelled by the calendar day it falls in, not by
# the evening it belongs to. Saturday night runs Sat 23:00 -> Sun 06:00, so the
# Toonami overnight is keyed SUNDAY; Adult Swim's Sunday night runs Sun 23:00
# -> Mon 06:00, so its small hours are keyed MONDAY.

# 02:00-06:00. Saturday night's tail is Toonami rather than the acquisitions --
# the Midnight Run is what those hours were for before Adult Swim existed.
OVERNIGHT_BLOCK = {
    "SUNDAY": animation.TOONAMI_MIDNIGHT_RUN,
    "default": animation.AS_LATE,
}

MORNING_BLOCK = {
    "SATURDAY": animation.SATURDAY_MORNING,
    "SUNDAY": animation.THE_SCOOBY_BLOCK,
    "default": animation.CARTOON_CARTOONS,
}

# Sunday takes the vault an hour earlier than the rest of the week, so the
# afternoon can hold three hours of the modern shows.
MIDDAY_BLOCK = {
    "SATURDAY": animation.CARTOON_CARTOONS,
    "SUNDAY": animation.THE_VAULT,
    "default": animation.CN_MIDDAY_BLOCK,
}

NOON_BLOCK = {
    "SATURDAY": animation.SYNDICATION_HOUR,
    "SUNDAY": animation.CARTOON_THEATRE,
    "default": animation.CN_NOON_BLOCK,
}

AFTERNOON_BLOCK = {
    "SUNDAY": animation.CN_MODERN,
    "default": animation.CN_AFTERNOON_BLOCK,
}

# FRIDAY comes before WEEKDAY in the dict, and the resolver takes the first
# label that matches -- Cartoon Cartoon Fridays takes the Toonami slot.
EVENING_BLOCK = {
    "FRIDAY": animation.CARTOON_CARTOON_FRIDAY,
    "SATURDAY": animation.TOONAMI_SATURDAY,
    "SUNDAY": animation.CARTOON_CARTOONS,
    "default": animation.TOONAMI_BLOCK,
}

PRIME_BLOCK = {
    "SATURDAY": animation.TOONAMI_SATURDAY_VAULT,
    "SUNDAY": animation.FOX_PRIMETIME,
    "WEEKDAY_A": animation.AS_ORIGINALS_A,  # Mon/Wed/Fri
    "default": animation.AS_ORIGINALS_B,    # Tue/Thu/Sat
}

# 23:00-24:00. Sunday is the one night the originals run late instead of the
# anime -- Adult Swim launched on a Sunday, and it is the only night of the
# week with no Toonami anywhere in it. Friday gets the premiere variant, which
# is the only night Attack on Titan Junior High airs.
NIGHT_BLOCK = {
    "FRIDAY": animation.MIDNIGHT_RUN_PREMIERE,
    "SUNDAY": animation.AS_ORIGINALS_B,
    "default": animation.MIDNIGHT_RUN,
}

# 00:00-02:00. MONDAY here is Sunday night, following AS_ORIGINALS_B through
# the midnight boundary rather than cutting to anime halfway.
AFTER_HOURS_BLOCK = {
    "MONDAY": animation.AS_ORIGINALS_B,
    "default": animation.MIDNIGHT_RUN_LATE,
}

# ==============================================================================
# 4. HOLIDAY SCHEDULES
# ==============================================================================

# The channel gets older as the night goes on, and Halloween follows it: the
# vault and the morning stay kid-safe, the middle of the day is CN's own two
# Halloween shows, and only the Adult Swim hours reach the adult collections.
HALLOWEEN_SCHEDULE = {
    "overnight": common.HALLOWEEN_ADULT_SCARES,
    "early":     common.HALLOWEEN_KIDS_SPOOKFEST,
    "morning":   common.HALLOWEEN_KIDS_SPOOKFEST,
    "midday":    animation.CN_HALLOWEEN,
    "noon":      animation.CN_HALLOWEEN,
    "afternoon": animation.CN_HALLOWEEN,
    "evening":   animation.CN_HALLOWEEN,
    "prime":     common.HALLOWEEN_TV_EVENT,
    "night":     common.HALLOWEEN_ADULT_SCARES,
    "after_hours": common.HALLOWEEN_ADULT_SCARES,
}

CHRISTMAS_SCHEDULE = {
    "overnight": common.CHRISTMAS_TV_EVENT,
    "early":     common.CHRISTMAS_TV_EVENT,
    "morning":   common.CHRISTMAS_TV_EVENT,
    "midday":    common.CHRISTMAS_TV_EVENT,
    "noon":      common.CHRISTMAS_TV_EVENT,
    "afternoon": common.CHRISTMAS_TV_EVENT,
    "evening":   common.CHRISTMAS_TV_EVENT,
    "prime":     "christmas_animated_movie",
    "night":     common.CHRISTMAS_TV_EVENT,
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
    "after_hours": AFTER_HOURS_BLOCK,
    "overnight": OVERNIGHT_BLOCK,
    "early":     animation.THE_VAULT,
    "morning":   MORNING_BLOCK,
    "midday":    MIDDAY_BLOCK,
    "noon":      NOON_BLOCK,
    "afternoon": AFTERNOON_BLOCK,
    "evening":   EVENING_BLOCK,
    "prime":     PRIME_BLOCK,
    "night":     NIGHT_BLOCK,
}

# One key, not two. "WEEKDAY" is the framework's default in
# `assemble_day_schedule` -- it is what you get when no other key matches a
# day label -- so a second "WEEKEND" key pointing at the same dict did nothing
# but suggest a weekend grid that does not exist. Every day-of-week difference
# on this channel lives in the per-slot variant dicts above.
SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
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
        holiday_schedules=HOLIDAY_SCHEDULES,
        timeslot_preset=CARTOON_NETWORK_TIMESLOTS,
        block_profiles={},  # Use defaults from HOLIDAY_PROFILES

        # No channel-level filler or bumpers.
        #
        # This used to be `filler_content="adult_swim_bumpers"`, which only the
        # five branded blocks overrode -- so roughly 14 hours of every 24,
        # Saturday-morning Scooby-Doo included, ran Adult Swim bumps between
        # shows. There is no daytime replacement available:
        # `filler/bumpers/cartoon network/general/` is empty, and the 110 files
        # tagged `commercials/90s` are mislabelled 2000s British adverts. Until
        # one of those two is fixed, silence is more Cartoon Network than Adult
        # Swim is. Toonami and Adult Swim carry their own branding per block,
        # and now their own per-show bumper sets per item.
        # See reference/bumper-inventory.md.
        filler_content=None,
        bumpers=None,

        logger=ChannelLogger(prefix="[CARTOONS]"),
        # A plain content key, not a Block or a Collection. `circuit_breaker`
        # hands fallback_content straight to `play_item` with no resolution
        # step, so anything that is not already a key silently fails to play
        # and the breaker's "fallback succeeded" is a lie. `animated_classic_tv`
        # is the vault by query -- pre-1970 animation -- which is what this
        # channel should be showing if everything else has fallen over.
        fallback_content="animated_classic_tv",
        enable_marathons=True,
        enable_filler=False,
        enable_bumpers=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
    )

    return run_daily_schedule(api, context, build_id, config)
