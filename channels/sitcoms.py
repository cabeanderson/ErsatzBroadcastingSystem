"""
Good Times (190) -- the studio audience

Multi-camera network sitcom, 1951-1999. The week is the networks and the day is
that network's history: each weekday belongs to CBS, NBC, ABC or FOX and walks
its roster across the clock, arranged by what fits the hour rather than by date.
Three daytime strips carry a season-keyed book on top, so the daytime reshuffles
four times a year while prime, evening and the overnight stay the spine.

The full design, the roster by network and -- most importantly -- the hours
rules that keep the channel clear of Nick at Nite, Totally 80s and Lucy TV are
in the docstring of `scripts/library/sitcoms.py`. Read that before editing a
slot here; six of the ten slots have a title they may not carry.

Rebuilt 2026-09-01. What the previous grid got wrong:

- **Era was nailed to the clock.** Every morning was `SEVENTIES_MORNING` or
  `CLASSIC_SITCOMS_60s_70s`, every daytime `NINETIES_DAYTIME`, every prime
  `MUST_SEE_TV`. The channel walked through history once and then stood still --
  seven identical days with a Thursday and a Friday variant.
- **`night: (23, 2)` wrapped midnight**, the G1 replay bug. Split into
  `late` 23-24 and `after_hours` 00-02, which is also what makes the finer Nick
  at Nite reading below expressible at all.
- **`MUST_SEE_THURSDAY` stacked four appointments in one slot** -- the live
  defect channel-rules.md cites for G5. The Office, Parks and Recreation,
  Community and 30 Rock are single-camera and have moved to Corncob TV with the
  Thursday night they anchor.
- **The weekend declared no `evening`**, so 17:00-20:00 on Saturday and Sunday
  fell through to `fallback_content`. All seven days declare all ten slots now.
- **Half the shelf was unreachable.** Frasier (273 episodes), Will & Grace,
  Spin City, Just Shoot Me!, Martin, Sabrina, Northern Exposure, Soap, Mork &
  Mindy, I Dream of Jeannie, The Addams Family and the Smothers Brothers were
  all on disk with no registry key at all.
"""

from etv_client.models import ControlWaitUntil

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import sitcoms

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Ten slots, no slot wrapping midnight (G1). The split at 00:00 is not
# cosmetic here: Nick at Nite runs the pre-1970 shows 21:00-24:00 and the 70s
# shift 00:00-02:00, so `late` and `after_hours` have to dodge *different*
# titles. A single `night: (23, 2)` could not express that, and would replay its
# first items across the boundary besides.

GOOD_TIMES_TIMESLOTS = {
    "after_hours": (0, 2),     # The Last Laugh -- 80s/90s only
    "overnight":   (2, 6),     # The Vault
    "early":       (6, 8),     # Sign-On
    "morning":     (8, 10),    # The Morning Strip  -- book
    "midday":      (10, 12),   # The Midday Strip   -- book
    "noon":        (12, 14),   # The Noon Hour      -- one show, one day
    "afternoon":   (14, 17),   # After School       -- book
    "evening":     (17, 20),   # The Syndication Strip
    "prime":       (20, 23),   # the named night
    "late":        (23, 24),   # The Late Shift
}

# ==============================================================================
# 2. THE NETWORK WHEEL
# ==============================================================================
#
# `assemble_day_schedule` picks the first key in SCHEDULES that the day carries
# as a label, so a weekday-named arm gates the whole day -- which is what an
# appointment needs (G5) and what gives each night an identity of its own.
# "WEEKDAY" stays last as the required default arm.

MONDAY = {
    "after_hours": sitcoms.MON_AFTER_HOURS,
    "overnight":   sitcoms.MON_OVERNIGHT,
    "early":       sitcoms.MON_EARLY,
    "morning":     sitcoms.MON_MORNING,
    "midday":      sitcoms.MON_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.MON_AFTERNOON,
    "evening":     sitcoms.MON_EVENING,
    "prime":       sitcoms.MON_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

TUESDAY = {
    "after_hours": sitcoms.TUE_AFTER_HOURS,
    "overnight":   sitcoms.TUE_OVERNIGHT,
    "early":       sitcoms.TUE_EARLY,
    "morning":     sitcoms.TUE_MORNING,
    "midday":      sitcoms.TUE_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.TUE_AFTERNOON,
    "evening":     sitcoms.TUE_EVENING,
    "prime":       sitcoms.TUE_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

WEDNESDAY = {
    "after_hours": sitcoms.WED_AFTER_HOURS,
    "overnight":   sitcoms.WED_OVERNIGHT,
    "early":       sitcoms.WED_EARLY,
    "morning":     sitcoms.WED_MORNING,
    "midday":      sitcoms.WED_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.WED_AFTERNOON,
    "evening":     sitcoms.WED_EVENING,
    "prime":       sitcoms.WED_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

THURSDAY = {
    "after_hours": sitcoms.THU_AFTER_HOURS,
    "overnight":   sitcoms.THU_OVERNIGHT,
    "early":       sitcoms.THU_EARLY,
    "morning":     sitcoms.THU_MORNING,
    "midday":      sitcoms.THU_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.THU_AFTERNOON,
    "evening":     sitcoms.THU_EVENING,
    "prime":       sitcoms.THU_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

FRIDAY = {
    "after_hours": sitcoms.FRI_AFTER_HOURS,
    "overnight":   sitcoms.FRI_OVERNIGHT,
    "early":       sitcoms.FRI_EARLY,
    "morning":     sitcoms.FRI_MORNING,
    "midday":      sitcoms.FRI_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.FRI_AFTERNOON,
    "evening":     sitcoms.FRI_EVENING,
    "prime":       sitcoms.FRI_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

SATURDAY = {
    "after_hours": sitcoms.SAT_AFTER_HOURS,
    "overnight":   sitcoms.SAT_OVERNIGHT,
    "early":       sitcoms.SAT_EARLY,
    "morning":     sitcoms.SAT_MORNING,
    "midday":      sitcoms.SAT_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.SAT_AFTERNOON,
    "evening":     sitcoms.SAT_EVENING,
    "prime":       sitcoms.SAT_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

SUNDAY = {
    "after_hours": sitcoms.SUN_AFTER_HOURS,
    "overnight":   sitcoms.SUN_OVERNIGHT,
    "early":       sitcoms.SUN_EARLY,
    "morning":     sitcoms.SUN_MORNING,
    "midday":      sitcoms.SUN_MIDDAY,
    "noon":        sitcoms.NOON_HOUR,
    "afternoon":   sitcoms.SUN_AFTERNOON,
    "evening":     sitcoms.SUN_EVENING,
    "prime":       sitcoms.SUN_PRIME,
    "late":        sitcoms.LATE_SHIFT,
}

SCHEDULES = {
    "MONDAY":    MONDAY,
    "TUESDAY":   TUESDAY,
    "WEDNESDAY": WEDNESDAY,
    "THURSDAY":  THURSDAY,
    "FRIDAY":    FRIDAY,
    "SATURDAY":  SATURDAY,
    "SUNDAY":    SUNDAY,
    # Required default arm. Every day of the week matches one of the seven
    # above, so this is only reached if the label system stops emitting weekday
    # names -- in which case Wednesday is the least specialised day to land on.
    "WEEKDAY":   WEDNESDAY,
}

# ==============================================================================
# 3. HOLIDAY SCHEDULES
# ==============================================================================
#
# The channel's own event collections rather than `common.*`: those lead with
# `*_animated_tv`, and a laugh-track channel spending Halloween on cartoons is
# running another channel's holiday. Prime keeps its named night on Halloween
# and Thanksgiving -- the whole point of an appointment is that it is still
# there -- and gives way only for Christmas.

HALLOWEEN_SCHEDULE = {
    "morning":   sitcoms.HALLOWEEN_EVENT,
    "midday":    sitcoms.HALLOWEEN_EVENT,
    "noon":      sitcoms.HALLOWEEN_EVENT,
    "afternoon": sitcoms.HALLOWEEN_EVENT,
    "evening":   sitcoms.HALLOWEEN_EVENT,
    "late":      sitcoms.HALLOWEEN_EVENT,
}

THANKSGIVING_SCHEDULE = {
    "morning":   sitcoms.THANKSGIVING_EVENT,
    "midday":    sitcoms.THANKSGIVING_EVENT,
    "noon":      sitcoms.THANKSGIVING_EVENT,
    "afternoon": sitcoms.THANKSGIVING_EVENT,
    "evening":   sitcoms.THANKSGIVING_EVENT,
}

CHRISTMAS_SCHEDULE = {
    "morning":   sitcoms.CHRISTMAS_EVENT,
    "midday":    sitcoms.CHRISTMAS_EVENT,
    "noon":      sitcoms.CHRISTMAS_EVENT,
    "afternoon": sitcoms.CHRISTMAS_EVENT,
    "evening":   sitcoms.CHRISTMAS_EVENT,
    "prime":     sitcoms.CHRISTMAS_EVENT,
    "late":      sitcoms.CHRISTMAS_EVENT,
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
        timeslot_preset=GOOD_TIMES_TIMESLOTS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        block_profiles={},
        logger=ChannelLogger(prefix="[GOOD TIMES]"),
        # Sixteen titles that are clear of Nick at Nite, Totally 80s and Lucy TV
        # at every hour of the day. A fallback fires on a stall and cannot know
        # what time it is, so "safe at some hours" is not safe.
        fallback_content=sitcoms.CHANNEL_FALLBACK,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_thematic_injection=True,
        enable_bumpers=True,
    )

    return run_daily_schedule(api, context, build_id, config)
