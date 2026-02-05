"""
80s TV Content
Collections, Blocks, and Special Programming.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic.models import Swap

# ==============================================================================
# 1. COLLECTIONS
# ==============================================================================

# --- MORNING ---
MORNING_CARTOONS = RandomCollection([
    "eighties_cartoons_heman",
    "eighties_cartoons_transformers",
    "eighties_cartoons_gi_joe",
    "eighties_cartoons_smurfs"
])

MORNING_SITCOMS = RandomCollection([
    "eighties_sitcom_family_ties",
    "eighties_sitcom_growing_pains",
    "eighties_sitcom_full_house"
])

# --- DAYTIME ---
DAYTIME_GENRE_WHEEL = RandomCollection([
    "eighties_action_tv",      # e.g., The A-Team, MacGyver
    "eighties_drama_tv",       # e.g., Hill Street Blues, St. Elsewhere
    "eighties_daytime_movie"   # A random 80s movie
])

FALL_WINTER_DAYTIME_WHEEL = RandomCollection([
    "eighties_crime_tv",       # e.g., Miami Vice, Magnum P.I.
    "eighties_drama_tv",       # More drama focus
    "eighties_suspense_movie"  # Different movie genre
])

# --- PRIME TIME COLLECTIONS ---
ACTION_NIGHT_COLLECTION = OrderedCollection(["eighties_action_knight_rider", "eighties_action_airwolf"])
COMEDY_GOLD_COLLECTION = OrderedCollection(["eighties_sitcom_cheers", "eighties_sitcom_golden_girls", "eighties_sitcom_night_court"])
PI_WEDNESDAY_COLLECTION = OrderedCollection(["eighties_crime_miami_vice", "eighties_crime_magnum_pi"])
MUST_SEE_TV_COLLECTION = OrderedCollection(["eighties_sitcom_cosby_show", "eighties_sitcom_family_ties", "eighties_sitcom_cheers"])
SCIFI_SATURDAY_COLLECTION = OrderedCollection(["eighties_scifi_star_trek", "eighties_scifi_v"])

# --- LATE NIGHT ---
LATE_NIGHT_MUSIC = "eighties_music_videos"
LATE_NIGHT_CULT_MOVIES = "eighties_cult_movie"


# ==============================================================================
# 2. BLOCKS
# ==============================================================================

DAYTIME_MOVIE_BLOCK = Block(
    name="80s Movie Matinee",
    items=["eighties_comedy_movie", "eighties_action_movie"],
    fill_strategy="fill",
    filler="eighties_music_videos"
)

# --- PRIME TIME BLOCKS ---

ACTION_NIGHT_BLOCK = Block(
    name="Action Night",
    items=ACTION_NIGHT_COLLECTION,
    commercial_duration=120,
    commercials="commercials_80s_spot"
)

COMEDY_GOLD_BLOCK = Block(
    name="Comedy Gold",
    items=COMEDY_GOLD_COLLECTION,
)

PI_WEDNESDAY_BLOCK = Block(
    name="P.I. Wednesday",
    items=PI_WEDNESDAY_COLLECTION,
)

MUST_SEE_TV_BLOCK = Block(
    name="Must See TV",
    items=MUST_SEE_TV_COLLECTION,
)

FRIDAY_NIGHT_MOVIES_BLOCK = Block(
    name="Friday Night Movies",
    items=["eighties_blockbuster_movie"],
    intro="movie_intro_bumper",
    fill_strategy="gap" # Leave dead air if movie ends early
)

SCIFI_SATURDAY_BLOCK = Block(
    name="Sci-Fi Saturday",
    items=SCIFI_SATURDAY_COLLECTION,
)

PRIME_TIME_BLOCKS = {
    "MONDAY": ACTION_NIGHT_BLOCK,
    "TUESDAY": COMEDY_GOLD_BLOCK,
    "WEDNESDAY": PI_WEDNESDAY_BLOCK,
    "THURSDAY": MUST_SEE_TV_BLOCK,
    "FRIDAY": FRIDAY_NIGHT_MOVIES_BLOCK,
    "SATURDAY": SCIFI_SATURDAY_BLOCK,
    "SUNDAY": "eighties_drama_movie"
}

# --- SEASONAL BLOCKS ---

SEASONAL_MORNING_BLOCK = SeasonalBlock(
    base=MORNING_CARTOONS, # Spring/Summer default
    seasonal={
        "FALL": Swap(MORNING_SITCOMS),
        "WINTER": Swap(MORNING_SITCOMS)
    }
)

SEASONAL_DAYTIME_BLOCK = SeasonalBlock(
    base=DAYTIME_GENRE_WHEEL, # Spring/Summer default
    seasonal={
        "FALL": Swap(FALL_WINTER_DAYTIME_WHEEL),
        "WINTER": Swap(FALL_WINTER_DAYTIME_WHEEL)
    }
)

# --- DEFAULT ASSIGNMENTS ---
MORNING_BLOCK = SEASONAL_MORNING_BLOCK
DAYTIME_BLOCK = SEASONAL_DAYTIME_BLOCK
LATE_NIGHT_BLOCK = LATE_NIGHT_MUSIC