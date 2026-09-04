"""
Mystery Theatre - Crime, Mystery, and Procedurals

Weekdays run a strip: Monk/Psych mornings and afternoons, Retro P.I. at midday,
the Lunch Special, British mystery in the evening, and a different named block
each weeknight at eight. November hands the whole weeknight lineup to Noir
November. Nights are films.

Saturday is the film day, Sunday the parlour-mystery day into Sunday Prestige.

Poirot and Miss Marple also air on the British channel. That is deliberate --
both channels have a real claim and the hours do not overlap.

True crime was dropped: `true_crime_tv` resolved to one show with six episodes.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.logic import triggers, Marathon, Swap
from scripts.logic.structures import Block
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.library import detective
from scripts.core.logger import ChannelLogger
from datetime import date

# ==============================================================================
# 1. MARATHONS - Special event programming
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Monk: The Trudy Arc",
        trigger=triggers.chance(0.01, "monk_trudy_marathon"),
        collection="monk_trudy_arc_tv",
        hours=(10, 23),
        priority=1
    )
]

# ==============================================================================
# 2. BLOCK DEFINITIONS
# ==============================================================================

# NOVEMBER is checked before the weekday names, and dict resolution takes the
# first label that matches, so Noir November takes the whole weekday lineup for
# one month. It previously lived on PRIME_BLOCK's "default" arm behind five
# explicitly named weekdays -- unreachable, so the channel's signature seasonal
# event had never once aired. Scoped to NOVEMBER rather than FALL on purpose: a
# whole-season takeover would delete the Mon-Fri lineup for three months.
PRIME_BLOCK = {
    "NOVEMBER": detective.NOIR_NOVEMBER_COLLECTION,
    "MONDAY": detective.DETECTIVE_MONDAY_BRITISH,
    "TUESDAY": detective.DETECTIVE_TUESDAY_BLUESKY,
    "WEDNESDAY": detective.DETECTIVE_WEDNESDAY_HARDBOILED,
    "THURSDAY": detective.DETECTIVE_THURSDAY_WHODUNIT,
    "FRIDAY": detective.DETECTIVE_FRIDAY_RETRO
}

# Monk and Psych keep the morning and the afternoon -- five hours a weekday.
# They had seven, plus an evening swap in two seasons, which put two shows at a
# quarter of everything the channel aired.
EVENING_BLOCK = SeasonalBlock(
    base=detective.DETECTIVE_BRITISH_BLOCK,
    seasonal={
        "SUMMER": Swap("monk_chronological_tv")
    }
)

LUNCH_SPECIAL = Block(
    name="Lunch Special",
    items=[{
        "WEEKDAY_A": "elsbeth_tv",
        "WEEKDAY_B": "moonlighting_tv",
        "default": "modern_mystery_tv"
    }],
    fill_strategy="bridge",
    strict_window=False
)

# ==============================================================================
# 3. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": detective.DETECTIVE_LATE_NIGHT,
        "morning": detective.DETECTIVE_USA_BLOCK,      # Monk / Psych
        "midday": detective.RETRO_PI_STRIP,            # was a third hour of Monk / Psych
        "noon": LUNCH_SPECIAL,
        "afternoon": detective.THE_PROCEDURAL_WALL,    # was a third + fourth hour of Monk / Psych
        "evening": EVENING_BLOCK,
        "prime": PRIME_BLOCK,
        "night": detective.MYSTERY_MOVIE_WHEEL         # was late night again; now film
    },
    # Saturday and Sunday used to be the same day printed twice -- identical from
    # 02:00 to 17:00 and again from 23:00. Saturday is the film day; Sunday is
    # the parlour-mystery day leading into Prestige.
    "SATURDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": detective.CLASSIC_DETECTIVES,
        "morning": detective.MODERN_CASEBOOK,          # House, Burn Notice, Veronica Mars
        "midday": "poirot_tv",
        "noon": detective.WHODUNIT_WHEEL,
        "afternoon": "miss_marple_tv",
        "evening": detective.MYSTERY_MOVIE_WHEEL,      # the wheel that shows films
        "prime": detective.MYSTERY_MOVIE_WHEEL,
        "night": "columbo_tv"
    },
    "SUNDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": detective.CLASSIC_DETECTIVES,
        "morning": detective.WHODUNIT_WHEEL,
        "midday": "miss_marple_tv",
        "noon": detective.MODERN_CRIME,
        "afternoon": "columbo_tv",
        "evening": detective.WHODUNIT_WHEEL,
        "prime": detective.SUNDAY_PRESTIGE_BLOCK,
        "night": detective.MYSTERY_MOVIE_WHEEL
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
        logger=ChannelLogger(prefix="[DETECTIVE]"),
        # Was `procedural_tv`, which is tag:procedural -- six shows.
        fallback_content="modern_mystery_tv",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
