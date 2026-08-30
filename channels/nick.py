"""
Nick - Nicktoons by day, Nick at Nite by night

Two identities on one channel, split at 21:00.

Daytime is a rotation problem before it is a programming problem: eight Nick
cartoons cannot fill a day without repeating into the ground, so four of the
strips ride a four-pool `monthly_rotation()` bench that brings the WB trio and
the educational set into the mix a month at a time. The four start the cycle at
four different months, so no two of them show the same pool on the same day.

Schedule shape:
- After hours (00-02): Nick at Nite, the 70s shift
- Overnight  (02-06): monthly bench
- Early      (06-08): educational shorts
- Morning    (08-10): monthly bench
- Midday     (10-12): monthly bench, one pool along
- Noon       (12-14): Nicktoons Classic, Teen Nick at the weekend
- Afternoon  (14-17): monthly bench, one pool along again
- Evening    (17-19): the Avatar strip -- chronological weekdays, shuffled weekends
- Prime      (19-21): Teen Nick, SNICK on Saturday
- Nite       (21-24): Nick at Nite

Sharing rule: Good Times (scripts/channels/sitcoms.py) shares the whole Nick at
Nite lineup and keeps clear of 21:00-02:00. See reference/channel-plan.md.
"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework - Orchestration
from scripts.scheduling import run_daily_schedule, ScheduleConfig

# Framework - Content
from scripts.library import nickelodeon, common
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================

# Nick at Nite is 21:00-02:00, which the default preset cannot express: it puts
# prime at 20-23 and night at 23-02. Splitting the night at midnight also gives
# the block its two halves -- pre-1970 before, the 70s after.
NICK_TIMESLOTS = {
    "after_hours": (0, 2),
    "overnight":   (2, 6),
    "early":       (6, 8),
    "morning":     (8, 10),
    "midday":      (10, 12),
    "noon":        (12, 14),
    "afternoon":   (14, 17),
    "evening":     (17, 19),
    "prime":       (19, 21),
    "nite":        (21, 24),
}

# ==============================================================================
# 2. BLOCK VARIANTS
# ==============================================================================

# Saturday keeps the cartoons where they belong; Sunday leans educational.
MORNING_BLOCK = {
    "SATURDAY": nickelodeon.WB_ANIMATION,
    "SUNDAY": nickelodeon.NICK_EDUCATIONAL,
    "default": nickelodeon.MORNING_BENCH,
}

NOON_BLOCK = {
    "WEEKEND": nickelodeon.NICK_TEEN,
    "default": nickelodeon.NICKTOONS_CLASSIC,
}

PRIME_BLOCK = {
    "SATURDAY": nickelodeon.SNICK,
    "default": nickelodeon.NICK_TEEN,
}

# ==============================================================================
# 3. HOLIDAY SCHEDULES
# ==============================================================================

# Daytime stays kid-safe; the night block takes the general TV event, since its
# audience at that hour is the one watching Nick at Nite in the first place.
HALLOWEEN_SCHEDULE = {
    "overnight":   common.HALLOWEEN_KIDS_SPOOKFEST,
    "early":       common.HALLOWEEN_KIDS_SPOOKFEST,
    "morning":     common.HALLOWEEN_KIDS_SPOOKFEST,
    "midday":      common.HALLOWEEN_KIDS_SPOOKFEST,
    "noon":        common.HALLOWEEN_KIDS_SPOOKFEST,
    "afternoon":   common.HALLOWEEN_TEEN_FRIGHTS,
    "evening":     common.HALLOWEEN_TEEN_FRIGHTS,
    "prime":       common.HALLOWEEN_TEEN_FRIGHTS,
    "nite":        common.HALLOWEEN_TV_EVENT,
    "after_hours": common.HALLOWEEN_TV_EVENT,
}

CHRISTMAS_SCHEDULE = {
    "morning":     common.CHRISTMAS_TV_EVENT,
    "midday":      common.CHRISTMAS_TV_EVENT,
    "noon":        common.CHRISTMAS_TV_EVENT,
    "afternoon":   common.CHRISTMAS_TV_EVENT,
    "evening":     common.CHRISTMAS_TV_EVENT,
    "prime":       common.CHRISTMAS_TV_EVENT,
    "nite":        common.CHRISTMAS_TV_EVENT,
    "after_hours": common.CHRISTMAS_TV_EVENT,
}

HOLIDAY_SCHEDULES = {
    "HALLOWEEN": HALLOWEEN_SCHEDULE,
    "CHRISTMAS": CHRISTMAS_SCHEDULE,
}

# ==============================================================================
# 4. SCHEDULE
# ==============================================================================

DAILY_SCHEDULE = {
    "after_hours": nickelodeon.NICK_AT_NITE_AFTER_HOURS,
    "overnight":   nickelodeon.OVERNIGHT_BENCH,
    "early":       nickelodeon.NICK_EDUCATIONAL,
    "morning":     MORNING_BLOCK,
    "midday":      nickelodeon.MIDDAY_BENCH,
    "noon":        NOON_BLOCK,
    "afternoon":   nickelodeon.AFTERNOON_BENCH,
    "evening":     nickelodeon.AVATAR_STRIP,
    "prime":       PRIME_BLOCK,
    "nite":        nickelodeon.NICK_AT_NITE,
}

SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
    "WEEKEND": DAILY_SCHEDULE,
}

# ==============================================================================
# 5. ERSATZTV INTEGRATION
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
        timeslot_preset=NICK_TIMESLOTS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        block_profiles={},
        # Schoolhouse Rock is three minutes a piece -- the pad the channel
        # actually has assets for. There are no Nick bumpers on disk.
        filler_content="schoolhouse_rock_tv",
        fallback_content=nickelodeon.NICKTOONS_CLASSIC,
        logger=ChannelLogger(prefix="[NICK]"),
        enable_filler=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
    )

    return run_daily_schedule(api, context, build_id, config)
