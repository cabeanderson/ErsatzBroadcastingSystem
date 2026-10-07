"""
Cartoon Network - the vault, the cartoons, Toonami, Adult Swim

Four brands on one dial position, in the order the day actually ran them. The
restructure that produced this grid is written up in
reference/cartoon-network-review.md; the short version is that the channel was
giving 27 hours a week to Disney and 13 to Nickelodeon while Cartoon Network's
own originals held five, and that Adult Swim was running 20:00-02:00 with
Hanna-Barbera behind it until 06:00 -- the exact inverse of the real thing.

Schedule shape, weekdays:
- Overnight    (02-06): Adult Swim, the acquisitions
- Early        (06-08): The Vault
- Morning      (08-10): Cartoon Cartoons
- Midday       (10-12): Syndication Hour -- CN's own shows in summer
- Noon         (12-14): Action Hour, Marvel-led in spring
- Afternoon    (14-15): The Scooby Block
- After school (15-17): TOONAMI
- Power hour   (17-18): two chronological Dragon Ball Z episodes
- Evening      (18-19): Cartoon Network
- FOX access   (19-~19:40): Simpsons plus one companion
- Prime        (~19:40-22): Cartoon Network -- CCF from 20:00 Friday
- Late prime   (22-23): Adult Swim, the originals
- Night        (23-24): The Midnight Run -- its premiere hour on Friday
- After hrs    (00-02): The Midnight Run, the deeper cuts

Saturday runs oldest to newest and then into the action: the classic shorts at
06:00, Cartoon Cartoons at 08:00, the modern shows at 10:00, the syndication
package 12:00-15:00, Action Hour 15:00-18:00, then five hours of Toonami. The
Toonami Midnight Run takes the Saturday-night overnight.

Sunday: the vault, oldies only through 09:00, Cartoon Cartoons, a film at
10:00, the modern shows, syndication, Action Hour, and FOX Primetime at 19:00.

Daytime blocks group seven- and eleven-minute segments into programme-length
picks and carry enough shows to avoid cycling repeatedly inside one window.
The deliberate exceptions read like television: DBZ is a two-episode power
hour, FOX Sunday reruns its three anchors once, and overnight reruns may shuffle.

Summer (June-August) hands the weekday 10:00 slot to CN's own shows.

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
#
# Toonami begins at 15:00, where it belongs historically. Its final hour is a
# separate DBZ power hour so that exactly two episodes can be guaranteed.
CARTOON_NETWORK_TIMESLOTS = {
    "after_hours":  (0, 2),
    "overnight":    (2, 6),
    "early":        (6, 8),
    "morning":      (8, 9),
    "late_morning": (9, 10),
    "midday":       (10, 12),
    "noon":         (12, 14),
    "afternoon":    (14, 15),
    "after_school": (15, 17),
    "power_hour":   (17, 18),
    "early_evening": (18, 19),
    "access":       (19, 20),
    "prime":        (20, 22),
    "late_prime":   (22, 23),
    "night":        (23, 24),
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
        name="DBZ Movie Marathon",
        # One percent on each eligible weekend day: about one event a year,
        # rare enough to remain a surprise instead of becoming another strip.
        trigger=triggers.all_of(
            triggers.any_of(triggers.has_label("SATURDAY"),
                            triggers.has_label("SUNDAY")),
            triggers.chance(0.01, "dbz_movie_takeover")
        ),
        collection=animation.DBZ_MOVIE_TRILOGIES,
        hours=(12, 18),
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

# 06:00-08:00. Saturday has its own fixed running order, the one day the
# weekend-only shorts (Popeye, the Fleischer Superman) open the morning.
EARLY_BLOCK = {
    "SATURDAY": animation.SATURDAY_MORNING,
    "default": animation.THE_VAULT,
}

MORNING_BLOCK = {
    "SUNDAY": animation.SUNDAY_MORNING,
    "SATURDAY": animation.CARTOON_CARTOONS_WEEKEND,
    "default": animation.CARTOON_CARTOONS,
}

# Sunday oldies end at 09:00. From here both weekend days use their own
# chronological Cartoon Cartoons feed, independent of the weekday strip.
LATE_MORNING_BLOCK = {
    "SATURDAY": animation.CARTOON_CARTOONS_WEEKEND,
    "SUNDAY": animation.CARTOON_CARTOONS_WEEKEND,
    "default": animation.CARTOON_CARTOONS,
}

MIDDAY_BLOCK = {
    "SATURDAY": animation.CN_SATURDAY,
    "SUNDAY": animation.CARTOON_THEATRE,
    "default": animation.CN_MIDDAY_BLOCK,
}

NOON_BLOCK = {
    "SATURDAY": animation.SYNDICATION_HOUR,
    "SUNDAY": animation.CARTOON_CARTOONS_WEEKEND,
    "default": animation.CN_AFTERNOON_BLOCK,
}

# 14:00-15:00. On Saturday this is the third hour of the syndication package:
# the same collection continues where 12:00 stopped, so the three hours are
# eight different shows.
AFTERNOON_BLOCK = {
    "SATURDAY": animation.SYNDICATION_HOUR,
    "SUNDAY": animation.CN_MODERN,
    "default": animation.THE_SCOOBY_BLOCK,
}

# 15:00-17:00. Saturday has the only ordinary random film opportunity: about
# five percent of Saturdays, Cartoon Theatre replaces these two action hours.
AFTER_SCHOOL_BLOCK = {
    "SATURDAY": animation.WEEKEND_ACTION_OR_MOVIE,
    "SUNDAY": animation.SYNDICATION_HOUR,
    "default": animation.TOONAMI_EARLY,
}

# 17:00-18:00. DBZ gets two consecutive chronological episodes every weekday.
POWER_HOUR_BLOCK = {
    "SATURDAY": animation.ACTION_HOUR,
    "SUNDAY": animation.ACTION_HOUR,
    "default": animation.TOONAMI_POWER_HOUR,
}

EARLY_EVENING_BLOCK = {
    "SATURDAY": animation.TOONAMI_SATURDAY,
    "SUNDAY": animation.ACTION_HOUR,
    **animation.CN_EARLY_EVENING,
}

# 19:00. Weekdays always play exactly Simpsons plus one companion, then bridge
# into the 20:00 CN block as soon as those two episodes finish. Sunday begins
# its full FOX night; Saturday continues Toonami.
ACCESS_BLOCK = {
    "SATURDAY": animation.TOONAMI_SATURDAY,
    "SUNDAY": animation.FOX_PRIMETIME,
    **animation.FOX_WEEKDAY,
}

PRIME_BLOCK = {
    "SATURDAY": animation.TOONAMI_SATURDAY_VAULT,
    "SUNDAY": animation.FOX_PRIMETIME,
    "FRIDAY": animation.CARTOON_CARTOON_FRIDAY,
    "default": animation.CN_PRIME,
}

# Adult Swim now begins at 22:00, after the CN/FOX evening. Friday uses the
# same rotation as Monday/Wednesday; CCF remains a tight two hours and never
# wraps its six-show list merely to fill a third.
LATE_PRIME_BLOCK = {
    "SATURDAY": animation.TOONAMI_SATURDAY_VAULT,
    "SUNDAY": animation.AS_ORIGINALS_B,
    "WEEKDAY_A": animation.AS_ORIGINALS_A,
    "default": animation.AS_ORIGINALS_B,
}

# 23:00-24:00. Sunday is the one night the originals run late instead of the
# anime -- Adult Swim launched on a Sunday, and it is the only night of the
# week with no Toonami anywhere in it. Friday gets the premiere variant, which
# is the only night Attack on Titan Junior High airs.
NIGHT_BLOCK = {
    "FRIDAY": animation.MIDNIGHT_RUN_PREMIERE,
    "SUNDAY": animation.AS_ORIGINALS_B,
    "SATURDAY": animation.MIDNIGHT_RUN,
    "WEEKDAY_A": animation.AS_ORIGINALS_A,
    "default": animation.AS_ORIGINALS_B,
}

# 00:00-02:00. MONDAY here is Sunday night, which stays with the originals
# through the midnight boundary rather than cutting to anime halfway. It is the
# A rotation, not B: 23:00 was B under Sunday's date, and B again under
# Monday's would restart one show along and replay two of the last hour's.
AFTER_HOURS_BLOCK = {
    "MONDAY": animation.AS_ORIGINALS_A,
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
    "late_morning": common.HALLOWEEN_KIDS_SPOOKFEST,
    "midday":    animation.CN_HALLOWEEN,
    "noon":      animation.CN_HALLOWEEN,
    "afternoon": animation.CN_HALLOWEEN,
    "after_school": animation.CN_HALLOWEEN,
    "power_hour": animation.CN_HALLOWEEN,
    "early_evening": animation.CN_HALLOWEEN,
    "access":    animation.CN_HALLOWEEN,
    "prime":     common.HALLOWEEN_TV_EVENT,
    "late_prime": common.HALLOWEEN_TV_EVENT,
    "night":     common.HALLOWEEN_ADULT_SCARES,
    "after_hours": common.HALLOWEEN_ADULT_SCARES,
}

CHRISTMAS_SCHEDULE = {
    "overnight": common.CHRISTMAS_TV_EVENT,
    "early":     common.CHRISTMAS_TV_EVENT,
    "morning":   common.CHRISTMAS_TV_EVENT,
    "late_morning": common.CHRISTMAS_TV_EVENT,
    "midday":    common.CHRISTMAS_TV_EVENT,
    "noon":      common.CHRISTMAS_TV_EVENT,
    "afternoon": common.CHRISTMAS_TV_EVENT,
    "after_school": common.CHRISTMAS_TV_EVENT,
    "power_hour": common.CHRISTMAS_TV_EVENT,
    "early_evening": common.CHRISTMAS_TV_EVENT,
    "access":    common.CHRISTMAS_TV_EVENT,
    "prime":     "christmas_animated_movie",
    "late_prime": common.CHRISTMAS_TV_EVENT,
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
    "early":     EARLY_BLOCK,
    "morning":   MORNING_BLOCK,
    "late_morning": LATE_MORNING_BLOCK,
    "midday":    MIDDAY_BLOCK,
    "noon":      NOON_BLOCK,
    "afternoon": AFTERNOON_BLOCK,
    "after_school": AFTER_SCHOOL_BLOCK,
    "power_hour": POWER_HOUR_BLOCK,
    "early_evening": EARLY_EVENING_BLOCK,
    "access":    ACCESS_BLOCK,
    "prime":     PRIME_BLOCK,
    "late_prime": LATE_PRIME_BLOCK,
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
