# scripts/library/sources.py

"""
Centralized search query registry for all content types.
Uses builder functions for consistency and maintainability.
"""

from .marathons import MARATHONS
# Import builder functions and core types from logic
from scripts.library.queries import (
    episode_source, movie_source, show_source, 
    show_by_title, show_container_by_title, movie_by_title,
    playback_order, playlist_ref, apply_tags,
    ANIME, MOVIE, SHOW
)
from scripts.logic.factories import episode_list
# Import filter constants from our local library
from .filters import (
    NINETIES, EIGHTIES, STREAMING_ERA, CLASSIC_ERA,
    WINTER_TAGS, SUMMER_TAGS,
    FALL_TAGS, SPRING_TAGS, SILENT_ERA, GOLDEN_AGE, SEVENTIES, Y2K_ERA, TENS, TWENTIES,
    SHORT, NO_COMEDY, NO_HORROR,
    TV_CLASSIC, TV_GOLDEN_AGE, TV_HD, TV_VINTAGE,
    NO_FANTASY, NO_SITCOM, NO_BBC, NO_SCIFI,
    SIXTIES, SITCOM_80S_VIBE, SITCOM_90S_VIBE
)

# ============================================================================
# 1. MOVIES
# ============================================================================

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
    "british_movie": movie_source(extra='(tag:british OR studio:"BBC" OR studio:"BBC Films" OR studio:"Film4" OR studio:"Working Title" OR studio:"Ealing" OR studio:"Hammer" OR studio:"Warp Films" OR studio:"DNA Films")'),
    
    # --- FRANCHISES ---
    "star_wars_saga_chronological": playback_order(movie_source(extra='title:"Star Wars"'), force="Chronological"),
}

# --- PLAYLISTS ---
PLAYLIST_REGISTRY = {
    "star_trek_all_playlist": playlist_ref(name="Star Trek Universe", group="ErsatzTV"),
}

# ============================================================================
# 2. TV SHOWS (FILTERS & GENRES)
# ============================================================================

TV_REGISTRY = {
    # --- SCI-FI ---
    "classic_scifi_tv": show_source(genre='"science fiction"', era=TV_CLASSIC, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "syndicated_scifi_tv": show_source(genre='"science fiction"', era=TV_GOLDEN_AGE, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "golden_scifi_tv": show_source(genre='"science fiction"', era=TV_GOLDEN_AGE, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "modern_scifi_tv": show_source(genre='"science fiction"', era=TV_HD, extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "scifi_tv": show_source(genre='"science fiction"', extra=f"{NO_FANTASY} AND {NO_SITCOM}"),
    "scifi_fantasy_tv": show_source(genre='"science fiction"', extra=f"genre:fantasy AND {NO_SITCOM}"),
    "space_opera_tv": show_source(genre='"science fiction"', extra=NO_SITCOM),
    
    # --- FANTASY ---
    "fantasy_pure_tv": show_source(genre="fantasy", extra=f"{NO_SCIFI} AND {NO_SITCOM}"),
    "fantasy_tv": show_source(genre="fantasy", extra=NO_SITCOM),
    "epic_fantasy_tv": show_source(genre="fantasy", tags="(tag:epic OR tag:sword)", extra=NO_SITCOM),
    
    # --- SITCOMS BY ERA ---
    "60s_sitcoms_tv": show_source(tags="tag:sitcom", era=SIXTIES, extra=NO_BBC),
    "70s_sitcoms_tv": show_source(tags="tag:sitcom", era=SEVENTIES, extra=NO_BBC),
    "80s_sitcoms_tv": show_source(tags="tag:sitcom", era=SITCOM_80S_VIBE, extra=NO_BBC),
    "90s_sitcoms_tv": show_source(tags="tag:sitcom", era=SITCOM_90S_VIBE, extra=NO_BBC),
    "00s_sitcoms_tv": show_source(tags="tag:sitcom", era=Y2K_ERA, extra=NO_BBC),
    "10s_sitcoms_tv": show_source(tags="tag:sitcom", era=TENS, extra=NO_BBC),
    "golden_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_GOLDEN_AGE),
    "classic_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_CLASSIC),
    "modern_sitcoms_tv": show_source(tags="tag:sitcom", era=TV_HD),
    
    # --- ACTION & DRAMA BY ERA ---
    "60s_action_tv": show_source(genre="action", era=SIXTIES),
    "80s_action_tv": show_source(genre="action", era=EIGHTIES),
    "90s_action_tv": show_source(genre="action", era=NINETIES),
    "classic_action_tv": show_source(genre="action", era=TV_CLASSIC),
    "syndicated_action_tv": show_source(genre="action", era=TV_GOLDEN_AGE),
    "modern_action_tv": show_source(genre="action", era=TV_HD),
    
    "80s_drama_tv": show_source(genre="drama", era=EIGHTIES, extra=NO_SITCOM),
    "90s_drama_tv": show_source(genre="drama", era=NINETIES, extra=NO_SITCOM),
    "00s_drama_tv": show_source(genre="drama", era=Y2K_ERA, extra=NO_SITCOM),
    "golden_drama_tv": show_source(genre="drama", era=TV_GOLDEN_AGE, extra=NO_SITCOM),
    "modern_drama_tv": show_source(genre="drama", era=TV_HD, extra=NO_SITCOM),
    "prestige_drama_tv": show_source(genre="drama", studio="(HBO OR AMC OR Showtime OR FX)", extra=NO_SITCOM),
    
    # --- COMEDY & MYSTERY ---
    "classic_comedy_tv": show_source(genre="comedy", era=TV_CLASSIC),
    "modern_comedy_tv": show_source(genre="comedy", era=TV_HD),
    "sketch_comedy_tv": show_source(tags="tag:sketch"),
    "procedural_tv": show_source(genre="(mystery OR crime)", tags="tag:procedural"),
    "detective_tv": show_source(genre="(mystery OR crime)", tags="(tag:detective OR tag:investigator)"),
    "classic_mystery_tv": show_source(genre="(mystery OR crime)", era=TV_CLASSIC),
    "modern_mystery_tv": show_source(genre="(mystery OR crime)", era=TV_HD),
    "true_crime_tv": show_source(genre="documentary", extra="genre:crime"),
    
    # --- WESTERN, HORROR, THRILLER ---
    "classic_western_tv": show_source(genre="western", era=TV_CLASSIC),
    "modern_western_tv": show_source(genre="western", era=STREAMING_ERA),
    "western_tv": show_source(genre="western"),
    "horror_tv": show_source(genre="horror"),
    "classic_horror_tv": show_source(genre="horror", era=TV_CLASSIC),
    "modern_horror_tv": show_source(genre="horror", era=TV_HD),
    "thriller_tv": show_source(genre="thriller"),
    "supernatural_tv": show_source(genre="(supernatural OR tag:paranormal)"),
    
    # --- NETWORK SPECIFIC ---
    "hbo_drama_tv": show_source(genre="drama", studio="HBO", extra=NO_SITCOM),
    "hbo_comedy_tv": show_source(genre="comedy", studio="HBO"),
    "showtime_drama_tv": show_source(genre="drama", studio="Showtime", extra=NO_SITCOM),
    "amc_drama_tv": show_source(genre="drama", studio="AMC", extra=NO_SITCOM),
    "fx_drama_tv": show_source(genre="drama", studio="FX", extra=NO_SITCOM),
    "nbc_sitcoms_tv": show_source(tags="tag:sitcom", studio="NBC"),
    "cbs_sitcoms_tv": show_source(tags="tag:sitcom", studio="CBS"),
    "abc_sitcoms_tv": show_source(tags="tag:sitcom", studio="ABC"),
    "fox_sitcoms_tv": show_source(tags="tag:sitcom", studio="Fox"),
    
    # --- INTERNATIONAL & SPECIALTY ---
    "british_comedy_tv": show_source(genre="comedy", studio="(bbc OR itv)", tags="(tag:sitcom OR genre:comedy)"),
    "british_mystery_tv": show_source(genre="mystery", studio="(bbc OR itv)"),
    "british_drama_tv": show_source(genre="drama", studio="(bbc OR itv)"),
    "bbc_classics_tv": show_source(studio="bbc", era=TV_CLASSIC),
    "family_tv": show_source(rating="(content_rating:TV-G OR content_rating:TV-PG)"),
    "mature_tv": show_source(rating="(content_rating:TV-MA OR content_rating:TV-14)"),
    "kids_tv": show_source(rating="(content_rating:TV-Y OR content_rating:TV-Y7)"),
    "unscripted_alt_tv": show_source(genre="(documentary OR tag:alternative)", extra="(title:*Wilson* OR title:*Nathan*)"),
    "reality_classic_tv": show_source(genre="reality", era=TV_GOLDEN_AGE),
    "reality_competition_tv": show_source(genre="reality", tags="tag:competition"),
    "documentary_tv": show_source(genre="documentary"),
    "talk_show_tv": show_source(tags="(tag:talk-show OR tag:late-night)"),
    "legal_drama_tv": show_source(genre="drama", tags="(tag:legal OR tag:courtroom)", extra=NO_SITCOM),
    "medical_drama_tv": show_source(genre="drama", tags="(tag:medical OR tag:hospital)", extra=NO_SITCOM),
    "military_tv": show_source(tags="(tag:military OR tag:war)"),
    "sports_drama_tv": show_source(genre="drama", tags="tag:sports", extra=NO_SITCOM),
    "teen_drama_tv": show_source(genre="drama", tags="(tag:teen OR tag:high-school)", extra=NO_SITCOM),
    "workplace_comedy_tv": show_source(tags="tag:sitcom", extra="tag:workplace"),
    "family_drama_tv": show_source(genre="drama", tags="tag:family", extra=NO_SITCOM),
    
    # --- ERA CATCH-ALLS ---
    "vintage_tv": show_source(era=TV_VINTAGE),
    "retro_tv": show_source(era=TV_CLASSIC),
    "golden_age_tv": show_source(era=TV_GOLDEN_AGE),
    "hd_era_tv": show_source(era=TV_HD),

    # --- SPECIFIC SHOWS (Legacy/Unrefactored) ---
    # These should be moved to inline definitions in collections.py eventually
    "i_love_lucy_tv": show_by_title("i love lucy"),
    "andy_griffith_tv": show_by_title("the andy griffith show"),
    "dick_van_dyke_tv": show_by_title("the dick van dyke show"),
    "bewitched_tv": show_by_title("bewitched"),
    "gilligans_island_tv": show_by_title("gilligan's island"),
    "mary_tyler_moore_tv": show_by_title("the mary tyler moore show"),
    "bob_newhart_tv": show_by_title("the bob newhart show"),
    "mash_tv": show_by_title("m*a*s*h"),
    "good_times_tv": show_by_title("good times"),
    "sanford_and_son_tv": show_by_title("sanford and son"),
    "taxi_tv": show_by_title("taxi"),
    "cheers_tv": show_by_title("cheers"),
    "wonder_years_tv": show_by_title("the wonder years"),
    "family_matters_tv": show_by_title("family matters"),
    "perfect_strangers_tv": show_by_title("perfect strangers"),
    "full_house_tv": show_by_title("full house"),
    "coach_tv": show_by_title("coach"),
    "seinfeld_tv": show_by_title("seinfeld"),
    "fresh_prince_tv": show_by_title("the fresh prince of bel-air"),
    "saved_by_the_bell_tv": show_by_title("saved by the bell"),
    "sister_sister_tv": show_by_title("sister, sister"),
    "moesha_tv": show_by_title("moesha"),
    "mr_cooper_tv": show_by_title("hangin' with mr. cooper"),
    "home_improvement_tv": show_by_title("home improvement"),
    "drew_carey_tv": show_by_title("the drew carey show"),
    "newsradio_tv": show_by_title("newsradio"),
    "3rd_rock_tv": show_by_title("3rd rock from the sun"),
    "wings_tv": show_by_title("wings"),
    "mad_about_you_tv": show_by_title("mad about you"),
    "nanny_tv": show_by_title("the nanny"),
    "married_children_tv": show_by_title("married... with children"),
    "dinosaurs_tv": show_by_title("dinosaurs"),
    "the_office_tv": show_by_title("the office"),
    "parks_and_recreation_tv": show_by_title("parks and recreation"),
    "30_rock_tv": show_by_title("30 rock"),
    "community_tv": show_by_title("community"),

    # --- 80s CHANNEL SPECIFIC ---
    "eighties_cartoons_heman": show_by_title("He-Man and the Masters of the Universe"),
    "eighties_cartoons_transformers": show_by_title("The Transformers"),
    "eighties_cartoons_gi_joe": show_by_title("G.I. Joe: A Real American Hero"),
    "eighties_cartoons_smurfs": show_by_title("The Smurfs"),
    "eighties_sitcom_family_ties": show_by_title("Family Ties"),
    "eighties_sitcom_growing_pains": show_by_title("Growing Pains"),
    "eighties_sitcom_full_house": show_by_title("Full House"),
    "eighties_action_tv": show_source(genre="action", era=EIGHTIES),
    "eighties_drama_tv": show_source(genre="drama", era=EIGHTIES),
    "eighties_daytime_movie": movie_source(era=EIGHTIES, extra=NO_HORROR),
    "eighties_crime_tv": show_source(genre="crime", era=EIGHTIES),
    "eighties_suspense_movie": movie_source(genre="thriller", era=EIGHTIES),
    "eighties_action_knight_rider": show_by_title("Knight Rider"),
    "eighties_action_airwolf": show_by_title("Airwolf"),
    "eighties_sitcom_cheers": show_by_title("Cheers"),
    "eighties_sitcom_golden_girls": show_by_title("The Golden Girls"),
    "eighties_sitcom_night_court": show_by_title("Night Court"),
    "eighties_crime_miami_vice": show_by_title("Miami Vice"),
    "eighties_crime_magnum_pi": show_by_title("Magnum, P.I."),
    "eighties_sitcom_cosby_show": show_by_title("The Cosby Show"),
    "eighties_blockbuster_movie": movie_source(era=EIGHTIES, tags="tag:blockbuster"),
    "movie_intro_bumper": 'type:"other_video" AND tag:intro AND tag:movie',
    "eighties_scifi_star_trek": show_by_title("Star Trek: The Next Generation"),
    "eighties_scifi_v": show_by_title("V"),
    "eighties_drama_movie": movie_source(genre="drama", era=EIGHTIES),
    "eighties_music_videos": 'type:"music_video" AND year:[1980 TO 1989]',
    "eighties_weekend_movie": movie_source(era=EIGHTIES),
    "eighties_cult_movie": movie_source(era=EIGHTIES, tags="tag:cult"),
    "commercials_80s_spot": 'type:"other_video" AND tag:commercial AND tag:80s',

    # --- SPECIFIC SHOWS (Chronological/Themed) ---
    "devs_chronological_tv": playback_order(show_by_title("Devs"), force="Chronological"),
    "the_oa_chronological_tv": playback_order(show_by_title("The OA"), force="Chronological"),
    "black_mirror_chronological_tv": playback_order(show_by_title("Black Mirror"), force="Chronological"),
    "terminator_scc_chronological_tv": playback_order(show_by_title("Terminator: The Sarah Connor Chronicles"), force="Chronological"),
    "dark_angel_chronological_tv": playback_order(show_by_title("Dark Angel"), force="Chronological"),
    "firefly_chronological_tv": playback_order(show_by_title("Firefly"), force="Chronological"),
    "cleopetra_2525_chronological_tv": playback_order(show_by_title("Cleopatra 2525"), force="Chronological"),
    "farscape_chronological_tv": playback_order(show_by_title("Farscape"), force="Chronological"),
    "quantum_leap_chronological_tv": playback_order(show_by_title("Quantum Leap"), force="Chronological"),
    "monk_chronological_tv": playback_order(show_by_title("Monk"), force="Chronological"),

    # --- SPECIFIC SHOWS (Halloween/Themed) ---
    "scooby_doo_tv": show_by_title("Scooby-Doo, Where Are You!"),
    "gravity_falls_tv": show_by_title("Gravity Falls"),
    "infinity_train_tv": show_by_title("Infinity Train"),
    "courage_tv": show_by_title("Courage the Cowardly Dog"),
    "metalocalypse_tv": show_by_title("Metalocalypse"),
    "elsbeth_tv": show_by_title("Elsbeth"),
    "moonlighting_tv": show_by_title("Moonlighting"),
    "poirot_tv": show_by_title("Agatha Christie's Poirot"),
    "miss_marple_tv": show_by_title("Miss Marple"),
    "columbo_tv": show_by_title("Columbo"),
    "orville_tv": show_by_title("The Orville"),
    "knight_rider_tv": show_by_title("Knight Rider"),
    "pushing_daisies_tv": show_by_title("Pushing Daisies"),
    "the_killing_tv": show_by_title("The Killing"),
    "terriers_tv": show_by_title("Terriers"),
    "dollhouse_tv": show_by_title("Dollhouse"),
    "awake_tv": show_by_title("Awake"),
    "stargate_sg1_tv": show_by_title("Stargate SG-1"),
}

# ============================================================================
# 3. ANIMATED (FILTERS & GENRES)
# ============================================================================

ANIMATED_REGISTRY = {
    # --- BROAD TOOLS ---
    "animated_sitcoms_tv": show_source(tags="tag:sitcom", animated=True),
    "adult_animation_tv": show_source(tags="tag:sitcom", rating="(content_rating:TV-MA OR content_rating:TV-14)", animated=True),
    "family_animation_tv": show_source(tags="tag:sitcom", rating="(content_rating:TV-G OR content_rating:TV-PG OR content_rating:TV-Y7)", animated=True),
    "anime_tv": f"{SHOW} AND {ANIME}",
    "anime_action_tv": f"{SHOW} AND {ANIME} AND genre:action",
    "animated_action_tv": show_source(genre="action", animated=True, extra=NO_SITCOM),
    "animated_90s_tv": show_source(era=NINETIES, animated=True),
    "animated_classic_tv": show_source(era=TV_CLASSIC, animated=True),
    "superhero_animated_tv": show_source(tags="(tag:superhero OR tag:marvel OR tag:dc)", animated=True),
}

# ============================================================================
# 4. THEME & HOLIDAY REGISTRY
# ============================================================================

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
    "classic_hollywood_fall_movies": apply_tags(MOVIE_REGISTRY["classic_hollywood_movie"], FALL_TAGS),
    "classic_hollywood_spring_movies": apply_tags(MOVIE_REGISTRY["classic_hollywood_movie"], SPRING_TAGS),
}

# 5. FILLERS & BUMPERS
#
# ErsatzTV derives Other Video tags from the folder path: every path segment
# below the library root's PARENT becomes its own flat tag
# (ErsatzTV.Core/Metadata/FallbackMetadataProvider.cs::GetOtherVideoMetadata).
# Tags carry no hierarchy, so two folders with the same name anywhere in the
# tree produce the same tag and must be disambiguated by AND-ing a parent tag.
#
# Two indexed fields exist for the same tag value (LuceneSearchIndex.cs:1275):
#   tag       TextField   -> whitespace-tokenized + lowercased. "eureka" also
#                            matches the "eureka 7" folder.
#   tag_full  StringField -> KeywordAnalyzer: whole value, case-sensitive.
# Folder names on disk are lowercase, so tag_full queries are written lowercase.
# Prefer tag_full for anything that must address exactly one folder.

def filler_source(*folders):
    """Exact other_video query from folder-derived tags (all must be present)."""
    return 'type:"other_video" AND ' + " AND ".join(f'tag_full:"{f}"' for f in folders)


# Toonami per-show bumper folders, one key each. These ~940 files were
# previously reachable only by a broad tag query and referenced by nothing.
# Folder names match the library title exactly wherever the show is owned, so
# dispatcher.play_smart_bumper resolves them from the scheduled title with no
# key at all. The keys below stay useful for explicit block-level branding.
TOONAMI_SHOW_FOLDERS = [
    "akira", "astro boy", "attack on titan", "beware the batman", "big o",
    "black lagoon", "bleach", "blue exorcist", "cowboy bebop", "dragon ball z",
    "eureka seven", "flcl", "fullmetal alchemist brotherhood",
    "ghost in the shell", "igpx", "inuyasha", "kickheart", "korgoth", "naruto",
    "naruto shippuden", "neon genesis evangelion", "one piece", "samurai 7",
    "samurai jack", "soul eater", "space dandy", "star wars the clone wars",
    "summer wars", "sword art online", "sym-bionic titan", "thundercats",
    "yu yu hakusho",
]

# Adult Swim show folders cut out of bumps/ by filename match (>=5 files each).
ADULT_SWIM_SHOW_FOLDERS = [
    "aqua teen hunger force", "check it out with dr steve brule",
    "childrens hospital", "china il", "cowboy bebop", "delocated", "eagleheart",
    "family guy", "flcl", "futurama", "harvey birdman attorney at law",
    "inuyasha", "king of the hill", "loiter squad", "lupin the third",
    "metalocalypse", "moral orel", "rick and morty", "robot chicken",
    "sealab 2021", "space ghost coast to coast", "squidbillies", "superjail",
    "the boondocks", "the brak show", "the eric andre show",
    "the heart she holler", "the room", "the venture bros",
    "tim and eric awesome show great job", "trigun", "xavier renegade angel",
]

def _show_keys(prefix, folder, names):
    return {
        f"{prefix}_{n.replace(' ', '_').replace('-', '_')}_bumpers":
            filler_source(folder, "shows", n)
        for n in names
    }

TOONAMI_SHOW_BUMPERS = _show_keys("toonami", "toonami", TOONAMI_SHOW_FOLDERS)
ADULT_SWIM_SHOW_BUMPERS = _show_keys("adult_swim", "adult swim", ADULT_SWIM_SHOW_FOLDERS)

FILLERS = {
    # --- COMMERCIALS ---
    # Folder path is country / decade / audience-gate / product, so any
    # combination of those is an AND of flat tags. The gate level is the one
    # that matters for scheduling: "alcohol" must never reach a kids daypart.
    "commercials_spot": 'type:"other_video" AND tag_full:"commercials"',
    # Excludes alcohol. This is the key a kids or daytime channel should use.
    "commercials_family_safe_spot":
        'type:"other_video" AND tag_full:"commercials" AND NOT tag_full:"alcohol"',

    # audience gate
    "commercials_kids_spot": filler_source("commercials", "kids"),
    "commercials_alcohol_spot": filler_source("commercials", "alcohol"),
    "commercials_christmas_spot": filler_source("commercials", "christmas"),
    "commercials_general_spot": filler_source("commercials", "general"),

    # country
    "commercials_uk_spot": filler_source("commercials", "uk"),
    "commercials_us_spot": filler_source("commercials", "us"),
    "commercials_au_spot": filler_source("commercials", "au"),

    # decade. The bare decade keys predate the country split and still resolve,
    # since every path segment is its own tag.
    "commercials_80s_spot_folder": filler_source("commercials", "80s"),
    "commercials_90s_spot": filler_source("commercials", "90s"),
    "commercials_00s_spot": filler_source("commercials", "00s"),
    "commercials_uk_80s_spot": filler_source("commercials", "uk", "80s"),
    "commercials_uk_90s_spot": filler_source("commercials", "uk", "90s"),

    # useful crosses
    "commercials_uk_kids_spot": filler_source("commercials", "uk", "kids"),
    "commercials_uk_90s_kids_spot": filler_source("commercials", "uk", "90s", "kids"),
    "commercials_uk_90s_general_spot": filler_source("commercials", "uk", "90s", "general"),
    "commercials_uk_90s_alcohol_spot": filler_source("commercials", "uk", "90s", "alcohol"),

    # product, across every country and decade
    **{f"commercials_{c.replace(' ', '_')}_spot": filler_source("commercials", c)
       for c in ("cereal", "confectionery", "snacks", "drinks", "food", "toys",
                 "retail", "household", "tech", "leisure", "psa", "beer", "spirits")},

    # --- ADULT SWIM ---
    "adult_swim_intro": filler_source("adult swim", "intro"),
    "adult_swim_outro": filler_source("adult swim", "outro"),
    "adult_swim_bumpers": filler_source("adult swim", "bumps"),
    "adult_swim_bumpers_general": filler_source("adult swim", "bumps", "general"),
    "adult_swim_april_fools": filler_source("adult swim", "april fools"),
    # childrens hospital / the room are generated into ADULT_SWIM_SHOW_BUMPERS
    "adult_swim_marathon": filler_source("adult swim", "marathon"),
    "adult_swim_marathon_astro_boy": filler_source("adult swim", "marathon", "astro boy"),
    "adult_swim_marathon_cowboy_bebop": filler_source("adult swim", "marathon", "cowboy bebop"),
    "adult_swim_marathon_yu_yu_hakusho": filler_source("adult swim", "marathon", "yu yu hakusho"),

    # Sub-pools of adult swim/bumps. Each is also inside adult_swim_bumpers.
    "adult_swim_schedules": filler_source("adult swim", "bumps", "schedules"),
    "adult_swim_tagged_videos": filler_source("adult swim", "bumps", "tagged videos"),
    "adult_swim_pool": filler_source("adult swim", "bumps", "pool"),
    "adult_swim_fan_service": filler_source("adult swim", "bumps", "fan service"),

    # --- ADULT SWIM SEASONAL (233 files; inventory recorded this tree as empty) ---
    "adult_swim_seasonal_christmas": filler_source("adult swim", "seasonal", "christmas"),
    "adult_swim_seasonal_halloween": filler_source("adult swim", "seasonal", "halloween"),
    "adult_swim_seasonal_thanksgiving": filler_source("adult swim", "seasonal", "thanksgiving"),
    "adult_swim_seasonal_holidays": filler_source("adult swim", "seasonal", "holidays"),
    "adult_swim_seasonal_winter": filler_source("adult swim", "seasonal", "winter"),
    "adult_swim_seasonal_spring": filler_source("adult swim", "seasonal", "spring"),
    "adult_swim_seasonal_summer": filler_source("adult swim", "seasonal", "summer"),
    "adult_swim_seasonal_fall": filler_source("adult swim", "seasonal", "fall"),

    # --- TOONAMI ---
    "toonami_intro": filler_source("toonami", "intro"),
    "toonami_outro": filler_source("toonami", "outro"),
    # Generic (non-show) Toonami pool. Still only 21 files: 93 more sit loose at
    # the toonami/ root and pick up no second tag until they move into general/.
    "toonami_bumpers": 'type:"other_video" AND tag_full:"toonami" AND (tag_full:"bumps" OR tag_full:"general")',
    # Everything under toonami/, per-show sets included (~940).
    "toonami_all_bumpers": filler_source("toonami"),
    "toonami_marathon_cowboy_bebop": filler_source("toonami", "marathon", "cowboy bebop"),
    "toonami_dragon_ball_z_coolers_revenge": filler_source("toonami", "dragon ball z", "coolers revenge"),

    **TOONAMI_SHOW_BUMPERS,
    **ADULT_SWIM_SHOW_BUMPERS,

    # Back-compat alias; prefer toonami_cowboy_bebop_bumpers.
    "cowboy_bebop_bumpers": filler_source("toonami", "shows", "cowboy bebop"),
}

# 7. TEST KEYS
TEST_REGISTRY = {
    "test_monk_morning": episode_list(
        "Monk", 
        seasons=[1, 2, 3, 4, 5, 6, 7, 8], 
        counts=[13, 16, 16, 16, 16, 16, 16, 16]
    ),
    "test_monk_evening": episode_list(
        "Monk", 
        seasons=[1, 2, 3, 4, 5, 6, 7, 8], 
        counts=[13, 16, 16, 16, 16, 16, 16, 16]
    ),
}

# 6. THE MASTER EXPORT

MASTER_SOURCES = {
    **MOVIE_REGISTRY,
    **PLAYLIST_REGISTRY,
    **TV_REGISTRY,
    **ANIMATED_REGISTRY,
    **THEME_REGISTRY,
    **MARATHONS,
    **SEASONAL_VARIANTS,
    **FILLERS,
    **TEST_REGISTRY
}
