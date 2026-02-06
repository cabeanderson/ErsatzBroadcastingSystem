"""
Sitcom Content
Collections, Blocks, and Special Programming.
"""

from datetime import date
from scripts.logic.structures import RandomCollection, OrderedCollection, DailyOrderedCollection, Block
from scripts.logic.factories import annual_show
from scripts.library.queries import show_by_title
from scripts.logic.models import Swap, Feather
from scripts.logic.calendar.seasonal import SeasonalBlock
from . import branding

# --- COLLECTIONS ---

# Classic TV - OrderedCollection for nostalgic progression
NICK_AT_NITE = OrderedCollection([
    "i_love_lucy_tv",
    "andy_griffith_tv",
    "dick_van_dyke_tv",
    "bewitched_tv",
    "gilligans_island_tv",
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "taxi_tv",
    "cheers_tv",
    "wonder_years_tv"
])

SEVENTIES_MORNING = RandomCollection([
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "mash_tv",
    "good_times_tv",
    "sanford_and_son_tv"
])

CLASSIC_SITCOMS_60s_70s = RandomCollection([
    "i_love_lucy_tv",
    "andy_griffith_tv",
    "dick_van_dyke_tv",
    "bewitched_tv",
    "gilligans_island_tv",
    "mary_tyler_moore_tv",
    "bob_newhart_tv",
    "mash_tv",
    "good_times_tv",
    "sanford_and_son_tv"
])

# 1990s Programming Blocks - OrderedCollection for branded lineups
MUST_SEE_TV = OrderedCollection([
    {"title": "Seinfeld"},
    {"title": "The Office"},
    {"title": "Parks and Recreation"},
    {"title": "30 Rock"},
    {"title": "Community"}
])

NINETIES_PRIMETIME = RandomCollection([
    {"title": "Seinfeld"},
    {"title": "Home Improvement"},
    {"title": "The Drew Carey Show"},
    {"title": "Newsradio"},
    {"title": "3rd Rock from the Sun"},
    {"title": "Wings"},
    {"title": "Mad About You"}
])

NINETIES_DAYTIME = RandomCollection([
    "fresh_prince_tv",
    "saved_by_the_bell_tv",
    "sister_sister_tv",
    "moesha_tv",
    "mr_cooper_tv",
    "coach_tv",
    "nanny_tv",
    "married_children_tv"
])

NINETIES_FAMILY = RandomCollection([
    "full_house_tv",
    "family_matters_tv",
    "fresh_prince_tv",
    "home_improvement_tv",
    "dinosaurs_tv"
])

NINETIES_TEEN = RandomCollection([
    "saved_by_the_bell_tv",
    "sister_sister_tv",
    "moesha_tv",
    "mr_cooper_tv",
    "fresh_prince_tv"
])

# Specialty Rotations
WORKPLACE_COMEDIES = RandomCollection([
    "the_office_tv",
    "parks_and_recreation_tv",
    "30_rock_tv",
    "newsradio_tv",
    "taxi_tv",
    "mary_tyler_moore_tv"
])

WORKING_CLASS_SITCOMS = RandomCollection([
    "married_children_tv",
    "good_times_tv",
    "sanford_and_son_tv",
    "home_improvement_tv",
    "drew_carey_tv"
])

QUIRKY_COMEDIES = RandomCollection([
    "3rd_rock_tv",
    "community_tv",
    "30_rock_tv",
    "dinosaurs_tv",
    "taxi_tv"
])

# --- BLOCKS ---

TGIF_BLOCK = Block(
    name="TGIF on Ersatz",
    items=OrderedCollection([
        {"title": "Full House", "query": show_by_title("Full House"), "order": "Shuffle"},
        {"title": "Family Matters", "query": show_by_title("Family Matters"), "order": "Shuffle"},
        {"title": "Perfect Strangers", "query": show_by_title("Perfect Strangers"), "order": "Shuffle"},
        {"title": "Hangin' with Mr. Cooper", "query": show_by_title("Hangin' with Mr. Cooper"), "order": "Shuffle"},
        {"title": "Sister, Sister", "query": show_by_title("Sister, Sister"), "order": "Shuffle"},
        {"title": "Dinosaurs", "query": show_by_title("Dinosaurs"), "order": "Shuffle"},
    ]),
    bumpers=branding.BRANDING_TGIF.bumpers,
    use_epg_group=False
)

# Fox 90s
FOX_PRIME_SEASONAL = SeasonalBlock(
    base="married_children_tv",
    seasonal={
        "SUMMER": "90s_comedy_movie", # Summer movies
        "WINTER": "90s_drama_tv"      # Cozy dramas
    },
    blend_ratio=0.4 # 40% chance at peak season
)

# Sitcoms
SITCOM_WEEKDAY_PRIME = SeasonalBlock(
    base=MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(NINETIES_TEEN), # Saved by the Bell, etc.
        "WINTER": Feather(CLASSIC_SITCOMS_60s_70s, ratio=0.4) # 40% chance of Classics in Winter
    },
    blend_ratio=1.0 # Default to full swap for Summer
)

SITCOM_AFTERNOON_SEASONAL = SeasonalBlock(
    base=NINETIES_FAMILY,
    seasonal={
        "SUMMER": Swap(NINETIES_TEEN),
        "FALL": Feather(WORKING_CLASS_SITCOMS, ratio=0.6)
    }
)

SITCOM_WEEKEND_PRIME = SeasonalBlock(
    base=MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(NINETIES_TEEN),
        "WINTER": Swap(CLASSIC_SITCOMS_60s_70s)
    },
    blend_ratio=1.0
)

# --- SITCOM APPOINTMENT BLOCKS ---

# 1. THE OFFICE (Slot 1)
# Filler: Seinfeld (180 eps)
OFFICE_FILLERS = OrderedCollection(["seinfeld_tv"])

OFFICE_BLOCK = annual_show(
    show_title="The Office",
    seasons=9,
    episodes_per_season=[6, 22, 25, 19, 28, 26, 26, 24, 25],
    premiere_year=2026,
    premiere_season="FALL",
    reruns=OFFICE_FILLERS,
    loop=True
)

# 2. PARKS AND REC (Slot 2)
# Filler: 3rd Rock (139 eps)
PARKS_FILLERS = OrderedCollection(["3rd_rock_tv"])

PARKS_BLOCK = annual_show(
    show_title="Parks and Recreation",
    seasons=7,
    episodes_per_season=[6, 24, 16, 22, 22, 22, 13],
    premiere_year=2026,
    premiere_season="FALL",
    reruns=PARKS_FILLERS,
    loop=True
)

# 3. COMMUNITY (Slot 3)
# Filler: Fresh Prince (148 eps)
COMMUNITY_FILLERS = OrderedCollection(["fresh_prince_tv"])

COMMUNITY_BLOCK = annual_show(
    show_title="Community",
    seasons=6,
    episodes_per_season=[25, 24, 22, 13, 13, 13],
    premiere_year=2026,
    premiere_season="FALL",
    reruns=COMMUNITY_FILLERS,
    loop=True
)

# 4. 30 ROCK (Slot 4)
# Filler: Newsradio (97 eps)
THIRTY_ROCK_FILLERS = OrderedCollection(["newsradio_tv"])

THIRTY_ROCK_BLOCK = annual_show(
    show_title="30 Rock",
    seasons=7,
    episodes_per_season=[21, 15, 22, 22, 23, 22, 13],
    premiere_year=2026,
    premiere_season="FALL",
    reruns=THIRTY_ROCK_FILLERS,
    loop=True
)

# MUST SEE THURSDAY (Appointment Block)
MUST_SEE_THURSDAY = DailyOrderedCollection([
    OFFICE_BLOCK,
    PARKS_BLOCK,
    COMMUNITY_BLOCK,
    THIRTY_ROCK_BLOCK
])