# scripts/logic/profiles.py
"""
Universal Block Profiles for holiday ramping.
Defines how aggressively different timeslots succumb to holiday programming.
"""

from scripts.logic.models import BlockProfile

# 1. STANDARD PROFILE (7-10 Day Ramp)
# Good for Halloween, Thanksgiving, etc.
STANDARD_PROFILES = {
    "overnight": BlockProfile(max_ratio=1.0, bias=0.25, hangover_ratio=0.8),
    "early":     BlockProfile(max_ratio=0.25, bias=-0.2),
    "morning":   BlockProfile(max_ratio=0.4, bias=-0.1),
    "midday":    BlockProfile(max_ratio=0.5, bias=0.0, hangover_ratio=0.4),
    "noon":      BlockProfile(max_ratio=0.6, bias=0.0, hangover_ratio=0.4),
    "afternoon": BlockProfile(max_ratio=0.75, bias=0.05, hangover_ratio=0.5),
    "evening":   BlockProfile(max_ratio=0.7, bias=0.05, hangover_ratio=0.5),
    "prime":     BlockProfile(max_ratio=0.9, bias=0.1, hangover_ratio=0.6),
    "night":     BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.7)
}

# 2. LONG PROFILE (21+ Day Ramp)
# Good for Christmas
CHRISTMAS_PROFILES = {
    "overnight": BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.8),
    "early":     BlockProfile(max_ratio=0.3, bias=-0.1, hangover_ratio=0.3),
    "morning":   BlockProfile(max_ratio=0.5, bias=0.0, hangover_ratio=0.4),
    "midday":    BlockProfile(max_ratio=0.6, bias=0.1, hangover_ratio=0.5),
    "noon":      BlockProfile(max_ratio=0.7, bias=0.1, hangover_ratio=0.5),
    "afternoon": BlockProfile(max_ratio=0.85, bias=0.2, hangover_ratio=0.6),
    "evening":   BlockProfile(max_ratio=0.8, bias=0.2, hangover_ratio=0.6),
    "prime":     BlockProfile(max_ratio=0.95, bias=0.15, hangover_ratio=0.7),
    "night":     BlockProfile(max_ratio=1.0, bias=0.4, hangover_ratio=0.8)
}

# 3. SHORT PROFILE (3-5 Day Ramp)
# Good for Valentine's, St. Patrick's, July 4th
SHORT_PROFILES = {
    **STANDARD_PROFILES, # Start with standard...
    "overnight": BlockProfile(max_ratio=1.0, bias=0.2, hangover_ratio=0.5),
    "prime":     BlockProfile(max_ratio=0.8, bias=0.1, hangover_ratio=0.5),
    "night":     BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.5)
}

# 4. MASTER MAP
HOLIDAY_PROFILES = {
    "default":        STANDARD_PROFILES,
    "CHRISTMAS":      CHRISTMAS_PROFILES,
    "NEW_YEARS_EVE":  SHORT_PROFILES,
    "NEW_YEARS_DAY":  SHORT_PROFILES,
    "VALENTINES_DAY": SHORT_PROFILES,
    "ST_PATRICKS_DAY": SHORT_PROFILES,
    "STAR_WARS_DAY":  SHORT_PROFILES,
    "JULY_4":         SHORT_PROFILES,
    "GROUNDHOGS_DAY": SHORT_PROFILES,
}
