"""
Branded Blocks
==============
Playable units combining content collections with branding profiles.
"""

from scripts.logic.models import BrandedBlock, Swap, Feather
from scripts.logic.seasonal import SeasonalBlock
from . import collections
from . import structures
from . import branding

ADULT_SWIM_BLOCK = BrandedBlock(
    name="Adult Swim",
    content=collections.ADULT_SWIM_MAIN,
    branding=branding.BRANDING_ADULT_SWIM,
    use_epg_group=False,
    specific_intros={
        "cowboy_bebop_tv": "cowboy_bebop_bumpers"
    }
)

TOONAMI_BLOCK = BrandedBlock(
    name="Toonami",
    content=collections.TOONAMI_MAIN,
    branding=branding.BRANDING_TOONAMI,
    use_epg_group=False
)

TGIF_BLOCK = BrandedBlock(
    name="TGIF on Ersatz",
    content=collections.TGIF_PRIMETIME,
    branding=branding.BRANDING_TGIF,
    use_epg_group=True
)

ADULT_SWIM_WEIRD = BrandedBlock(
    name="Adult Swim",
    content=collections.ADULT_SWIM_WEIRD_CONTENT,
    branding=branding.BRANDING_ADULT_SWIM,
    use_epg_group=False
)

FOX_KIDS_BLOCK = BrandedBlock(
    name="Fox Kids",
    content=collections.MARVEL_HOUR,
    branding=branding.BRANDING_90S_KIDS,
    use_epg_group=True
)

# --- SEASONAL BLOCKS (Moved from Channels) ---

# Cartoon Network
CN_MORNING_HERO = SeasonalBlock(
    base=collections.SUPERHERO_HOUR,
    seasonal={
        "SPRING": Swap(collections.MARVEL_HOUR)
    }
)

CN_AFTERNOON_BLOCK = SeasonalBlock(
    base=collections.DISNEY_AFTERNOON,
    seasonal={
        "SPRING": Swap(collections.WB_AFTERNOON)
    }
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
    base=collections.MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN), # Saved by the Bell, etc.
        "WINTER": Feather(collections.CLASSIC_SITCOMS_60s_70s, ratio=0.4) # 40% chance of Classics in Winter
    },
    blend_ratio=1.0 # Default to full swap for Summer
)

SITCOM_AFTERNOON_SEASONAL = SeasonalBlock(
    base=collections.NINETIES_FAMILY,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN),
        "FALL": Feather(collections.WORKING_CLASS_SITCOMS, ratio=0.6)
    }
)

SITCOM_WEEKEND_PRIME = SeasonalBlock(
    base=collections.MUST_SEE_TV,
    seasonal={
        "SUMMER": Swap(collections.NINETIES_TEEN),
        "WINTER": Swap(collections.CLASSIC_SITCOMS_60s_70s)
    },
    blend_ratio=1.0
)

# Classic Movies
MOVIE_PRIMETIME_FEATURE = SeasonalBlock(
    base=collections.NEW_HOLLYWOOD_CINEMA,
    seasonal={
        "SUMMER": Swap(collections.MODERN_BLOCKBUSTERS),
        "FALL": Swap(collections.NOIR_NIGHT),
        "WINTER": Swap(collections.GOLDEN_AGE_CINEMA),
        "SPRING": Swap(collections.MUSICAL_MARQUEE),
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

# Appointment TV
LOST_APPOINTMENT_BLOCK = structures.annual_show(
    content_pattern="lost_s{n}",
    seasons=6,
    episodes=[25, 24, 23, 14, 17, 18],
    premiere_year=2026,
    start_season="FALL",
    reruns="lost_chronological_tv"
)