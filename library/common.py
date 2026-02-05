"""
Common collections and shared assets used by multiple channels.
"""

from scripts.logic.structures import RandomCollection

COMMERCIAL_BREAK = RandomCollection([
    "commercials_spot"
])

# Search-Based Era Blocks (Plain lists)
VINTAGE_VAULT = RandomCollection(["vintage_tv", "retro_tv"])
GOLDEN_AGE_TV = RandomCollection(["golden_age_tv", "golden_sitcoms_tv"])
MODERN_HD_TV = RandomCollection(["hd_era_tv", "modern_drama_tv", "modern_sitcoms_tv"])

# Holiday TV Episodes (Plain lists for event programming)
THANKSGIVING_COMEDY_EVENT = RandomCollection([
    "thanksgiving_sitcoms_tv",
    "thanksgiving_animated_tv",
    "thanksgiving_90s_tv"
])

HALLOWEEN_TV_EVENT = RandomCollection([
    "halloween_animated_tv",
    "halloween_sitcoms_tv",
    "halloween_drama_tv"
])

CHRISTMAS_TV_EVENT = RandomCollection([
    "christmas_animated_tv",
    "christmas_80s_sitcoms_tv",
    "christmas_90s_sitcoms_tv",
    "christmas_modern_sitcoms_tv"
])

VALENTINES_COMEDY_EVENT = RandomCollection([
    "valentines_tv",
    "valentines_animation_tv"
])

# Selective Halloween Blocks
HALLOWEEN_KIDS_SPOOKFEST = RandomCollection([
    "halloween_animated_tv",
    "scooby_doo_tv"
])

HALLOWEEN_TEEN_FRIGHTS = RandomCollection([
    "gravity_falls_tv",
    "infinity_train_tv",
    "courage_tv"
])

HALLOWEEN_ADULT_SCARES = RandomCollection([
    "metalocalypse_tv",
    "horror_tv"
])