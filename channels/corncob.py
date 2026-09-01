"""
Corncob TV (242) -- comedy after the laugh track

Single-camera, cable, streaming, sketch and alt. The line against Good Times is
the studio audience and not the year, so Freaks and Geeks (1999) and The Larry
Sanders Show (1992) are here while Frasier (1993) is not.

Axis: **the clock gets stranger.** The morning is the network single-camera
sitcom, the afternoon is the office comedies, the evening is cable, and the
small hours are the far end of the channel. Nightmare Theatre's shape in a
different register -- and it means era is not the axis and does not need to be.

Built 2026-09-01, when Good Times was rebuilt on the laugh-track line and this
channel's brief widened from "absurd comedy" to take everything on the far side
of it. It inherits Must See Thursday -- The Office, Parks and Recreation, 30
Rock and Community -- which had been four stacked `annual_show` appointments in
one Good Times slot and the standing example for rule G5.

The roster, the named nights and the one hours rule that matters (Cartoon
Network's Adult Swim, two shared titles) are in the docstring of
`scripts/library/comedy.py`.
"""

from etv_client.models import ControlWaitUntil

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import comedy

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Ten slots, none wrapping midnight (G1). The same map Cartoon Network and Nick
# carry, which is deliberate: the one sharing rule on this channel is against
# Adult Swim, and having the two grids on the same slot boundaries makes "Adult
# Swim is never on air at 10:00-12:00" a fact you can read off both files
# rather than a claim you have to simulate to believe.

CORNCOB_TIMESLOTS = {
    "after_hours": (0, 2),     # The Deep End
    "overnight":   (2, 6),     # The Vault
    "early":       (6, 8),     # Sign-On
    "morning":     (8, 10),    # The Morning Bench     -- monthly, 3 pools
    "midday":      (10, 12),   # The Syndication Hour
    "noon":        (12, 14),   # The Noon Hour         -- one show, one day
    "afternoon":   (14, 17),   # The Workplace
    "evening":     (17, 20),   # The Cable Hour        -- monthly, 4 pools
    "prime":       (20, 23),   # the named night
    "late":        (23, 24),   # The Late Shift / the Limited Series on Sunday
}

# ==============================================================================
# 2. SCHEDULE
# ==============================================================================
#
# One grid. Unlike Good Times, the day-of-week difference here lives *inside*
# three slots -- noon, prime and late are weekday-keyed dicts the resolver
# unwraps -- rather than in seven schedule arms, because the clock means the
# same thing every day on this channel. That is the axis: Tuesday at eleven and
# Saturday at eleven are both the far end of the night.

DAILY_SCHEDULE = {
    "after_hours": comedy.THE_DEEP_END,
    "overnight":   comedy.THE_VAULT,
    "early":       comedy.SIGN_ON,
    "morning":     comedy.MORNING_BENCH,
    "midday":      comedy.SYNDICATION_HOUR,
    "noon":        comedy.NOON_HOUR,
    "afternoon":   comedy.WORKPLACE_BLOCK,
    "evening":     comedy.CABLE_HOUR,
    "prime": {
        "MONDAY":    comedy.MON_PRIME,
        "TUESDAY":   comedy.TUE_PRIME,
        "WEDNESDAY": comedy.WED_PRIME,
        "THURSDAY":  comedy.THU_PRIME,
        "FRIDAY":    comedy.FRI_PRIME,
        "SATURDAY":  comedy.SAT_PRIME,
        "SUNDAY":    comedy.SUN_PRIME,
    },
    "late":        comedy.LATE_SHIFT,
}

# "WEEKDAY" is the framework default in `assemble_day_schedule` -- what you get
# when no other arm matches -- so one key covers every day. A second "WEEKEND"
# arm pointing at the same dict would only suggest a weekend grid that does not
# exist; see the same note on Cartoon Network.
SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
}

# ==============================================================================
# 3. HOLIDAY SCHEDULES
# ==============================================================================
#
# Prime keeps its named night through Halloween and Thanksgiving -- an
# appointment that vanishes on a holiday is not an appointment -- and gives way
# only for Christmas.

HALLOWEEN_SCHEDULE = {
    "morning":   comedy.HALLOWEEN_EVENT,
    "midday":    comedy.HALLOWEEN_EVENT,
    "noon":      comedy.HALLOWEEN_EVENT,
    "afternoon": comedy.HALLOWEEN_EVENT,
    "evening":   comedy.HALLOWEEN_EVENT,
    "late":      comedy.HALLOWEEN_EVENT,
}

THANKSGIVING_SCHEDULE = {
    "morning":   comedy.THANKSGIVING_EVENT,
    "midday":    comedy.THANKSGIVING_EVENT,
    "noon":      comedy.THANKSGIVING_EVENT,
    "afternoon": comedy.THANKSGIVING_EVENT,
    "evening":   comedy.THANKSGIVING_EVENT,
}

CHRISTMAS_SCHEDULE = {
    "morning":   comedy.CHRISTMAS_EVENT,
    "midday":    comedy.CHRISTMAS_EVENT,
    "noon":      comedy.CHRISTMAS_EVENT,
    "afternoon": comedy.CHRISTMAS_EVENT,
    "evening":   comedy.CHRISTMAS_EVENT,
    "prime":     comedy.CHRISTMAS_EVENT,
    "late":      comedy.CHRISTMAS_EVENT,
}

HOLIDAY_SCHEDULES = {
    "HALLOWEEN":    HALLOWEEN_SCHEDULE,
    "THANKSGIVING": THANKSGIVING_SCHEDULE,
    "CHRISTMAS":    CHRISTMAS_SCHEDULE,
}

# ==============================================================================
# 4. ERSATZTV INTEGRATION
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
        timeslot_preset=CORNCOB_TIMESLOTS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        block_profiles={},
        logger=ChannelLogger(prefix="[CORNCOB]"),
        # Twelve titles none of which Cartoon Network airs, so a stall cannot
        # land the channel on Adult Swim's two shared shows at Adult Swim's
        # hours. See library/comedy.py.
        fallback_content=comedy.CHANNEL_FALLBACK,
        # No bumpers: there are no Corncob assets on disk and G12 says ship
        # with none rather than borrow another channel's branding. Adult Swim
        # bumpers exist and are Cartoon Network's; using them here would put
        # its branding on a channel it does not own.
        enable_bumpers=False,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
    )

    return run_daily_schedule(api, context, build_id, config)
