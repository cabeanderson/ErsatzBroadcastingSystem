# scripts/core/registry.py
from typing import Dict, Tuple, List, Set, Any

# 1. STATIC HOLIDAYS (Fixed Dates)
HOLIDAYS: Dict[Tuple[int, int], str] = {
    (1, 1):   "NEW_YEARS_DAY",
    (2, 2):  "GROUNDHOGS_DAY",
    (2, 14):  "VALENTINES_DAY",
    (3, 17):  "ST_PATRICKS_DAY",
    (4, 1):   "APRIL_FOOLS",
    (4, 20):  "FOUR_TWENTY",
    (5, 4):   "STAR_WARS_DAY",
    (6, 19):  "JUNETEENTH",
    (7, 4):   "JULY_4",
    (10, 31): "HALLOWEEN",
    (11, 11): "VETERANS_DAY",
    # The 1963 first broadcast. Across the Pond runs a holiday schedule on it
    # rather than a marathon: `find_active_marathon` returns nothing while
    # `is_holiday_season` is true, and Thanksgiving's 14-day ramp covers 23
    # November in most years, so a marathon on this date could never fire.
    (11, 23): "DOCTOR_WHO_DAY",
    (12, 24): "CHRISTMAS_EVE",
    (12, 25): "CHRISTMAS",
    (12, 31): "NEW_YEARS_EVE",
}

# 2. SEMANTIC FLOATING RULES
# weekday: 0=Mon, 1=Tue... 6=Sun
# occurrence: 1-5 or "last"
FLOATING_RULES: List[Dict[str, Any]] = [
    {"name": "THANKSGIVING",    "month": 11, "weekday": 3, "occurrence": 4},
    {"name": "MEMORIAL_DAY",    "month": 5,  "weekday": 0, "occurrence": "last"},
    {"name": "LABOR_DAY",       "month": 9,  "weekday": 0, "occurrence": 1},
    {"name": "SUPER_BOWL",      "month": 2,  "weekday": 6, "occurrence": 2},
    {"name": "MLK_DAY",         "month": 1,  "weekday": 0, "occurrence": 3},
    {"name": "PRESIDENTS_DAY",  "month": 2,  "weekday": 0, "occurrence": 3},
    {"name": "MOTHERS_DAY",     "month": 5,  "weekday": 6, "occurrence": 2},
    {"name": "FATHERS_DAY",     "month": 6,  "weekday": 6, "occurrence": 3},
    {"name": "FRIDAY_THE_13TH", "month": None, "weekday": 4, "day": 13},
]

# 3. HOLIDAY PRIORITY (Highest to Lowest)
# Used for resolving conflicts when multiple holidays are active (e.g. Injection)
HOLIDAY_PRIORITY: List[str] = [
    "christmas",      # The big one
    "new_years_eve",
    "new_years_day",
    "halloween",
    "thanksgiving",
    "valentines_day",
    "st_patricks_day",
    "star_wars_day",
    "july_4",
    "mothers_day",
    "fathers_day",
    "super_bowl"
]

# 4. METEOROLOGICAL SEASONS
SEASONS: Dict[str, List[int]] = {
    "WINTER": [12, 1, 2],
    "SPRING": [3, 4, 5],
    "SUMMER": [6, 7, 8],
    "FALL":   [9, 10, 11]
}

# 4. SEASONAL RAMPS (Plateau-based)
SEASONAL_RAMPS: Dict[str, Dict[str, Any]] = {
    "WINTER": {
        "peak_start": (12, 15),      # Dec 15 - plateau starts
        "peak_end": (1, 15),         # Jan 15 - plateau ends (4 weeks)
        "ramp_up_weeks": 5,          # 8 weeks before peak_start
        "ramp_down_weeks": 5,        # 8 weeks after peak_end
    },
    "SPRING": {
        "peak_start": (3, 15),
        "peak_end": (4, 15),
        "ramp_up_weeks": 6,
        "ramp_down_weeks": 5,
    },
    "SUMMER": {
        "peak_start": (6, 15),
        "peak_end": (7, 15),
        "ramp_up_weeks": 5,
        "ramp_down_weeks": 5,
    },
    "FALL": {
        "peak_start": (9, 15),
        "peak_end": (10, 15),
        "ramp_up_weeks": 5,
        "ramp_down_weeks": 5,
    }
}

# 5. INDUSTRY DAYPARTS (Broadcast Standards)
DAYPARTS: Dict[Tuple[int, int], str] = {
    (0, 4):   "LATE_NIGHT",
    (4, 7):   "EARLY_MORNING",
    (7, 10):  "MORNING_NEWS",
    (10, 12): "MORNING",
    (12, 16): "AFTERNOON",
    (16, 19): "EARLY_FRINGE",
    (19, 20): "PRIME_ACCESS",
    (20, 23): "PRIMETIME",
    (23, 0):  "LATE_FRINGE"
}

# Month labels, indexed by datetime.month (1-12).
MONTHS: Dict[int, str] = {
    1: "JANUARY",  2: "FEBRUARY",  3: "MARCH",      4: "APRIL",
    5: "MAY",      6: "JUNE",      7: "JULY",       8: "AUGUST",
    9: "SEPTEMBER", 10: "OCTOBER", 11: "NOVEMBER", 12: "DECEMBER"
}

# 4b. THE BROADCAST YEAR
#
# The meteorological seasons above answer "what does it feel like outside".
# They do not answer "where is the network in its year", and that is the
# question a channel simulating broadcast television actually needs. September
# and December are both FALL; one is premiere month and the other is the dead
# fortnight before New Year, and no label told them apart.
#
# Windows are (start_month, start_day, end_month, end_day), inclusive, and are
# resolved by `is_in_date_range` so a window may wrap the year end. They are
# deliberately allowed to overlap: SWEEPS sits inside FALL_SEASON and
# MIDSEASON, and PREMIERE_WEEK inside FALL_SEASON. Dict resolution takes the
# first matching label, so a channel decides which one wins by the order it
# writes the arms -- the same mechanism Noir November uses on Mystery Theatre.
#
# Dates follow US network practice: the season opens the week containing the
# third Monday of September, sweeps are the November/February/May rating
# months, finales run late May, and summer is repeats until the next premiere.
BROADCAST_SEASONS: Dict[str, Tuple[int, int, int, int]] = {
    "FALL_SEASON":   (9, 15, 12, 15),
    "HIATUS":        (12, 16, 12, 31),
    "MIDSEASON":     (1, 1, 5, 15),
    "FINALE_WEEK":   (5, 16, 5, 22),
    "SUMMER_RERUNS": (5, 23, 9, 14),
}

# Premiere week is the week containing the third Monday of September. Held
# separately from BROADCAST_SEASONS because it is derived from a weekday rather
# than a fixed date, and because it must not exclude FALL_SEASON -- a premiere
# is the opening of the season, not a gap in it.
PREMIERE_WEEK_MONTH: int = 9
PREMIERE_WEEK_OCCURRENCE: int = 3

# The three ratings periods. Each emits both the generic SWEEPS label and its
# own, so a block can say "any sweeps" or "the November one" -- November is the
# only sweeps period that also carries a holiday, and channels treat it
# differently for that reason.
#
# Date windows rather than whole months, and not cosmetically: a whole-month
# May put SWEEPS_MAY on 30 May, which is nine days into SUMMER_RERUNS and a
# week past FINALE_WEEK -- a sweeps period running after the finales it exists
# to lead into. These are the real broadcast windows, and each one ends where
# its season ends.
SWEEPS_PERIODS: Dict[str, Tuple[int, int, int, int]] = {
    "SWEEPS_NOV": (10, 28, 11, 24),   # ends before Thanksgiving
    "SWEEPS_FEB": (1, 28, 2, 24),
    "SWEEPS_MAY": (4, 25, 5, 22),     # ends with FINALE_WEEK
}

# Year-cycle lengths that get a label, in years.
#
# Every other label in this file repeats identically every year -- two Tuesdays
# two years apart are indistinguishable to `derive_labels`, which is why a
# month-keyed rotation is a twelve-slot loop no matter how much content sits
# behind it. These are the only labels that tell one year from the next, and
# `multiyear_rotation` is built on them.
#
# Four lengths rather than an open range because each one costs a label on
# every day of every simulation, and a rotation longer than five years is a
# rotation nobody will ever see the whole of.
YEAR_CYCLES: Tuple[int, ...] = (2, 3, 4, 5)

# Weekday labels, indexed to match datetime.weekday() (Monday == 0).
WEEKDAYS: List[str] = [
    "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
]

# WEEKDAY_GROUPS should only include weekdays (0–4), not Saturday/Sunday
WEEKDAY_GROUPS: Dict[str, Set[int]] = {
    "WEEKDAY_A": {0, 2, 4},  # Mon/Wed/Fri
    "WEEKDAY_B": {1, 3},     # Tue/Thu
}
