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

# WEEKDAY_GROUPS should only include weekdays (0–4), not Saturday/Sunday
WEEKDAY_GROUPS: Dict[str, Set[int]] = {
    "WEEKDAY_A": {0, 2, 4},  # Mon/Wed/Fri
    "WEEKDAY_B": {1, 3},     # Tue/Thu
}
