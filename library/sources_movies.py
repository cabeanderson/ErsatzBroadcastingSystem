"""
Movie source definitions.
"""
from .builders import (
    movie_source, playback_order,
    SILENT_ERA, GOLDEN_AGE, CLASSIC_ERA, SEVENTIES, EIGHTIES, NINETIES, 
    Y2K_ERA, TENS, TWENTIES, STREAMING_ERA,
    ANIME, SHORT, NO_COMEDY, MOVIE
)

MOVIE_REGISTRY = {
    # --- FILM HISTORY ---
    "20s_silent_movie": movie_source(era=SILENT_ERA),
    "30s_golden_age_movie": movie_source(era=GOLDEN_AGE),
    "classic_hollywood_movie": movie_source(era=CLASSIC_ERA),
    "film_history_all_movie": movie_source(era=CLASSIC_ERA),
    "70s_movie": movie_source(era=SEVENTIES),
    "80s_movie": movie_source(era=EIGHTIES),
    "90s_movie": movie_source(era=NINETIES),
    "00s_movie": movie_source(era=Y2K_ERA),
    "10s_movie": movie_source(era=TENS),
    "20s_movie": movie_source(era=TWENTIES),

    # --- ANIMATION (FILM) ---
    "animation_movie": movie_source(animated=True),
    "classic_animation_movie": movie_source(animated=True, era=CLASSIC_ERA, extra=SHORT),
    "anime_movie": f"{MOVIE} AND {ANIME}",
    "ghibli_movie": movie_source(animated=True, extra='(studio:"Studio Ghibli" OR title:*Ghibli*)'),
    "disney_movie": movie_source(animated=True, studio="Disney"),
    "pixar_movie": movie_source(animated=True,studio="Pixar"),
    "dreamworks_movie": movie_source(studio="Dreamworks"),

    # --- FAMILY & RATING ---
    "family_g_movie": movie_source(rating="content_rating:G"),
    "family_pg_movie": movie_source(rating="content_rating:PG"),
    "kids_safe_movie": movie_source(rating="(content_rating:TV-G OR content_rating:TV-Y)"),

    # --- HORROR VAULT ---
    "classic_horror_movie": movie_source(genre="horror", era=EIGHTIES, extra=NO_COMEDY),
    "horror_zombies_movie": movie_source(genre="horror", tags="tag:zombie", extra=NO_COMEDY),
    "horror_werewolf_movie": movie_source(genre="horror", tags="tag:werewolf", extra=NO_COMEDY),
    "horror_vampire_movie": movie_source(genre="horror", tags="tag:vampire", extra=NO_COMEDY),
    "horror_slasher_movie": movie_source(genre="horror", tags="tag:slasher", extra=NO_COMEDY),
    "horror_aliens_movie": movie_source(genre="horror", tags="tag:alien", extra=NO_COMEDY),
    "horror_kaiju_movie": movie_source(tags="(tag:kaiju OR title:*godzilla*)", extra=NO_COMEDY),
    "horror_found_footage_movie": movie_source(genre="horror", tags='tag:"found footage"', extra=NO_COMEDY),

    # --- HOLIDAYS ---
    "christmas_movie": movie_source(tags="tag:christmas", extra="NOT genre:horror"),
    "halloween_movie": movie_source(tags="tag:halloween"),

    # --- GENRE BLOCKS ---
    "80s_action_movie": movie_source(genre="action", era=EIGHTIES),
    "90s_action_movie": movie_source(genre="action", era=NINETIES),
    "blockbuster_action_movie": movie_source(genre="action", tags="(studio:Marvel OR studio:DC OR tag:superhero)"),
    "80s_comedy_movie": movie_source(genre="comedy", era=EIGHTIES),
    "90s_comedy_movie": movie_source(genre="comedy", era=NINETIES),
    "western_movie": movie_source(genre="western"),
    "musical_movie": movie_source(genre="musical"),
    "war_movie": movie_source(genre="war"),

    # --- SCI-FI / THRILLER ---
    "classic_scifi_movie": movie_source(genre='"science fiction"', era=CLASSIC_ERA),
    "modern_scifi_movie": movie_source(genre='"science fiction"', era=STREAMING_ERA),
    "comedy_scifi_movie": movie_source(genre='"science fiction"', extra="genre:comedy"),
    "action_scifi_movie": movie_source(genre='"science fiction"', extra="genre:action"),
    "cyberpunk_movie": movie_source(tags="tag:cyberpunk"),
    "psych_thriller_movie": movie_source(genre="(thriller OR mystery)", extra="(title:*Psycho* OR title:*Silence*)"),
    "mystery_crime_movie": movie_source(genre="(mystery OR crime)", extra=NO_COMEDY),
    "classic_noir_movie": movie_source(genre="crime", era=GOLDEN_AGE),

    # --- SPECIALTY ---
    "videogame_movie": movie_source(extra="(title:*Mario* OR title:*Sonic* OR title:*Kombat*)"),
    "short_film_movie": movie_source(extra=SHORT),
    
    # --- FRANCHISES ---
    "star_wars_saga_chronological": playback_order(movie_source(extra='title:"Star Wars"'), force="Chronological"),
}