"""
Across the Pond (104) -- British television

One BBC/ITV broadcast day, run end to end.

The channel used to be billed as "British comedy & panel" and there is not one
panel show on disk -- QI, Taskmaster, Have I Got News for You, Would I Lie to
You?, Buzzcocks, 8 Out of 10 Cats, all checked and absent. A negative is not a
premise (F4) and neither is a promise the library cannot keep, so the identity
is the thing the library actually supports and the grid was already reaching
for: **a British broadcast day, from the morning repeat to the pub lock-in.**

The axis is the schedule itself (F3). Every slot is named for what a British
listings page calls that hour, and each keeps that hour's register -- the
vintage half-hours in the small hours, factual over breakfast, the
feature-length mystery through the morning, comedy in the afternoon, Top Gear
at teatime, Doctor Who at seven, drama at eight, the lock-in from eleven. A
viewer could describe the channel without seeing the config, which is the test.

Television with a film shelf (F5), and not close: roughly 1,600 episodes across
45 shows against sixty-odd named British films. Film gets Saturday night and the
Sunday matinee, and that is all.

What this build changed, beyond the grid:

  * The default timeslot preset is gone. `night: (23, 2)` wrapped midnight (G1).
  * Saturday and Sunday were the weekday grid printed twice. They are days now.
  * `british_comedy_tv` could not see Channel 4 -- widened in `sources.py`.
  * Luther was commented out with 20 episodes on disk; the Cornetto trilogy ran
    as a double bill; Life of Brian resolved to nothing. All three were filing
    mismatches, all three are fixed in `library/british.py`.
  * Both marathons were RandomCollections, which collapse to one item (G9).
  * 110 UK commercials, categorised months ago and never once scheduled.

Added 2026-09-09: **Sharpe is a season rather than a title in a rotation.**
Sixteen feature-length films run one a Thursday at eight for sixteen weeks
every spring, ending in the week of Waterloo Day, with a British period film
behind them and a marathon on 18 June. See `library/british.py`.

"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.logic import triggers, Marathon

# Content
from scripts.library import british

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Ten slots, because a British day changes register about that often and the
# default preset's nine could not express it -- the whole 17:00-20:00 evening
# was one lump holding Doctor Who and Top Gear in rotation, so neither was a
# fixture.
#
# The real reason for a custom map is `night: (23, 2)`. A slot that wraps
# midnight is entered twice under two different day labels, so "Saturday night"
# resolves to two different nights and an ordered collection replays its first
# items across the boundary. Cartoon Network, Nick, Disney, High Noon and
# Nightmare Theatre each carry their own map for this; Across the Pond was still
# on the preset. `night` is 23-24 and `after_hours` is 00-03.
#
# Slot names are the standard ones wherever the hours allow, because
# `HOLIDAY_PROFILES` is keyed by slot name and an unrecognised name falls back
# to a bare `BlockProfile()` -- full holiday ramp, no bias. Only `after_hours`
# and `seven` are custom, and both are short late slots where that is harmless.

POND_TIMESLOTS = {
    "after_hours": (0, 3),    # the lock-in's back half
    "overnight":   (3, 6),    # Closedown
    "early":       (6, 9),    # Breakfast
    "morning":     (9, 12),   # The Daytime Mystery
    "noon":        (12, 14),  # The Lunch Break
    "afternoon":   (14, 17),  # Britcom Afternoon
    "evening":     (17, 19),  # Teatime -- Top Gear
    "seven":       (19, 20),  # The Seven O'Clock Show -- Doctor Who
    "prime":       (20, 23),  # drama, film on Saturday
    "night":       (23, 24),  # the lock-in opens
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================
#
# One marathon, and it is a `MarathonSequence`. Both of the channel's previous
# marathons were handed `RandomCollection`s, which `find_active_marathon`
# collapses to a single item -- the window played one film and fell back to the
# grid (G9).
#
# Doctor Who Day is not here. 23 November falls inside Thanksgiving's fourteen-
# day ramp in most years, and a marathon cannot fire while `is_holiday_season`
# is true, so it could never have run. It is a holiday schedule below.

MARATHONS = [
    # 18 June. The spring Sharpe season reaches Sharpe's Waterloo in the week
    # of the anniversary; this is the encore, and the one day Teatime and the
    # Seven O'Clock Show give way. Priority 4 so it outranks Bond, which can
    # only fire on the three US bank holidays and never on this date anyway.
    Marathon(
        name="Sharpe's Waterloo",
        trigger=triggers.on_date(6, 18),
        collection=british.SHARPES_WATERLOO,
        hours=(17, 24),
        priority=4
    ),
    Marathon(
        name="Bank Holiday Bond",
        # US bank holidays as the proxy for UK ones. None of these three is a
        # holiday *season* -- only Halloween, Thanksgiving and Christmas are --
        # so unlike Doctor Who Day this one can actually fire.
        trigger=lambda boss: boss.has_any("MEMORIAL_DAY", "LABOR_DAY", "PRESIDENTS_DAY")
                             and boss.roll(0.5, "bond_bank_holiday"),
        collection=british.JAMES_BOND_MARATHON,
        hours=(12, 22),
        priority=3
    ),
]

# ==============================================================================
# 3. PRIME
# ==============================================================================
#
# Five drama nights, a film night and a natural-history night. The day gate is
# the slot dict, not a `frequency` argument -- `frequency` paces an episode
# index, it does not stop a block airing on other days (G5).
#
# No two of these draw the same title, which is the whole reason the mystery
# pool is absent: Poirot, Marple and Morse own 09:00-12:00, and running them at
# eight as well would be one pool wearing two blocks (G4). It would also hand
# Mystery Theatre a collision on four nights out of seven.
#
# Luther is Wednesday. Mystery Theatre's Monday prime draws `british_mystery_tv`
# and Luther is in it (C1).

PRIME_BLOCK = {
    "MONDAY":    british.PRIME_MONDAY_GRITTY,
    "TUESDAY":   british.PRIME_TUESDAY_THRILLER,
    "WEDNESDAY": british.PRIME_WEDNESDAY_AFTER_DARK,
    "THURSDAY":  british.PRIME_THURSDAY_PERIOD,
    "FRIDAY":    british.PRIME_FRIDAY_SKETCH,
    "SUNDAY":    british.PRIME_SUNDAY_NATURAL_HISTORY,
    "default":   british.SATURDAY_NIGHT_CINEMA,
}

# Mon/Wed/Fri/Sun against Tue/Thu/Sat. Four hours a night of alternative comedy
# is more than any one pool can carry, and the split is by weekday label rather
# than by a third variant -- three blocks left the weekend one at 148 episodes.
LOCK_IN = {
    "TUESDAY":  british.PUB_LOCK_IN_B,
    "THURSDAY": british.PUB_LOCK_IN_B,
    "SATURDAY": british.PUB_LOCK_IN_B,
    "default":  british.PUB_LOCK_IN_A,
}

# ==============================================================================
# 4. SCHEDULE DEFINITIONS
# ==============================================================================

WEEKDAY = {
    "after_hours": LOCK_IN,
    "overnight":   british.CLOSEDOWN,
    "early":       british.BREAKFAST,
    "morning":     british.THE_DAYTIME_MYSTERY,
    "noon":        british.THE_LUNCH_BREAK,
    "afternoon":   british.BRITCOM_AFTERNOON,
    "evening":     british.TEATIME,
    "seven":       british.THE_SEVEN_OCLOCK_SHOW,
    "prime":       PRIME_BLOCK,
    "night":       LOCK_IN,
}

SCHEDULES = {
    "WEEKDAY": WEEKDAY,

    # Saturday and Sunday were the weekday grid printed twice -- Village
    # Mysteries at eight on a Saturday, same as a Tuesday. Both mornings had to
    # change regardless of taste: Mystery Theatre runs Poirot Saturday
    # 10:00-12:00 and Miss Marple Sunday 10:00-12:00, so the weekday mystery
    # strip collided with it on both days (C1).
    #
    # Saturday takes the children's hour it should always have had, keeps the
    # afternoon comedy, and gives prime to the film.
    "SATURDAY": {
        **WEEKDAY,
        "morning": british.SATURDAY_MORNING,
    },

    # Sunday is the day the channel is proudest of. The matinee is the
    # bank-holiday Bond film, moved off the contested 20:00 hour to 14:00-17:00,
    # which measured as one of the emptiest film hours on the lineup (C7). Prime
    # is Attenborough at eight on BBC One, and nothing else in the lineup runs
    # natural history at all, so it collides with nobody.
    "SUNDAY": {
        **WEEKDAY,
        "morning":   british.THE_OMNIBUS,
        "afternoon": british.THE_SUNDAY_MATINEE,
    },
}

# ==============================================================================
# 5. HOLIDAY SCHEDULES
# ==============================================================================
#
# Christmas takes the evening and the night, not the whole day. The old schedule
# put a four-item collection into all nine slots -- 24 hours against four
# specials, three of which are tag-dependent queries no offline checker can
# confirm. Teatime through the lock-in is where a British Christmas actually
# lives, and the rest of the day keeps the ordinary grid.
#
# Doctor Who Day is 23 November, registered in `core/registry.py`. It is a
# schedule rather than a marathon because Thanksgiving's ramp makes
# `is_holiday_season` true on that date in most years, and marathons do not fire
# during a holiday season (G9) -- the previous marathon had never once run.

HOLIDAY_SCHEDULES = {
    "CHRISTMAS": {
        "evening": british.BRITISH_CHRISTMAS,
        "seven":   british.BRITISH_CHRISTMAS,
        "prime":   british.BRITISH_CHRISTMAS,
        "night":   british.BRITISH_CHRISTMAS,
    },
    "DOCTOR_WHO_DAY": {
        "morning":   british.DOCTOR_WHO_DAY_BLOCK,
        "noon":      british.DOCTOR_WHO_DAY_BLOCK,
        "afternoon": british.DOCTOR_WHO_DAY_BLOCK,
        "evening":   british.DOCTOR_WHO_DAY_BLOCK,
        "seven":     british.DOCTOR_WHO_DAY_BLOCK,
        "prime":     british.DOCTOR_WHO_DAY_BLOCK,
    },
}

# ==============================================================================
# 6. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    # 00:00, not 06:00. The broadcast day now starts with the lock-in's back
    # half, and resetting to 06:00 discarded it.
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00",
        tomorrow=False,
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        timeslot_preset=POND_TIMESLOTS,
        logger=ChannelLogger(prefix="[POND]"),
        # A stall should drop into another British half-hour, not open a
        # feature-length Poirot mid-morning. `british_comedy_tv` is 33 shows and
        # ~995 episodes now that Channel 4 is in it.
        fallback_content="british_comedy_tv",
        # 110 UK commercials, categorised and never scheduled until now. The
        # assets are real, which is the test G12 sets; `ENABLE_FILLER` is off
        # globally, so this declares what the channel would run.
        filler_content=british.BRITISH_FILLERS,
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_filler=True,
    )

    return run_daily_schedule(api, context, build_id, config)
