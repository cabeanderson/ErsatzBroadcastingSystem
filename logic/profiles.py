# scripts/logic/profiles.py
"""
Universal Block Profiles for holiday ramping.
Defines how aggressively different timeslots succumb to holiday programming.
"""

from scripts.logic.models import BlockProfile, HolidayProfile

# 1. MEDIUM PROFILE (7-14 Day Ramp)
# Good for Halloween, Thanksgiving, etc.
MEDIUM_PROFILES = HolidayProfile(window=14, hangover_days=1, blocks={
    "overnight": BlockProfile(max_ratio=1.0, bias=0.25, hangover_ratio=0.8),
    "early":     BlockProfile(max_ratio=0.25, bias=-0.2),
    "morning":   BlockProfile(max_ratio=0.4, bias=-0.1),
    "midday":    BlockProfile(max_ratio=0.5, bias=0.0, hangover_ratio=0.4),
    "noon":      BlockProfile(max_ratio=0.6, bias=0.0, hangover_ratio=0.4),
    "afternoon": BlockProfile(max_ratio=0.75, bias=0.05, hangover_ratio=0.5),
    "evening":   BlockProfile(max_ratio=0.7, bias=0.05, hangover_ratio=0.5),
    "prime":     BlockProfile(max_ratio=0.9, bias=0.1, hangover_ratio=0.6),
    "night":     BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.7) 
})

# 2. LONG PROFILE (21+ Day Ramp)
# Good for Christmas
LONG_PROFILES = HolidayProfile(window=30, hangover_days=3, blocks={
    "overnight": BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.8),
    "early":     BlockProfile(max_ratio=0.3, bias=-0.1, hangover_ratio=0.3),
    "morning":   BlockProfile(max_ratio=0.5, bias=0.0, hangover_ratio=0.4),
    "midday":    BlockProfile(max_ratio=0.6, bias=0.1, hangover_ratio=0.5),
    "noon":      BlockProfile(max_ratio=0.7, bias=0.1, hangover_ratio=0.5),
    "afternoon": BlockProfile(max_ratio=0.85, bias=0.2, hangover_ratio=0.6),
    "evening":   BlockProfile(max_ratio=0.8, bias=0.2, hangover_ratio=0.6),
    "prime":     BlockProfile(max_ratio=0.95, bias=0.15, hangover_ratio=0.7),
    "night":     BlockProfile(max_ratio=1.0, bias=0.4, hangover_ratio=0.8) 
})

# 3. SHORT PROFILE (3-5 Day Ramp)
# Good for Valentine's, St. Patrick's, July 4th
# A slightly less aggressive version of the standard profile.
SHORT_PROFILES = HolidayProfile(window=5, blocks={
    "overnight": BlockProfile(max_ratio=1.0, bias=0.2, hangover_ratio=0.5), # More aggressive overnight
    "early":     BlockProfile(max_ratio=0.25, bias=-0.2),
    "morning":   BlockProfile(max_ratio=0.4, bias=-0.1),
    "midday":    BlockProfile(max_ratio=0.5, bias=0.0, hangover_ratio=0.4),
    "noon":      BlockProfile(max_ratio=0.6, bias=0.0, hangover_ratio=0.4),
    "afternoon": BlockProfile(max_ratio=0.75, bias=0.05, hangover_ratio=0.5),
    "evening":   BlockProfile(max_ratio=0.7, bias=0.05, hangover_ratio=0.5),
    "prime":     BlockProfile(max_ratio=0.8, bias=0.1, hangover_ratio=0.5), # Less aggressive prime
    "night":     BlockProfile(max_ratio=1.0, bias=0.3, hangover_ratio=0.5)   # Less aggressive night
})

# 4. EXTRA-LONG PROFILE (45+ Day Ramp)
# Good for "Christmas Creep" or extended seasonal themes.
EXTRA_LONG_PROFILES = HolidayProfile(window=45, blocks={
    "overnight": BlockProfile(max_ratio=1.0, bias=0.1, hangover_ratio=0.6), # Less aggressive overnight
    "early":     BlockProfile(max_ratio=0.1, bias=-0.3, hangover_ratio=0.2), # Very subtle start
    "morning":   BlockProfile(max_ratio=0.2, bias=-0.2, hangover_ratio=0.3),
    "midday":    BlockProfile(max_ratio=0.3, bias=-0.1, hangover_ratio=0.4),
    "noon":      BlockProfile(max_ratio=0.4, bias=0.0, hangover_ratio=0.4),
    "afternoon": BlockProfile(max_ratio=0.5, bias=0.05, hangover_ratio=0.5),
    "evening":   BlockProfile(max_ratio=0.6, bias=0.1, hangover_ratio=0.5),
    "prime":     BlockProfile(max_ratio=0.8, bias=0.1, hangover_ratio=0.6),
    "night":     BlockProfile(max_ratio=1.0, bias=0.2, hangover_ratio=0.7) 
})

# 5. MASTER MAP
HOLIDAY_PROFILES = {
    "default":        MEDIUM_PROFILES,
    "HALLOWEEN":      MEDIUM_PROFILES,
    "THANKSGIVING":   MEDIUM_PROFILES,
    "CHRISTMAS":      LONG_PROFILES,
    "NEW_YEARS_EVE":  SHORT_PROFILES,
    "NEW_YEARS_DAY":  SHORT_PROFILES,
    "VALENTINES_DAY": SHORT_PROFILES,
    "ST_PATRICKS_DAY": SHORT_PROFILES,
    "STAR_WARS_DAY":  SHORT_PROFILES,
    "JULY_4":         SHORT_PROFILES,
    "GROUNDHOGS_DAY": SHORT_PROFILES,
}
