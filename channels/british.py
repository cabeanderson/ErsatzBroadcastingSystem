"""
British Channel - "The Telly"
24/7 British Programming: Comedy, Drama, Mysteries, and Factual.
"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.logic import triggers, Marathon

# Content
from scripts.library import british, common

# ==============================================================================
# MARATHONS
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Bank Holiday Bond",
        # 50% chance on "lesser" holidays (using US bank holidays as proxy for UK ones)
        trigger=lambda boss: boss.has_any("MEMORIAL_DAY", "LABOR_DAY", "PRESIDENTS_DAY") and boss.roll(0.5, "bond_bank_holiday"),
        collection=british.JAMES_BOND_FILMS,
        hours=(12, 18),
        priority=3
    ),
    Marathon(
        name="Doctor Who Day",
        trigger=triggers.on_date(11, 23),
        collection=british.DOCTOR_WHO_COLLECTION,
        hours=(10, 24),
        priority=5
    )
]

# ==============================================================================
# SCHEDULE DEFINITIONS
# ==============================================================================

DAILY_SCHEDULE = {
    "overnight": british.KEEP_CALM, # 02:00 - 06:00 (Filler)
    "early":     british.KEEP_CALM, # 06:00 - 08:00
    "morning":   british.VILLAGE_MYSTERIES,      # 08:00 - 10:00
    "midday":    british.DETECTIVE_HOUR,         # 10:00 - 12:00
    "noon":      british.THE_LUNCH_BREAK,        # 12:00 - 14:00
    "afternoon": {                               # 14:00 - 17:00
        "WEEKDAY_A": british.BRITCOM_AFTERNOON_A,
        "WEEKDAY_B": british.BRITCOM_AFTERNOON_B,
        "default": british.BRITCOM_AFTERNOON_A
    },
    "evening":   {                               # 17:00 - 20:00
        "SUNDAY":  british.SUNDAY_SANCTUARY,
        "default": british.TEATIME_FLAGSHIPS
    },
    "prime":     {                               # 20:00 - 23:00
        "MONDAY":    british.PRIME_DRAMA_A,
        "TUESDAY":   british.PRIME_DRAMA_A,
        "WEDNESDAY": british.PRIME_CRIME_BLOCK,
        "THURSDAY":  british.PRIME_DRAMA_A,
        "FRIDAY":    british.FRIDAY_NIGHT_DINNER, # Alternative Comedy
        "SATURDAY":  british.SATURDAY_MOVIE_NIGHT,
        "SUNDAY":    british.BEST_OF_BRITISH_MOVIES,
        "default":   british.PRIME_DRAMA_A
    },
    "night":     {                               # 23:00 - 02:00
        "WEEKDAY_A": british.PUB_LOCK_IN_A,      # Mon/Wed/Fri
        "WEEKDAY_B": british.PUB_LOCK_IN_B,      # Tue/Thu
        "WEEKEND":   british.PUB_LOCK_IN_C,      # Sat/Sun
        "default":   british.PUB_LOCK_IN_A
    }
}

SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
    "WEEKEND": DAILY_SCHEDULE
}

HOLIDAY_SCHEDULES = {
    "CHRISTMAS": {
        "overnight": british.KEEP_CALM,
        "morning": british.BRITISH_CHRISTMAS_COLLECTION,
        "midday": british.BRITISH_CHRISTMAS_COLLECTION,
        "noon": british.BRITISH_CHRISTMAS_COLLECTION,
        "afternoon": british.BRITISH_CHRISTMAS_COLLECTION,
        "evening": british.BRITISH_CHRISTMAS_COLLECTION,
        "prime": british.BRITISH_CHRISTMAS_COLLECTION,
        "night": british.BRITISH_CHRISTMAS_COLLECTION,
    }
}

# ==============================================================================
# CONFIGURATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(
        when="06:00", # Reset to start of broadcast day
        tomorrow=False, 
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        timeslot_preset="default",
        logger=ChannelLogger(prefix="[BRITISH]"),
        fallback_content=british.KEEP_CALM_COLLECTION,
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_filler=True,
        filler_content=british.BRITISH_FILLERS
    )
    
    return run_daily_schedule(api, context, build_id, config)