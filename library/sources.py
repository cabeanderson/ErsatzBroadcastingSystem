# scripts/library/sources.py

"""
Centralized search query registry for all content types.
Uses builder functions for consistency and maintainability.
"""

from .marathons import MARATHONS
from .builders import (
    episode_source, movie_source, apply_tags,
    NINETIES, EIGHTIES, STREAMING_ERA, CLASSIC_ERA,
    WINTER_TAGS, SUMMER_TAGS
)
from .sources_movies import MOVIE_REGISTRY
from .sources_tv import TV_REGISTRY
from .sources_animated import ANIMATED_LIBRARY

# 8. THEME & HOLIDAY REGISTRY

THEME_REGISTRY = {
    # --- THANKSGIVING ---
    "thanksgiving_animated_tv": episode_source(tags='tag:thanksgiving', animated=True),
    "thanksgiving_sitcoms_tv": episode_source(show_genre="comedy", tags='tag:thanksgiving'),
    "thanksgiving_90s_tv": episode_source(era=NINETIES, tags='tag:thanksgiving'),
    
    # --- CHRISTMAS TV ---
    "christmas_animated_tv": episode_source(tags='tag:christmas', animated=True),
    "christmas_80s_sitcoms_tv": episode_source(show_genre="comedy", era=EIGHTIES, tags='tag:christmas'),
    "christmas_90s_sitcoms_tv": episode_source(show_genre="comedy", era=NINETIES, tags='tag:christmas'),
    "christmas_modern_sitcoms_tv": episode_source(show_genre="comedy", era=STREAMING_ERA, tags='tag:christmas'),
    
    # --- HALLOWEEN TV ---
    "halloween_animated_tv": episode_source(tags='tag:halloween', animated=True),
    "halloween_sitcoms_tv": episode_source(show_genre="comedy", tags='tag:halloween'),
    "halloween_drama_tv": episode_source(show_genre="drama", tags='tag:halloween'),

    # --- OTHER HOLIDAYS ---
    "new_years_tv": episode_source(tags='tag:"new years"'),
    "new_years_animated_tv": episode_source(tags='tag:"new years"', animated=True),
    "st_pattys_tv": episode_source(tags='tag:"st patricks day"'),
    "st_pattys_animated_tv": episode_source(tags='tag:"st patricks day"', animated=True),
    "valentines_tv": episode_source(tags='tag:valentines'),
    "valentines_animation_tv": episode_source(tags='tag:valentines', animated=True),
    "easter_tv": episode_source(tags='tag:easter'),
    "easter_animation_tv": episode_source(tags='tag:easter', animated=True),
    "july_4th_tv": episode_source(tags='tag:"july 4th"'),

    # --- HALLOWEEN MOVIES ---
    "halloween_classic_movie": movie_source(tags="tag:halloween", era=CLASSIC_ERA),
    "halloween_80s_movie": movie_source(tags="tag:halloween", era=EIGHTIES),
    "halloween_90s_movie": movie_source(tags="tag:halloween", era=NINETIES),
    "halloween_modern_movie": movie_source(tags="tag:halloween", era=STREAMING_ERA),
    "halloween_all_movie": movie_source(tags="tag:halloween"),
    "halloween_comedy_movie": movie_source(tags="tag:halloween", genre="(comedy OR tag:horror-comedy)"),

    # --- CHRISTMAS MOVIES ---
    "christmas_classic_movie": movie_source(tags="tag:christmas", era=CLASSIC_ERA),
    "christmas_80s_movie": movie_source(tags="tag:christmas", era=EIGHTIES),
    "christmas_90s_movie": movie_source(tags="tag:christmas", era=NINETIES),
    "christmas_modern_movie": movie_source(tags="tag:christmas", era=STREAMING_ERA),
    "christmas_all_movie": movie_source(tags="tag:christmas"),
    "christmas_family_movie": movie_source(tags="tag:christmas", rating="(content_rating:G OR content_rating:PG)"),
    "christmas_animated_movie": movie_source(tags='tag:christmas', animated=True, rating="(content_rating:G OR content_rating:PG)"),
}

# --- SEASONAL VARIANTS ---
SEASONAL_VARIANTS = {
    "classic_hollywood_winter_movies": apply_tags(MOVIE_REGISTRY["classic_hollywood_movie"], WINTER_TAGS),
    "classic_hollywood_summer_movies": apply_tags(MOVIE_REGISTRY["classic_hollywood_movie"], SUMMER_TAGS),
}

# 9. FILLERS & BUMPERS
FILLERS = {
    "commercials_spot": 'type:"other_video"',
    "commercials_90s_spot": 'type:"other_video" AND tag:90s',
    "adult_swim_intro": 'type:"other_video" AND tag:"adult swim" AND tag:intro',
    "adult_swim_bumpers": 'type:"other_video" AND tag:"adult swim" AND tag:bumps',
    "toonami_intro": 'type:"other_video" AND tag:toonami AND tag:intro',
    "toonami_outro": 'type:"other_video" AND tag:toonami AND tag:outro',
    "toonami_bumpers": 'type:"other_video" AND tag:toonami AND (tag:bumps OR tag:general)',
    "cowboy_bebop_bumpers": 'type:"other_video" AND tag:"cowboy bebop"',
}

# 10. THE MASTER EXPORT

MASTER_SOURCES = {
    **MOVIE_REGISTRY,
    **TV_REGISTRY,
    **ANIMATED_LIBRARY,
    **THEME_REGISTRY,
    **MARATHONS,
    **SEASONAL_VARIANTS,
    **FILLERS
}
