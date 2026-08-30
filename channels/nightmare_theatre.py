"""
Nightmare Theatre - Horror

A film channel with a television spine, which is the opposite of High Noon and
is forced by the library: 242 horror features against about 370 usable
episodes. Seventeen hours of film a day, seven of TV.

The organizing axis is the clock, not the era. The channel gets darker as the
night goes on:

    06-09  Creature Feature      Godzilla, King Kong, wolfmen -- the daylight
    09-12  The Vault             the pre-1980 shelf
    12-17  Matinee of the Damned every era at once, seasonally tilted
    17-19  The Legacy            Poltergeist: The Legacy (Sunday: animation)
    19-20  Tales from the Crypt  the anthology, lead-in to prime
    20-22  the appointment       one serialized show a night
    22-24  NIGHTMARE THEATRE     the name block -- the 1980s feature
    00-02  The Witching Hour     slashers and found footage live only here
    02-06  Insomnia Theatre      the modern jukebox

Saturday is the funny night: the comedies keep the 19:00 half-hour, the three
short prestige runs take prime, and 22:00-02:00 is a horror-comedy double
feature. Sunday swaps the evening for animated horror and keeps Twin Peaks.

The channel owns `genre:horror` outright. Nothing was taken from another
channel to build it -- the horror film pool had been parked in orphaned
collections in `library/movies.py` that no channel scheduled, and Other Worlds
had already evicted its horror strands when it became science-fiction-only.
Three horror-tagged shows stay where they are: The X-Files and Beyond Belief
(Other Worlds) and Millennium (Mystery Theatre).

No filler and no bumpers: there are no horror assets on disk. This is the
single highest-value thing the channel is missing -- Nightmare Theatre is a
*hosted* format and it currently has no host.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic import triggers, Marathon
from scripts.library import horror
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# The channel carries its own map. The default's two-hour dayparts cut a feature
# in half -- the mean horror running time here is 104 minutes -- and the
# "movies" preset's four six-hour slots are too coarse to express a clock that
# changes character nine times a day.
#
# `night` is 00-02 and `late` is 22-24, each with its own slot rather than the
# default's `night: (23, 2)`. A wrapping slot is entered twice under two
# different day labels, so "Saturday night" resolves to two different nights and
# a collection replays its first items across the boundary -- the bug Cartoon
# Network, Nick, Disney and High Noon each carry their own map to avoid.

NIGHTMARE_TIMESLOTS = {
    "night":     (0, 2),     # The Witching Hour
    "overnight": (2, 6),     # Insomnia Theatre
    "early":     (6, 9),     # Creature Feature
    "morning":   (9, 12),    # The Vault
    "afternoon": (12, 17),   # Matinee of the Damned
    "evening":   (17, 19),   # The Legacy
    "crypt":     (19, 20),   # Tales from the Crypt
    "prime":     (20, 22),   # the appointment
    "late":      (22, 24),   # NIGHTMARE THEATRE
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    # There is no FRIDAY_THE_13TH label in `core/registry.py` -- it is a
    # floating date that is not a holiday -- so it is composed from the weekday
    # label the day director already derives and the new `day_of_month` trigger.
    Marathon(
        name="Friday the 13th",
        trigger=triggers.all_of(
            triggers.has_label("FRIDAY"),
            triggers.day_of_month(13)
        ),
        collection=horror.FRIDAY_THE_13TH,
        hours=(20, 24)
    ),
    Marathon(
        name="Krampusnacht",
        trigger=triggers.on_date(12, 5),
        collection=horror.KRAMPUSNACHT,
        hours=(20, 24)
    ),
]

# ==============================================================================
# 3. BLOCK DEFINITIONS
# ==============================================================================

# One appointment per night, gated by the weekday label rather than by the
# appointment's own `frequency` -- `frequency` paces an episode index, it does
# not stop the show airing on other days. Saturday is deliberately absent and
# falls through to the limited-series block.
PRIME_BLOCK = {
    "MONDAY":    horror.MONDAY_NIGHT,
    "TUESDAY":   horror.TUESDAY_NIGHT,
    "WEDNESDAY": horror.WEDNESDAY_NIGHT,
    "THURSDAY":  horror.THURSDAY_NIGHT,
    "FRIDAY":    horror.FRIDAY_NIGHT,
    "SUNDAY":    horror.SUNDAY_NIGHT,
    "default":   horror.SATURDAY_LIMITED_SERIES
}

# ==============================================================================
# 4. HOLIDAY SCHEDULES
# ==============================================================================

# October 31. The clock discipline is the right rule 364 days a year and the
# wrong one today: the channel runs horror from noon to close, and the Crypt
# gets the whole hour to itself rather than sharing the wheel.
HALLOWEEN_SCHEDULE = {
    "afternoon": horror.HALLOWEEN_MARATHON,
    # 17:00-20:00 is three hours of Tales from the Crypt, not one. Films do not
    # land on slot boundaries -- the afternoon's last feature runs past 17:00 and
    # a 104-minute film started at 18:00 swallows the Crypt's hour whole, which
    # is what happened before this: the anthology went missing from the channel's
    # own night. Half-hours pack cleanly and the Crypt earns the evening anyway.
    "evening":   horror.CRYPT_MARATHON,
    "crypt":     horror.CRYPT_MARATHON,
    # 20:00-24:00 is the Michael Myers run in order. There is no Devil's Night
    # marathon on the 30th and there cannot be: `find_active_marathon` bails
    # while `holiday_ctx.is_holiday_season` is true and Halloween is one, so
    # holidays outrank marathons on exactly the dates a horror channel most
    # wants one. The holiday schedule is the mechanism that works here.
    "prime":     horror.HALLOWEEN_NIGHT_FEATURE,
    "late":      horror.HALLOWEEN_NIGHT_FEATURE,
}

# ==============================================================================
# 5. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "night":     horror.THE_WITCHING_HOUR,
        "overnight": horror.INSOMNIA_THEATRE,
        "early":     horror.CREATURE_FEATURE,
        "morning":   horror.THE_VAULT,
        "afternoon": horror.MATINEE_OF_THE_DAMNED,
        "evening":   horror.THE_LEGACY,
        "crypt":     horror.TALES_FROM_THE_CRYPT,
        "prime":     PRIME_BLOCK,
        "late":      horror.NIGHTMARE_THEATRE_FEATURE
    },
    # Saturday is the funny night. The comedies take the 19:00 half-hour, the
    # short prestige runs take prime, and 22:00 through 02:00 is an unbroken
    # horror-comedy double feature -- the one slot on the channel where the 51
    # films every other key excludes actually play.
    "SATURDAY": {
        "night":     horror.MIDNIGHT_MOVIE,
        "overnight": horror.INSOMNIA_THEATRE,
        "early":     horror.CREATURE_FEATURE,
        "morning":   horror.THE_VAULT,
        "afternoon": horror.MATINEE_OF_THE_DAMNED,
        "evening":   horror.THE_LEGACY,
        "crypt":     horror.LATE_SHIFT_COMEDY,
        "prime":     horror.SATURDAY_LIMITED_SERIES,
        "late":      horror.MIDNIGHT_MOVIE
    },
    "SUNDAY": {
        "night":     horror.THE_WITCHING_HOUR,
        "overnight": horror.INSOMNIA_THEATRE,
        "early":     horror.CREATURE_FEATURE,
        "morning":   horror.THE_VAULT,
        "afternoon": horror.MATINEE_OF_THE_DAMNED,
        # The one hour of animated horror on the lineup. Every key on this
        # channel excludes genre:animation, so Castlevania, Love Death & Robots
        # and Pet Shop of Horrors reach air only by being named. Primal is not
        # here -- it is an Adult Swim original and Cartoon Network's Midnight
        # Run has the stronger claim.
        "evening":   horror.THE_ANIMATED_HOUR,
        "crypt":     horror.TALES_FROM_THE_CRYPT,
        "prime":     PRIME_BLOCK,
        "late":      horror.NIGHTMARE_THEATRE_FEATURE
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
        holiday_schedules={"HALLOWEEN": HALLOWEEN_SCHEDULE},
        timeslot_preset=NIGHTMARE_TIMESLOTS,
        logger=ChannelLogger(prefix="[NIGHTMARE]"),
        # The wide shelf, not an era. A stall anywhere on the grid should drop
        # into a horror feature; `horror_pure_tv` would be the wrong bed for a
        # channel that is seventeen hours film, and the era keys are each thin
        # enough that leaning on one would repeat inside a day.
        fallback_content="horror_movie",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
