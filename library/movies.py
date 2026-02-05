"""
Movie Content
Collections, Blocks, and Special Programming.
"""

from scripts.logic.structures import RandomCollection
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Feather

# --- COLLECTIONS ---

# Historical Cinema
SILENT_CINEMA = RandomCollection(["20s_silent_movie"])
GOLDEN_AGE_CINEMA = RandomCollection(["30s_golden_age_movie", "classic_hollywood_movie"])
NEW_HOLLYWOOD_CINEMA = RandomCollection(["70s_movie", "80s_movie"])
MODERN_BLOCKBUSTERS = RandomCollection(["90s_movie", "00s_movie", "10s_movie", "blockbuster_action_movie"])

# Spotlights
CYBERPUNK_SPOTLIGHT = RandomCollection(["cyberpunk_movie", "classic_scifi_movie"])
TIME_TRAVEL_SPOTLIGHT = RandomCollection(["classic_scifi_movie", "modern_scifi_movie", "80s_movie"])
ALIEN_INVASION_SPOTLIGHT = RandomCollection(["horror_aliens_movie", "classic_scifi_movie"])

# Genre Marquees
WESTERN_MATINEE = RandomCollection(["western_movie"])
MUSICAL_MARQUEE = RandomCollection(["musical_movie"])
WAR_CHRONICLES = RandomCollection(["war_movie"])
ACTION_ADRENALINE = RandomCollection(["80s_action_movie", "90s_action_movie", "blockbuster_action_movie"])
COMEDY_NIGHT = RandomCollection(["80s_comedy_movie", "90s_comedy_movie"])
NOIR_NIGHT = RandomCollection(["classic_noir_movie", "mystery_crime_movie"])
SCI_FI_SHOWCASE = RandomCollection(["classic_scifi_movie", "modern_scifi_movie", "cyberpunk_movie"])

# Monster Vault
CREATURE_FEATURE = RandomCollection(["horror_kaiju_movie", "horror_werewolf_movie"])
UNDEAD_CINEMA = RandomCollection(["horror_zombies_movie", "horror_vampire_movie"])
STALKER_CINEMA = RandomCollection(["horror_slasher_movie", "psych_thriller_movie"])
HORROR_VAULT = RandomCollection(["classic_horror_movie", "horror_found_footage_movie", "horror_aliens_movie"])

# Holiday Movies (Plain lists for event programming)
HALLOWEEN_MARATHON_EVENT = RandomCollection([
    "halloween_all_movie",
    "halloween_comedy_movie",
    "halloween_80s_movie",
    "halloween_90s_movie"
])

CHRISTMAS_FESTIVAL_EVENT = RandomCollection([
    "christmas_all_movie",
    "christmas_family_movie",
    "christmas_classic_movie",
    "christmas_80s_movie",
    "christmas_90s_movie"
])

# --- BLOCKS ---

# Classic Movies
MOVIE_PRIMETIME_FEATURE = SeasonalBlock(
    base=NEW_HOLLYWOOD_CINEMA,
    seasonal={
        "SUMMER": Swap(MODERN_BLOCKBUSTERS),
        "FALL": Swap(NOIR_NIGHT),
        "WINTER": Swap(GOLDEN_AGE_CINEMA),
        "SPRING": Swap(MUSICAL_MARQUEE),
    }
)

MOVIE_AFTERNOON_FEATURE = SeasonalBlock(
    base="classic_hollywood_movie",
    seasonal={
        "WINTER": Feather("classic_hollywood_winter_movies", 0.4),
        "SUMMER": Feather("classic_hollywood_summer_movies", 0.4),
        "SPRING": Feather("musical_movie", 0.3),
        "FALL": Feather("classic_noir_movie", 0.3)
    }
)