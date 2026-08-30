"""
Movie Content
Collections, Blocks, and Special Programming.
"""

from scripts.logic.structures import RandomCollection
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.models import Swap, Feather

# --- COLLECTIONS ---

# Historical Cinema
SILENT_CINEMA = RandomCollection(["20s_silent_movie"])
# The morning block (06:00-12:00). Uses the science-fiction-free variant because
# Other Worlds owns that shelf and airs it in the same hours; the afternoon
# feature and the seasonal variants still use the unfiltered key.
GOLDEN_AGE_CINEMA = RandomCollection(["30s_golden_age_movie", "classic_hollywood_pure_movie"])
NEW_HOLLYWOOD_CINEMA = RandomCollection(["70s_movie", "80s_movie"])
# Currently on no channel. Kept because the modern-film channel wants this pool;
# it was on Classic Cinema's summer prime, which is not where it belongs.
MODERN_BLOCKBUSTERS = RandomCollection(["90s_movie", "00s_movie", "10s_movie", "blockbuster_action_movie"])

# Spotlights
CYBERPUNK_SPOTLIGHT = RandomCollection(["cyberpunk_movie", "classic_scifi_movie"])
TIME_TRAVEL_SPOTLIGHT = RandomCollection(["classic_scifi_movie", "modern_scifi_movie", "80s_movie"])
ALIEN_INVASION_SPOTLIGHT = RandomCollection(["horror_aliens_movie", "classic_scifi_movie"])

# Genre Marquees
# WESTERN_MATINEE is gone. It was `western_movie` -- all 46 western films --
# across both weekend afternoons, 12 hours a week, and High Noon now owns that
# shelf outright. Same eviction Other Worlds got for science fiction.
MUSICAL_MARQUEE = RandomCollection(["musical_movie"])
WAR_CHRONICLES = RandomCollection(["war_movie"])
ACTION_ADRENALINE = RandomCollection(["80s_action_movie", "90s_action_movie", "blockbuster_action_movie"])
COMEDY_NIGHT = RandomCollection(["80s_comedy_movie", "90s_comedy_movie"])
# `mystery_crime_movie` spans every era, so this used to put Classic Cinema's
# overnight on the identical pool Mystery Theatre schedules at the same hour.
# The pre-1980 half is this channel's; the rest is Mystery Theatre's.
NOIR_NIGHT = RandomCollection(["classic_noir_movie", "classic_crime_movie"])
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
        # No SUMMER swap. Modern blockbusters were doing the whole of summer
        # prime here, which is a different channel's job -- this one is New
        # Hollywood and older. Summer now falls through to the base.
        "FALL": Swap(NOIR_NIGHT),            # Noir fits the moody fall vibe
        "WINTER": Feather("classic_hollywood_winter_movies", 0.5), # Blend in winter-tagged classics
        "SPRING": Feather("classic_hollywood_spring_movies", 0.5), # Blend in spring-tagged classics
    },
    auto_tag=True
)

# Classic Cinema's weekend prime. Deliberately built from pools no other channel
# touches: musicals and war films are unclaimed, and 70s film is this channel's
# alone. The obvious choice -- reusing the weekday New Hollywood block -- puts
# `80s_movie` opposite the Eighties channel on Sunday prime, and who owns 80s
# film is a question for the full grid pass, not something to settle by accident
# in a one-slot fix.
WEEKEND_MARQUEE = RandomCollection([
    "musical_movie",
    "war_movie",
    "70s_movie"
])

# Was `classic_hollywood_movie`, the unfiltered 1950-69 era. The `_pure_`
# variant is the same shelf with science fiction and westerns removed, which is
# what keeps this off Other Worlds' and High Noon's film at the same hour.
MOVIE_AFTERNOON_FEATURE = SeasonalBlock(
    base="classic_hollywood_pure_movie",
    seasonal={},
    auto_tag=True
)

# The weekend afternoon, in place of the western matinee. Base is the channel's
# own era so the slot is never thin; the four seasonal keys only Feather on top,
# which is what they were built for and where `classic_hollywood_summer_movies`
# and `classic_hollywood_fall_movies` finally get used -- both had been in the
# registry and on no channel.
WEEKEND_MATINEE = SeasonalBlock(
    base="classic_hollywood_pure_movie",
    seasonal={
        "WINTER": Feather("classic_hollywood_winter_movies", 0.5),
        "SPRING": Feather("classic_hollywood_spring_movies", 0.5),
        "SUMMER": Feather("classic_hollywood_summer_movies", 0.5),
        "FALL":   Feather("classic_hollywood_fall_movies", 0.5),
    },
    auto_tag=True
)