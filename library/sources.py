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
    ANIME, ANIMATED, MOVIE, SHOW
)
from scripts.logic.factories import episode_list
# Import filter constants from our local library
from .filters import (
    NINETIES, EIGHTIES, STREAMING_ERA, CLASSIC_ERA,
    WINTER_TAGS, SUMMER_TAGS,
    FALL_TAGS, SPRING_TAGS, SILENT_ERA, GOLDEN_AGE, SEVENTIES, Y2K_ERA, TENS, TWENTIES,
    SHORT, NO_COMEDY, NO_HORROR,
    TV_CLASSIC, TV_GOLDEN_AGE, TV_HD, TV_VINTAGE,
    NO_FANTASY, NO_SITCOM, NO_BBC, NO_SCIFI, NO_WESTERN, MODERN_FILM_ERA, PRE_EIGHTIES_ERA,
    POST_EIGHTIES_ERA, RECENT_ERA, NEW_RELEASE_ERA,
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
    # Same era with science fiction and westerns removed: ~108 films of the 137.
    # Classic Cinema's morning block used the unfiltered key, which put Forbidden
    # Planet, Day the Earth Stood Still, Godzilla and 15 others on it at the
    # same hour Other Worlds airs `classic_scifi_movie` -- the same 1950-69
    # shelf. Westerns joined the exclusion when High Noon was built: the 1950-69
    # slice is The Searchers, Shane, Giant, The Magnificent Seven, the Leone
    # trilogy and Butch Cassidy -- eleven films that are the western channel's
    # centre, not Classic Cinema's afternoon. Follows the `_pure_` convention:
    # the era minus what another channel owns.
    # Horror joined the exclusion when Be Kind Rewind was built and Classic
    # Cinema was restated as a pre-1980 channel: Nightmare Theatre's
    # `horror_movie` draws every era, so the 1950-69 slice -- Psycho, The
    # Birds, Village of the Damned -- was reachable from both channels.
    # 108 -> 99.
    "classic_hollywood_pure_movie": movie_source(era=CLASSIC_ERA, extra=f"{NO_SCIFI} AND {NO_WESTERN} AND {NO_HORROR}"),
    "film_history_all_movie": movie_source(era=CLASSIC_ERA),
    "70s_movie": movie_source(era=SEVENTIES),
    "80s_movie": movie_source(era=EIGHTIES),
    # The two decades minus the horror shelf, on the `_pure_` convention: the
    # era with what another channel owns taken out. Classic Cinema's weekday
    # prime is New Hollywood, and the unfiltered keys put 67 eighties horror
    # films and 20 seventies ones on it -- the same films Nightmare Theatre runs
    # at 22:00. The Eighties channel had already drawn this line for itself:
    # `eighties_daytime_movie` has carried NOT genre:horror all along.
    # 137 -> 117 and 296 -> 229.
    "70s_pure_movie": movie_source(era=SEVENTIES, extra=NO_HORROR),
    # Westerns joined the exclusion when Be Kind Rewind took this key over as
    # its late shelf: High Noon draws `western_movie` across every era and runs
    # film to midnight, so the two channels shared Silverado and Young Guns.
    "80s_pure_movie": movie_source(era=EIGHTIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "90s_movie": movie_source(era=NINETIES),
    "00s_movie": movie_source(era=Y2K_ERA),
    "10s_movie": movie_source(era=TENS),
    "20s_movie": movie_source(era=TWENTIES),

    # --- CABES CLASSIC CINEMA -- the pre-1980 shelf ---
    #
    # The channel is 1920-1979 outright: 328 live-action films, a 25-day cycle
    # at 24 hours a day. It gave the 1980s to Totally 80s and Be Kind Rewind
    # when the era line was drawn, which is what turned it from a residue into
    # a channel -- see `library/movies.py`.
    #
    # These keys carry NO_HORROR / NO_SCIFI / NO_WESTERN not because sharing is
    # forbidden -- it is not -- but because Nightmare Theatre, Other Worlds and
    # High Noon all draw *every* era for those genres, so the same title really
    # would land on two channels. The exclusions are an hours problem solved at
    # the key, which is cheaper here than re-timing four channels.

    # The wide pre-1980 shelf, and the channel's fallback bed. 241 films.
    # Everything the channel can reach without stepping on a genre channel.
    "classic_cinema_movie": movie_source(era=PRE_EIGHTIES_ERA, extra=f"{NO_HORROR} AND {NO_SCIFI} AND {NO_WESTERN}"),   # 241
    # 1930-49 without the Universal monsters, which are Nightmare Theatre's
    # 09:00 Vault. 41 -> 36.
    "golden_age_pure_movie": movie_source(era=GOLDEN_AGE, extra=NO_HORROR),                                             #  36
    # The 1970s as Classic Cinema's prime. `70s_pure_movie` above drops horror
    # only; this also drops westerns, because High Noon runs film 20:00-24:00
    # and that is exactly this block's hours. 137 -> 114.
    "70s_prestige_movie": movie_source(era=SEVENTIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),                           # 114
    # Era-bounded genre cuts. The unbounded `musical_movie` and `war_movie` were
    # on Classic Cinema's weekend prime while reaching every era, which is how a
    # pre-1980 channel was scheduling 2018 musicals. Note how thin the musical
    # shelf actually is before 1980 -- six films, which is why MUSICAL_MARQUEE
    # could never have carried a slot on its own.
    "classic_musical_movie": movie_source(genre="musical", era=PRE_EIGHTIES_ERA),                                       #   6
    "classic_war_movie": movie_source(genre="war", era=PRE_EIGHTIES_ERA),                                               #  29
    "classic_comedy_movie": movie_source(genre="comedy", era=PRE_EIGHTIES_ERA),                                         #  90
    "classic_drama_movie": movie_source(genre="drama", era=PRE_EIGHTIES_ERA, extra=f"NOT genre:crime AND {NO_WESTERN}"), # 129
    # The big-canvas pictures -- Lawrence of Arabia, Ben-Hur, Bridge on the River
    # Kwai, The Great Escape. Adventure and history minus the two genres that
    # have their own channels.
    "classic_epic_movie": movie_source(genre="(adventure OR history)", era=PRE_EIGHTIES_ERA, extra=f"{NO_WESTERN} AND {NO_SCIFI}"),  # 57

    # --- BE KIND REWIND -- the 1980-and-after shelf ---
    #
    # 1,530 live-action films, a 122-day cycle at 24 hours a day: by a wide
    # margin the largest pool on the lineup, and the reason this channel can
    # afford to sub-sort by genre, decade and director where the others cannot.
    #
    # Nothing here is exclusive. Totally 80s, Other Worlds, Mystery Theatre and
    # Nightmare Theatre all keep their full claims and Be Kind Rewind overlaps
    # every one of them; the rule is that the same title must not air on two
    # channels in the same hour, and that is enforced by the grid (see
    # `channels/be_kind_rewind.py`) rather than by fencing pools off.

    # Every `modern_*` key below is **1990 and after**, not 1980, and that is the
    # hours rule made structural rather than left to the grid to remember.
    #
    # Be Kind Rewind's pool is 1980+, but Totally 80s runs film from 10:00 to
    # 23:00 and the two channels would otherwise draw the same 1980s title in
    # the same hour -- which the collision report caught on the first build, as
    # `modern_drama_movie` against `eighties_drama_movie` on Sunday prime. The
    # 1980s are reachable on this channel only through the explicitly-80s keys
    # (`80s_pure_movie`, `eighties_cult_movie`, `80s_action_movie`,
    # `80s_comedy_movie`), and those are scheduled only between 22:00 and 06:00,
    # when Totally 80s is dark. A key that cannot reach the decade cannot
    # collide on it by accident three refactors from now.
    #
    # `80s_pure_movie` was Cabes Classic Cinema's weekday prime until the era
    # line moved; it is this channel's late shelf now, which is the same 229
    # films finding a set of hours nobody else wants.

    # The channel-wide shelf and its fallback bed. Horror and westerns are out
    # at the key because Nightmare Theatre and High Noon draw every era of both
    # and run film in this channel's prime; everything else is deconflicted by
    # hours instead.
    "modern_cinema_movie": movie_source(era=POST_EIGHTIES_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),                  # 1090
    # Recency, the channel's one genuine promise. `recent_movie` is wide enough
    # to carry a nightly presence; `new_release_movie` is the Friday appointment
    # and cycles in a little over a year at two features a week.
    "recent_movie": movie_source(era=RECENT_ERA, extra=NO_HORROR),                                                      #  ~205
    "new_release_movie": movie_source(era=NEW_RELEASE_ERA, extra=NO_HORROR),                                            #  ~105
    # Genre cuts across the whole modern era.
    "modern_action_movie": movie_source(genre="action", era=POST_EIGHTIES_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),    #  475
    "modern_comedy_movie": movie_source(genre="comedy", era=POST_EIGHTIES_ERA, extra=NO_HORROR),                          #  562
    "modern_drama_movie": movie_source(genre="drama", era=POST_EIGHTIES_ERA, extra=f"{NO_HORROR} AND NOT genre:crime"),   #  480
    "modern_adventure_movie": movie_source(genre="adventure", era=POST_EIGHTIES_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),  # 387
    "modern_family_movie": movie_source(genre="family", era=POST_EIGHTIES_ERA),                                           #  113
    "modern_romance_movie": movie_source(genre="romance", era=POST_EIGHTIES_ERA),                                         #  207
    # The one key that needs every exclusion spelled out. Thriller is 470 films
    # from 1980 on, but crime/mystery is Mystery Theatre's, science fiction is
    # Other Worlds' and horror is Nightmare Theatre's -- and all three draw the
    # modern era. Only 72 thrillers are genuinely nobody else's spine, and a
    # bare `genre:thriller` key would quietly re-open three borders at once.
    "modern_thriller_movie": movie_source(
        genre="thriller", era=POST_EIGHTIES_ERA,
        extra=f"NOT genre:crime AND NOT genre:mystery AND {NO_SCIFI} AND {NO_HORROR}"
    ),                                                                                                                  #   72
    # The decade shelves, horror and westerns removed -- the `_pure_` convention
    # the rest of the registry already uses. Be Kind Rewind runs these in its
    # afternoon, which is exactly when Nightmare Theatre draws `horror_movie`
    # (every era) and High Noon draws `western_movie` (every era). Neither of
    # those channels has an hour to hide in -- Nightmare runs seventeen hours
    # of film a day -- so this border is kept at the key.
    #
    # Measured, not assumed: `scripts/testing/same_title_check.py` resolves both
    # keys' queries against the library and intersects the title sets. The raw
    # `90s_movie` shares 29 titles with `horror_movie` and aired opposite it
    # nineteen times in a fortnight.
    "90s_pure_movie": movie_source(era=NINETIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "00s_pure_movie": movie_source(era=Y2K_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "10s_pure_movie": movie_source(era=TENS, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "20s_pure_movie": movie_source(era=TWENTIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),

    # Genre x decade. The registry had these for the 80s and 90s only, so every
    # decade after 1999 could be reached as a whole or not at all. Same two
    # exclusions, for the same reason: a bare `genre:drama` cut of the 2010s
    # reaches Black Swan, Crimson Peak and Bone Tomahawk.
    "00s_action_movie": movie_source(genre="action", era=Y2K_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "10s_action_movie": movie_source(genre="action", era=TENS, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "20s_action_movie": movie_source(genre="action", era=TWENTIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "00s_comedy_movie": movie_source(genre="comedy", era=Y2K_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "10s_comedy_movie": movie_source(genre="comedy", era=TENS, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "20s_comedy_movie": movie_source(genre="comedy", era=TWENTIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "90s_drama_movie": movie_source(genre="drama", era=NINETIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "00s_drama_movie": movie_source(genre="drama", era=Y2K_ERA, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    "10s_drama_movie": movie_source(genre="drama", era=TENS, extra=f"{NO_HORROR} AND {NO_WESTERN}"),

    # --- ANIMATION (FILM) ---
    "animation_movie": movie_source(animated=True),
    "classic_animation_movie": movie_source(animated=True, era=CLASSIC_ERA, extra=SHORT),
    # `genre:anime` is on two films in the whole library -- Laid-Back Camp the
    # Movie and the 1986 Transformers -- so the tag cannot carry a film channel
    # (G11). Japanorama's shelves below are named title by title instead, which
    # is also the only form `key_census` can size: `library-movies.tsv` carries
    # no studio column, so a studio-based film key resolves to "not in
    # manifests" and is never checked against anything.
    "anime_movie": f"{MOVIE} AND {ANIME}",
    "disney_movie": movie_source(animated=True, studio="Disney"),
    "pixar_movie": movie_source(animated=True,studio="Pixar"),
    "dreamworks_movie": movie_source(studio="Dreamworks"),

    # --- FAMILY & RATING ---
    "family_g_movie": movie_source(rating="content_rating:G"),
    "family_pg_movie": movie_source(rating="content_rating:PG"),
    "kids_safe_movie": movie_source(rating="(content_rating:TV-G OR content_rating:TV-Y)"),

    # --- HORROR VAULT ---
    # Three era shelves, not two. 242 non-animated horror films is five times the
    # western pool, and Nightmare Theatre runs seventeen hours of film a day --
    # a single `horror_movie` key on the whole grid would cycle the same shelf
    # through breakfast and midnight alike.
    #
    # `classic_horror_movie` was `era=EIGHTIES` and meant the 1980s, which is
    # not what "classic horror" names anywhere else. It is now the pre-1980
    # shelf it sounds like -- Nosferatu, Frankenstein, Freaks, King Kong,
    # Godzilla, Body Snatchers, Psycho, Night of the Living Dead, The Exorcist,
    # Texas Chain Saw, Jaws, Halloween, Alien -- and the old 1980s definition
    # moved to `eighties_horror_movie` unchanged. The only consumer was
    # `movies.HORROR_VAULT`, which no channel scheduled, so nothing on air
    # changed meaning under it.
    "classic_horror_movie": movie_source(genre="horror", era=PRE_EIGHTIES_ERA, extra=NO_COMEDY),   #  39
    "eighties_horror_movie": movie_source(genre="horror", era=EIGHTIES, extra=NO_COMEDY),          #  50
    "modern_horror_movie": movie_source(genre="horror", era=POST_EIGHTIES_ERA, extra=NO_COMEDY),   # 102
    # The whole shelf, comedies still out. For the wide afternoon block that is
    # allowed to draw any era -- the one place the channel puts 1931 Frankenstein
    # next to 2018 Hereditary on purpose.
    "horror_movie": movie_source(genre="horror", extra=NO_COMEDY),                                 # 191
    # The 51 films every other horror key throws away. NO_COMEDY is right for a
    # block that means to frighten and wrong as a library policy: it discards
    # An American Werewolf in London, Re-Animator, Return of the Living Dead,
    # Fright Night, Gremlins, Creepshow, Evil Dead II and Shaun of the Dead.
    # They are not a lesser horror shelf, they are a different room -- Saturday
    # night, after the appointment.
    "horror_comedy_movie": movie_source(genre="horror", extra="genre:comedy"),                     #  51
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
    # The 1990s pair carry the same two exclusions as their 2000s and 2010s
    # equivalents below -- they are Be Kind Rewind's afternoon and had been in
    # the registry, unclaimed, since before any of the genre channels existed.
    "90s_action_movie": movie_source(genre="action", era=NINETIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    # Era-bounded when Be Kind Rewind took it up. It had no date filter at all,
    # so a "blockbuster" key reached pre-1980 superhero film -- straight into
    # Classic Cinema's decades. Nothing caught it because the key sat in
    # `movies.MODERN_BLOCKBUSTERS`, which no channel had scheduled since
    # Classic Cinema gave up its summer swap.
    "blockbuster_action_movie": movie_source(genre="action", era=POST_EIGHTIES_ERA, tags="(studio:Marvel OR studio:DC OR tag:superhero)"),
    "80s_comedy_movie": movie_source(genre="comedy", era=EIGHTIES),
    "90s_comedy_movie": movie_source(genre="comedy", era=NINETIES, extra=f"{NO_HORROR} AND {NO_WESTERN}"),
    # High Noon's shelf, all 46 films. Cabes Classic Cinema used to run the whole
    # of it across both weekend afternoons; it handed the pool back when the
    # western channel was built, the same way Other Worlds took science fiction.
    "western_movie": movie_source(genre="western"),                                   #  46
    # The two halves, for when a block wants one era rather than the shelf.
    # Both are High Noon's -- this is not an ownership split like the crime keys.
    "classic_western_movie": movie_source(genre="western", era=PRE_EIGHTIES_ERA),     #  17
    "modern_western_movie": movie_source(genre="western", era=MODERN_FILM_ERA),       #  29
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
    # The crime/mystery shelf, split by era so Classic Cinema and Mystery
    # Theatre never draw the same film. Together these are `mystery_crime_movie`,
    # which neither channel should schedule directly.
    "classic_crime_movie": movie_source(genre="(mystery OR crime)", era=PRE_EIGHTIES_ERA, extra=NO_COMEDY),  #  74
    "modern_crime_movie": movie_source(genre="(mystery OR crime)", era=MODERN_FILM_ERA, extra=NO_COMEDY),    # 291
    "classic_noir_movie": movie_source(genre="crime", era=GOLDEN_AGE),

    # --- FANTASY ---
    # Counts are live-action titles on disk as of the 2026-08-30 census
    # (media/ANALYSIS.md). movie_source() excludes animation by default, so the
    # live-action figure is the one these keys actually return; the raw Fantasy
    # tag covers 333 films, 95 of them animated.
    "fantasy_movie": movie_source(genre="fantasy"),                                    # 238
    "fantasy_pure_movie": movie_source(genre="fantasy", extra=NO_SCIFI),               # 185
    "fantasy_adventure_movie": movie_source(genre="fantasy", extra="genre:adventure"), # 102
    "fantasy_comedy_movie": movie_source(genre="fantasy", extra="genre:comedy"),       #  97
    "epic_fantasy_movie": movie_source(genre="fantasy", tags="(tag:epic OR tag:sword)"),
    "dark_fantasy_movie": movie_source(genre="fantasy", extra="genre:horror"),         #  54
    "fairytale_movie": movie_source(genre="fantasy", extra="genre:family"),            #  46
    "animated_fantasy_movie": movie_source(genre="fantasy", animated=True),            #  95
    "classic_fantasy_movie": movie_source(genre="fantasy", era=CLASSIC_ERA),
    "80s_fantasy_movie": movie_source(genre="fantasy", era=EIGHTIES),                  #  45
    "90s_fantasy_movie": movie_source(genre="fantasy", era=NINETIES),                  #  59
    "modern_fantasy_movie": movie_source(genre="fantasy", era=STREAMING_ERA),          #  63

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

# `studio:(bbc OR itv)` is BBC and ITV only, and that silently excluded the whole
# Channel 4 canon -- Peep Show, Father Ted, The IT Crowd, Spaced, Derry Girls,
# Toast of London, Garth Marenghi's Darkplace, Queer as Folk -- plus Sky and E4.
# Twelve shows and 287 episodes, including Peep Show, which is the largest
# British comedy on disk. Across the Pond found it; nothing had used the keys.
BRITISH_BROADCASTERS = '(bbc OR itv OR "channel 4" OR "channel 5" OR sky OR e4)'

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
    # The one sci-fi key with no NO_FANTASY clause, so it is the widest pool
    # here -- everything scifi_tv returns plus the shows this library tags as
    # both (Stargate SG-1, Quantum Leap, Xena). Named for what it is: it was
    # `space_opera_tv`, which promised Babylon 5 and delivered Sabrina the
    # Teenage Witch. Real space opera is a title-based collection now.
    "scifi_all_tv": show_source(genre='"science fiction"', extra=NO_SITCOM),
    "animated_scifi_tv": show_source(genre='"science fiction"', animated=True, extra=NO_SITCOM),
    
    # --- FANTASY ---
    # Show/episode counts from the 2026-08-30 census (media/ANALYSIS.md).
    # show_source() excludes animation by default: the Fantasy tag covers 80
    # shows, half of them animated, so the animated pool needs its own key
    # rather than being reachable only by accident.
    "fantasy_pure_tv": show_source(genre="fantasy", extra=f"{NO_SCIFI} AND {NO_SITCOM}"),  # 23 shows / 1,128 eps
    "fantasy_tv": show_source(genre="fantasy", extra=NO_SITCOM),                           # 40 shows / 2,158 eps
    "epic_fantasy_tv": show_source(genre="fantasy", tags="(tag:epic OR tag:sword)", extra=NO_SITCOM),
    "dark_fantasy_tv": show_source(genre="fantasy", extra=f"genre:horror AND {NO_SITCOM}"),  #  8 shows /   219 eps
    "classic_fantasy_tv": show_source(genre="fantasy", era=TV_VINTAGE, extra=NO_SITCOM),
    "modern_fantasy_tv": show_source(genre="fantasy", era=TV_HD, extra=NO_SITCOM),          # 23 shows /   658 eps
    "animated_fantasy_tv": show_source(genre="fantasy", animated=True, extra=NO_SITCOM),    # 40 shows / 3,366 eps
    
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
    # Was `era=TV_CLASSIC` (1976-1989) and returned **nothing**: every classic
    # western in the library is 1955-1959, which is TV_VINTAGE. The key naming
    # High Noon's entire spine resolved to zero shows, and nothing caught it
    # because no channel had ever scheduled it. Now the five B&W network
    # westerns -- Bonanza, Gunsmoke, The Rifleman, Wanted: Dead or Alive,
    # Rawhide -- 946 episodes.
    "classic_western_tv": show_source(genre="western", era=TV_VINTAGE),
    # NO_SCIFI drops Westworld, which carries a Western genre tag and is not one.
    "modern_western_tv": show_source(genre="western", era=STREAMING_ERA, extra=NO_SCIFI),
    # The raw genre tag. Do not schedule this: it also returns Breaking Bad and
    # Westworld, both tagged Western and neither one. Use the era keys above, or
    # name the shows -- which is what `library/western.py` does.
    "western_tv": show_source(genre="western"),
    # The raw genre tag, and the same trap `western_tv` carries. Do not schedule
    # it: genre:horror reaches The X-Files (Other Worlds' Investigation strand),
    # Millennium (Mystery Theatre's anchor) and Beyond Belief (Other Worlds'
    # Saturday), so a horror channel drawing this key airs three other channels'
    # spines. Use `horror_pure_tv` or name the shows.
    "horror_tv": show_source(genre="horror"),
    # Was `era=TV_CLASSIC` (1976-1989) and returned **nothing**, the same class
    # of bug `classic_western_tv` carried: there is no horror television in this
    # library before 1989, and the one 1989 show -- Tales from the Crypt -- is
    # tagged Comedy/Crime/Mystery/Science Fiction and so is not reachable by
    # genre:horror at all. The era that actually holds content is 1989-2009:
    # Nightmare Cafe, Poltergeist: The Legacy and Darkplace, once the other
    # channels' shows are excluded. Named for the window rather than the vibe,
    # because "classic horror TV" is a thing this library does not have.
    "classic_horror_tv": show_source(
        genre="horror",
        era="release_date:[* TO 2009-12-31]",
        extra='NOT show_title:"The X-Files" AND NOT show_title:"Millennium" '
              'AND NOT show_title:"Beyond Belief: Fact or Fiction"'
    ),
    "modern_horror_tv": show_source(genre="horror", era=TV_HD),
    "thriller_tv": show_source(genre="thriller"),
    # Was genre:"(supernatural OR tag:paranormal)". There is no Supernatural
    # genre in this library and tag:paranormal is on 3 shows, so the key was
    # near-empty while holding a third of a daily block. tag:supernatural is the
    # tag that actually exists (12 shows).
    "supernatural_tv": show_source(tags="(tag:supernatural OR tag:paranormal)"),
    
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
    # Comedy and drama take the full broadcaster list. `british_mystery_tv`
    # deliberately does not: Mystery Theatre runs it as its 17:00-20:00 evening
    # strip, and the only title widening would add is Black Mirror, which is
    # tagged Mystery but is not one in any sense that block means (G11).
    "british_comedy_tv": show_source(genre="comedy", studio=BRITISH_BROADCASTERS, tags="(tag:sitcom OR genre:comedy)"),
    "british_mystery_tv": show_source(genre="mystery", studio="(bbc OR itv)"),
    "british_drama_tv": show_source(genre="drama", studio=BRITISH_BROADCASTERS),
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

    # Registered 2026-09-01 for the Good Times rebuild. Every one was on disk
    # and reachable by no channel: the sitcom shelf the channel actually has is
    # roughly twice the size of the roster it was scheduling. Frasier alone is
    # 273 episodes, which is more than any single show the channel already ran.
    #
    # `golden_girls_tv` and `night_court_tv` are renames, not new keys -- they
    # were `eighties_sitcom_golden_girls` and `eighties_sitcom_night_court`,
    # Totally 80s-specific names for two shows that are now on two channels.
    # Same cleanup `eighties_sitcom_cheers` -> `cheers_tv` got: a pool under a
    # channel-specific name reads to the collision report as that channel's
    # private pool, and stops reading as shared the moment it is shared.
    "frasier_tv": show_by_title("frasier"),
    "golden_girls_tv": show_by_title("the golden girls"),
    "night_court_tv": show_by_title("night court"),
    "spin_city_tv": show_by_title("spin city"),
    "just_shoot_me_tv": show_by_title("just shoot me!"),
    "will_and_grace_tv": show_by_title("will & grace"),
    # G10 applied to a show rather than a film: `show_title:"martin"` is a
    # phrase match that also returns Doc Martin -- 83 episodes of Across the
    # Pond's lunch block, on this channel every time the key was drawn.
    "martin_tv": show_by_title("martin") + ' AND NOT show_title:"Doc Martin"',
    "sabrina_tv": show_by_title("sabrina, the teenage witch"),
    "northern_exposure_tv": show_by_title("northern exposure"),
    # "Addams Family The" is how the library stores it -- the folder is
    # `Addams Family The (1964)` -- so `show_title:"the addams family"` phrase
    # matches nothing. Caught by key_census on the day the key was added.
    "addams_family_tv": show_by_title("addams family the"),
    "smothers_brothers_tv": show_by_title("the smothers brothers comedy hour"),
    "soap_tv": show_by_title("soap"),
    "mork_mindy_tv": show_by_title("mork & mindy"),
    "jeannie_tv": show_by_title("i dream of jeannie"),

    # Registered 2026-09-01. All five were on disk and in no channel's reach --
    # `key_census` only scores keys that exist, so a show with no key at all is
    # invisible to it. Found by diffing `reference/library-tv.tsv` against every
    # title named anywhere in `library/`, which is the check nothing was doing.
    # Together they are ~700 episodes of exactly the decade Totally 80s is short
    # of, and none of them is claimed by another channel.
    "murphy_brown_tv": show_by_title("murphy brown"),
    "roseanne_tv": show_by_title("roseanne"),
    "kids_in_the_hall_tv": show_by_title("the kids in the hall"),
    "police_squad_tv": show_by_title("police squad!"),
    "pee_wee_playhouse_tv": show_by_title("pee-wee's playhouse"),
    "in_living_color_tv": show_by_title("in living color"),
    "the_office_tv": show_by_title("the office"),
    "parks_and_recreation_tv": show_by_title("parks and recreation"),
    "30_rock_tv": show_by_title("30 rock"),
    "community_tv": show_by_title("community"),

    # --- CORNCOB TV -- comedy after the laugh track (registered 2026-09-01) ---
    #
    # Single-camera network, cable, streaming, sketch and alt. The line against
    # Good Times is the studio audience, not the year: Freaks and Geeks (1999),
    # The Larry Sanders Show (1992) and Mr. Show (1995) are single-camera with
    # no laugh track and belong here, while Frasier (1993) and Will & Grace
    # (1998) are multi-camera and stay there.
    #
    # `scrubs_tv` and `frasier_tv` between them are 516 episodes that no channel
    # could reach before this pass -- neither had a key.

    # The daytime spine: single-camera network sitcom.
    "scrubs_tv": show_by_title("scrubs"),
    "malcolm_tv": show_by_title("malcolm in the middle"),
    "my_name_is_earl_tv": show_by_title("my name is earl"),
    "arrested_development_tv": show_by_title("arrested development"),
    "superstore_tv": show_by_title("superstore"),
    "good_place_tv": show_by_title("the good place"),
    "abbott_elementary_tv": show_by_title("abbott elementary"),
    "schitts_creek_tv": show_by_title("schitt's creek"),
    "kimmy_schmidt_tv": show_by_title("unbreakable kimmy schmidt"),
    "better_off_ted_tv": show_by_title("better off ted"),
    "ghosted_tv": show_by_title("ghosted"),
    "freaks_and_geeks_tv": show_by_title("freaks and geeks"),
    "mythic_quest_tv": show_by_title("mythic quest"),

    # Adult animation. All three were on disk and named nowhere in `library/`
    # or `channels/` -- invisible to `key_census`, which can only score keys
    # that exist. South Park is 305 episodes, the largest single unscheduled
    # show in the library and roughly twice the next Corncob title.
    "south_park_tv": show_by_title("south park"),
    "bojack_horseman_tv": show_by_title("bojack horseman"),
    "f_is_for_family_tv": show_by_title("f is for family"),

    # The episodic procedural bench. All four were on disk and named nowhere,
    # and channel-coverage.md assigned three of them to this channel on
    # 2026-08-29 without anything wiring them. The Shield is 336 episodes --
    # the second-largest unscheduled show in the library.
    "the_shield_tv": show_by_title("the shield"),
    "nine_one_one_tv": show_by_title("9-1-1"),
    "greys_anatomy_tv": show_by_title("grey's anatomy"),
    "chicago_med_tv": show_by_title("chicago med"),

    # Cable half-hours.
    "always_sunny_tv": show_by_title("it's always sunny in philadelphia"),
    "curb_tv": show_by_title("curb your enthusiasm"),
    "veep_tv": show_by_title("veep"),
    "workaholics_tv": show_by_title("workaholics"),
    "portlandia_tv": show_by_title("portlandia"),
    "silicon_valley_tv": show_by_title("silicon valley"),
    "reno_911_tv": show_by_title("reno 911!"),
    "trailer_park_boys_tv": show_by_title("trailer park boys"),
    "wilfred_tv": show_by_title("wilfred (us)"),
    "baskets_tv": show_by_title("baskets"),
    "atlanta_tv": show_by_title("atlanta"),
    "man_seeking_woman_tv": show_by_title("man seeking woman"),
    "jim_gaffigan_tv": show_by_title("the jim gaffigan show"),
    "red_green_tv": show_by_title("the red green show"),
    "penn_teller_tv": show_by_title("penn & teller: bull!"),
    "mr_inbetween_tv": show_by_title("mr inbetween"),
    "reservation_dogs_tv": show_by_title("reservation dogs"),
    "future_man_tv": show_by_title("future man"),

    # Sketch and alt.
    "mr_show_tv": show_by_title("mr. show"),
    "the_state_tv": show_by_title("the state"),
    "strangers_with_candy_tv": show_by_title("strangers with candy"),
    "key_and_peele_tv": show_by_title("key & peele"),
    "chappelles_show_tv": show_by_title("chappelle's show"),
    "tim_and_eric_tv": show_by_title("tim and eric awesome show, great job!"),
    "itysl_tv": show_by_title("i think you should leave with tim robinson"),
    "nathan_for_you_tv": show_by_title("nathan for you"),
    "detroiters_tv": show_by_title("detroiters"),
    "insomniac_tv": show_by_title("insomniac with dave attell"),
    "food_party_tv": show_by_title("food party"),
    "the_guild_tv": show_by_title("the guild"),
    "john_wilson_tv": show_by_title("how to with john wilson"),
    "larry_sanders_tv": show_by_title("the larry sanders show"),
    "conchords_tv": show_by_title("flight of the conchords"),

    # The Limited Series bench -- short and often serialized, which is what the
    # slot is for (G6). None of these can strip; each is a season of Sundays.
    "party_down_tv": playback_order(show_by_title("party down"), force="Chronological"),
    "enlightened_tv": playback_order(show_by_title("enlightened"), force="Chronological"),
    "vice_principals_tv": playback_order(show_by_title("vice principals"), force="Chronological"),
    "eastbound_tv": show_by_title("eastbound & down"),
    "wet_hot_tv": playback_order(show_by_title("wet hot american summer"), force="Chronological"),
    "the_rehearsal_tv": show_by_title("the rehearsal"),
    "the_curse_tv": show_by_title("the curse"),
    "jury_duty_tv": show_by_title("jury duty"),
    "the_studio_tv": show_by_title("the studio"),
    "chair_company_tv": show_by_title("the chair company"),
    "north_of_north_tv": show_by_title("north of north"),
    "bad_thoughts_tv": show_by_title("bad thoughts"),
    "history_world_2_tv": show_by_title("history of the world: part ii"),
    "other_space_tv": show_by_title("other space"),
    "people_of_earth_tv": show_by_title("people of earth"),

    # Shared with Cartoon Network's Adult Swim, which airs them 20:00-23:00
    # Tue/Thu, 23:00-24:00 Sunday and 00:00-02:00 Monday. Corncob runs them as
    # syndication in daylight, the split channel-coverage.md prescribes.
    "eric_andre_tv": show_by_title("the eric andre show"),
    "steve_brule_tv": show_by_title("check it out! with dr. steve brule"),

    # --- 80s CHANNEL SPECIFIC ---
    #
    # Three keys that used to live here were byte-identical to a general key
    # under a second name -- `eighties_sitcom_cheers` = `cheers_tv`,
    # `eighties_sitcom_full_house` = `full_house_tv`,
    # `eighties_action_knight_rider` = `knight_rider_tv`. That is not a
    # cosmetic duplication: section 1 of the collision report groups airings by
    # *key name*, so one pool under two names reads as two pools and the
    # channels sharing it never appear as sharing anything. Totally 80s and
    # Good Times have both been airing Cheers and Full House for as long as
    # both channels have existed and the report has never said so. The channel
    # now references the general keys, and the duplicates are gone.
    "eighties_cartoons_heman": show_by_title("He-Man and the Masters of the Universe"),
    "eighties_cartoons_transformers": show_by_title("The Transformers"),
    "eighties_cartoons_smurfs": show_by_title("The Smurfs"),
    "eighties_cartoons_thundercats": show_by_title("ThunderCats"),
    "eighties_action_tv": show_source(genre="action", era=EIGHTIES),
    "eighties_drama_tv": show_source(genre="drama", era=EIGHTIES),
    "eighties_daytime_movie": movie_source(era=EIGHTIES, extra=NO_HORROR),
    "eighties_crime_tv": show_source(genre="crime", era=EIGHTIES),
    "eighties_suspense_movie": movie_source(genre="thriller", era=EIGHTIES),
    "eighties_action_a_team": show_by_title("The A-Team"),
    "eighties_crime_miami_vice": show_by_title("Miami Vice"),
    "eighties_crime_magnum_pi": show_by_title("Magnum, P.I."),
    "eighties_scifi_quantum_leap": show_by_title("Quantum Leap"),
    "eighties_blockbuster_movie": movie_source(era=EIGHTIES, tags="tag:blockbuster"),
    "movie_intro_bumper": 'type:"other_video" AND tag:intro AND tag:movie',
    "eighties_scifi_star_trek": show_by_title("Star Trek: The Next Generation"),
    "eighties_drama_movie": movie_source(genre="drama", era=EIGHTIES),
    # 1975, not 1980. The music video library was reorganised 2026-09-02 and is
    # now dated -- every file carries a Kodi .nfo with a real <year> -- but the
    # decade alone yields 31 videos, about two hours. Opening the window to the
    # late 1970s adds Boston, the Carpenters, Pink Floyd and "Don't Stop 'Til
    # You Get Enough" for 35 videos and 152 minutes.
    #
    # !! THIS KEY SELECTS NOTHING ON THE SERVER. Verified 2026-09-07 against a
    # freshly reset playout: Totally 80s airs zero music videos, while The Beat
    # airs all 302 of them and 35 do fall in this window. The pool is real and
    # dated; the query does not reach it. Either Lucene does not index `year`
    # for music videos, or `music_video` is the wrong type token -- and there is
    # no read API to ask. Do not trust this key until a build proves it.
    # See KNOWN_ISSUES, 2026-09-07.
    "eighties_music_videos": 'type:"music_video" AND year:[1975 TO 1989]',
    # NO_HORROR, matching `eighties_daytime_movie` above, which has carried the
    # exclusion since before there was a horror channel to justify it. Without
    # it this key is the whole 1980s and contains `eighties_horror_movie`
    # outright -- Totally 80s' weekend film against Nightmare Theatre's name
    # block, drawing the same 67 films at the same hour. Caught by section 3 of
    # the collision report.
    "eighties_weekend_movie": movie_source(era=EIGHTIES, extra=NO_HORROR),
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
# 3c. JAPANORAMA
# ============================================================================
#
# Channel 164. Two halves, and the split between them is the point.
#
# The `_syndication_tv` keys are shows Cartoon Network's Toonami also runs.
# They carry Shuffle where Toonami's carry Chronological, which is the C2
# rung-1 split: Toonami runs them as a first-run strip after school, Japanorama
# runs them as daytime syndication you can drop into. The hours rule that keeps
# the two apart is written out in the docstring of `library/anime.py`; forcing
# Shuffle here is what makes the two presentations impossible to confuse at the
# key level rather than by a grid remembering (C3).
#
# Everything else on this channel is Japanorama's alone.

JAPANORAMA_REGISTRY = {
    # --- THE MORNING: iyashikei -------------------------------------------
    "laid_back_camp_tv": show_by_title("Laid-Back Camp"),
    "campfire_cooking_tv": show_by_title(
        "Campfire Cooking in Another World with My Absurd Skill"),
    "okitsura_tv": show_by_title(
        "OKITSURA: Fell in Love with an Okinawan Girl, but I Just Wish I Know What She's Saying"),
    # Encouragement of Climb is three shows by running time and has to be cut
    # into them (G2). Season 1 is twelve 3.5-minute shorts, seasons 2-3 run
    # 13.5 minutes, season 4 is a full 24. Handing all 61 episodes to one strip
    # drops a three-minute short into a half-hour hole.
    "yama_no_susume_tv":
        'type:episode AND show_title:"Encouragement of Climb" AND season_number:[2 TO 4]',

    # --- THE FILLER: the 3.5-minute shelf ---------------------------------
    # Twenty-four shorts, none over four minutes. Cartoon Network ships with no
    # daytime filler at all because its bumper trees are empty and G12 says
    # silence beats the wrong branding. This channel has real programming that
    # fits the same hole, so it pads with that instead of with nothing.
    "japanorama_shorts_tv":
        'type:episode AND ('
        '(show_title:"Encouragement of Climb" AND season_number:1)'
        ' OR show_title:"Room Camp")',

    # --- TEATIME ----------------------------------------------------------
    "assassination_classroom_tv": show_by_title("Assassination Classroom"),
    "ranking_of_kings_tv": show_by_title("Ranking of Kings"),
    "girls_und_panzer_tv": show_by_title("Girls und Panzer"),
    "one_punch_man_tv": show_by_title("One-Punch Man"),
    "dandadan_tv": show_by_title("DAN DA DAN"),

    # --- PRIME: the strip -------------------------------------------------
    # Two keys per show, not one key played two ways: an ErsatzTV content key
    # carries its playback order, so chronological on weeknights and shuffled
    # on Sunday is two registrations (G8).
    "frieren_chronological_tv": playback_order(
        show_by_title("Frieren: Beyond Journey's End"), force="Chronological"),
    "frieren_tv": playback_order(
        show_by_title("Frieren: Beyond Journey's End"), force="Shuffle"),
    "vinland_saga_chronological_tv": playback_order(
        show_by_title("Vinland Saga"), force="Chronological"),
    "vinland_saga_tv": playback_order(
        show_by_title("Vinland Saga"), force="Shuffle"),
    "carole_and_tuesday_tv": playback_order(
        show_by_title("Carole & Tuesday"), force="Chronological"),
    "kids_on_the_slope_tv": playback_order(
        show_by_title("Kids on the Slope"), force="Chronological"),
    "violet_evergarden_tv": show_by_title("Violet Evergarden"),
    "kinos_journey_tv": show_by_title("Kino's Journey"),
    "fullmetal_alchemist_brotherhood_tv": playback_order(
        show_by_title("Fullmetal Alchemist: Brotherhood"), force="Shuffle"),
    "death_note_tv": playback_order(show_by_title("Death Note"), force="Shuffle"),

    # --- THE SATURDAY EVENTS ----------------------------------------------
    # Four runs too short to strip, one to a season of the year (G6).
    "blue_eye_samurai_tv": playback_order(
        show_by_title("Blue Eye Samurai"), force="Chronological"),
    "macross_plus_tv": playback_order(
        show_by_title("Macross Plus"), force="Chronological"),
    "tatami_time_machine_blues_tv": playback_order(
        show_by_title("The Tatami Time Machine Blues"), force="Chronological"),
    "scott_pilgrim_takes_off_tv": playback_order(
        show_by_title("Scott Pilgrim Takes Off"), force="Chronological"),

    # --- DEEP NIGHT -------------------------------------------------------
    "tatami_galaxy_tv": show_by_title("The Tatami Galaxy"),
    "terror_in_resonance_tv": playback_order(
        show_by_title("Terror in Resonance"), force="Chronological"),
    "cyberpunk_edgerunners_tv": playback_order(
        show_by_title("Cyberpunk: Edgerunners"), force="Chronological"),
    # Deliberately unbounded: the phrase matches Midnight Diner (2009) and
    # Midnight Diner: Tokyo Stories (2016) both, which is 40 episodes of one
    # show under two titles. The only live-action series on the channel.
    "midnight_diner_tv": show_by_title("Midnight Diner"),

    # --- SHARED WITH TOONAMI: the syndication half ------------------------
    "pokemon_syndication_tv": playback_order(show_by_title("Pokémon"), force="Shuffle"),
    # `show_title:"Dragon Ball"` is a phrase match and returns Z, GT, Super and
    # DAIMA with it (G10). The kids' hour wants the 1986 show alone.
    "dragon_ball_syndication_tv": playback_order(
        'type:episode AND show_title:"Dragon Ball"'
        ' AND NOT show_title:"Dragon Ball Z" AND NOT show_title:"Dragon Ball GT"'
        ' AND NOT show_title:"Dragon Ball Super" AND NOT show_title:"Dragon Ball DAIMA"',
        force="Shuffle"),
    # Same trap: Sailor Moon returns Sailor Moon Crystal. animation.py carries
    # the identical exclusion for the identical reason.
    "sailor_moon_syndication_tv": playback_order(
        'type:episode AND show_title:"Sailor Moon" AND NOT show_title:"Sailor Moon Crystal"',
        force="Shuffle"),
    "sailor_moon_crystal_tv": playback_order(
        show_by_title("Sailor Moon Crystal"), force="Shuffle"),
    "one_piece_syndication_tv": playback_order(show_by_title("One Piece"), force="Shuffle"),
    "naruto_syndication_tv": playback_order(show_by_title("Naruto"), force="Shuffle"),
    "inuyasha_syndication_tv": playback_order(show_by_title("InuYasha"), force="Shuffle"),
    "rurouni_kenshin_syndication_tv": playback_order(
        show_by_title("Rurouni Kenshin"), force="Shuffle"),
    "dragon_ball_z_syndication_tv": playback_order(
        show_by_title("Dragon Ball Z"), force="Shuffle"),
    "dragon_ball_gt_tv": playback_order(show_by_title("Dragon Ball GT"), force="Shuffle"),
    "dragon_ball_super_syndication_tv": playback_order(
        show_by_title("Dragon Ball Super"), force="Shuffle"),
    "yu_yu_hakusho_syndication_tv": playback_order(
        show_by_title("Yu Yu Hakusho"), force="Shuffle"),

    # --- THE FALLBACK BED -------------------------------------------------
    # Everything on the channel that no other channel names, as one key. A
    # fallback has to be a key and not a Block -- `resolve_fallback_key()`
    # resolves keys and collections and warns on anything else -- and it has to
    # be drawn from the owned half: a stall can fire at any hour, so a bed built
    # from the syndication keys would be the one thing on the channel that can
    # reach Toonami's window and break the hours rule. Same reason Nick and
    # Disney carry `nicktoons_vault_tv` and `disney_vault_tv`.
    "japanorama_vault_tv": playback_order(
        'type:episode AND ('
        'show_title:"Laid-Back Camp" OR show_title:"Encouragement of Climb"'
        ' OR show_title:"Campfire Cooking in Another World with My Absurd Skill"'
        ' OR show_title:"Assassination Classroom" OR show_title:"Ranking of Kings"'
        ' OR show_title:"Girls und Panzer" OR show_title:"One-Punch Man"'
        ' OR show_title:"DAN DA DAN" OR show_title:"Frieren: Beyond Journey\'s End"'
        ' OR show_title:"Vinland Saga" OR show_title:"Violet Evergarden"'
        ' OR show_title:"Kino\'s Journey" OR show_title:"Carole & Tuesday"'
        ' OR show_title:"The Tatami Galaxy" OR show_title:"Midnight Diner"'
        ' OR show_title:"Dragon Ball GT")',
        force="Shuffle"),

    # --- FILM -------------------------------------------------------------
    # Named title by title rather than by studio or genre, because neither tag
    # can carry this shelf. `genre:anime` is on two films in the whole library,
    # and `library-movies.tsv` has no studio column -- so a
    # `studio:"Studio Ghibli"` key resolves to "not in manifests" in key_census
    # and cannot be checked offline at all (V3). That is what the old
    # `ghibli_movie` key was, and it is why this one is a title list.
    #
    # Every title is in the manifest's own form. `movie_by_title` builds a
    # phrase match against the indexed title and the library stores articles
    # inverted -- "Cat Returns, The", not "The Cat Returns" -- which is the trap
    # library/british.py records against `title:"The World's End"`, a query that
    # matched nothing for as long as it was there.
    #
    # Every shelf is closed with `genre:animation`, and that is load-bearing
    # rather than decorative. `title:"Metropolis"` is a phrase match that
    # returns Fritz Lang's 1927 silent as well as Rintaro's 2001 film -- the
    # oldest picture on Cabes Classic Cinema, on an anime channel at midnight --
    # and `title:"Your Name"` returns Call Me by Your Name. Both wrong films are
    # live action and every right one is animated, so one clause closes both
    # holes where a year bound would have had to be written per title.
    #
    # It has to be `animation OR anime`, not either alone. The library uses the
    # two tags inconsistently on exactly the films that most need catching:
    # The Transformers: The Movie and Laid-Back Camp the Movie carry `Anime`
    # and no `Animation`, while Your Name and all 23 Ghibli films carry
    # `Animation` and no `Anime`. Only two films in the library have the anime
    # tag at all, which is the same reason `anime_movie` cannot carry a shelf.
    "ghibli_movie": playback_order(
        'type:movie AND ('
        'title:"Nausicaä of the Valley of the Wind" OR title:"Castle in the Sky"'
        ' OR title:"Grave of the Fireflies" OR title:"My Neighbor Totoro"'
        ' OR title:"Kiki\'s Delivery Service" OR title:"Only Yesterday"'
        ' OR title:"Porco Rosso" OR title:"Ocean Waves" OR title:"Pom Poko"'
        ' OR title:"Whisper of the Heart" OR title:"Princess Mononoke"'
        ' OR title:"My Neighbors the Yamadas" OR title:"Spirited Away"'
        ' OR title:"Cat Returns, The" OR title:"Howl\'s Moving Castle"'
        ' OR title:"Tales from Earthsea" OR title:"Ponyo"'
        ' OR title:"Secret World of Arrietty, The" OR title:"From Up on Poppy Hill"'
        ' OR title:"Wind Rises, The" OR title:"Tale of The Princess Kaguya, The"'
        ' OR title:"When Marnie Was There" OR title:"Boy and the Heron, The")'
        f' AND ({ANIMATED} OR {ANIME})',
        force="Shuffle"),

    # The canon, and the two films Cartoon Network also plays. Akira and Ghost
    # in the Shell air on its Midnight Run at 23:00-02:00 with Toonami bumper
    # sets on them; this key is scheduled at 19:00-21:00 and nowhere else, which
    # is the whole of the hours rule for film.
    "anime_canon_movie": playback_order(
        'type:movie AND (title:"Akira" OR title:"Ghost in the Shell"'
        ' OR title:"Dirty Pair - Project Eden" OR title:"Transformers - The Movie, The")'
        f' AND ({ANIMATED} OR {ANIME})',
        force="Shuffle"),

    # The late shelf. Angel's Egg, Perfect Blue and Paprika are the reason this
    # channel has a 23:00 at all.
    "anime_arthouse_movie": playback_order(
        'type:movie AND (title:"Angel\'s Egg" OR title:"Perfect Blue"'
        ' OR title:"Metropolis" OR title:"Tokyo Godfathers" OR title:"Paprika"'
        ' OR title:"Miss Hokusai" OR title:"Blade Runner - Black Out 2022")'
        f' AND ({ANIMATED} OR {ANIME})',
        force="Shuffle"),

    # `title:"Evangelion"` is a phrase match on a single token, so it returns
    # all four Rebuild features once type:movie has removed the 1995 series.
    # Chronological because 1.0 through 3.0+1.0 is one film in four parts.
    "evangelion_movie": playback_order(
        'type:movie AND title:"Evangelion"', force="Chronological"),

    # Battle of Gods, Broly and Super Hero -- same phrase behaviour, bounded to
    # film so the 1,100 television episodes stay out.
    "dragon_ball_movie": playback_order('type:movie AND title:"Dragon Ball"', force="Shuffle"),

    "anime_modern_movie": playback_order(
        'type:movie AND (title:"Your Name" OR title:"Laid-Back Camp the Movie")'
        f' AND ({ANIMATED} OR {ANIME})',
        force="Shuffle"),
}

# ============================================================================
# 3b. NICKELODEON
# ============================================================================

NICK_REGISTRY = {
    # The Avatar strip runs chronologically on weekdays and shuffled at the
    # weekend. An ErsatzTV content key carries its playback order, so that is
    # two keys per show, not one key played two ways.
    "avatar_chronological_tv": playback_order(
        show_by_title("Avatar: The Last Airbender"), force="Chronological"),
    "avatar_shuffle_tv": playback_order(
        show_by_title("Avatar: The Last Airbender"), force="Shuffle"),
    "korra_chronological_tv": playback_order(
        show_by_title("The Legend of Korra"), force="Chronological"),
    "korra_shuffle_tv": playback_order(
        show_by_title("The Legend of Korra"), force="Shuffle"),

    # Three-minute shorts -- the natural pad between programmes on a kids
    # channel, and the only filler Nick has assets for.
    "schoolhouse_rock_tv": show_by_title("Schoolhouse Rock!"),

    # The channel's emergency bed, same contract as `disney_vault_tv`: a
    # content key, because `fallback_content` cannot be a Block. Nicktoons
    # only -- the Nick at Nite titles are shared with Good Times, and a
    # fallback firing at an arbitrary hour must not reach into them.
    "nicktoons_vault_tv": playback_order(
        'type:episode AND show_genre:animation AND ('
        'show_title:"The Ren & Stimpy Show" OR show_title:"Rocko\'s Modern Life"'
        ' OR show_title:"Aaahh!!! Real Monsters" OR show_title:"The Wild Thornberrys"'
        ' OR show_title:"SpongeBob SquarePants" OR show_title:"Invader ZIM"'
        ' OR show_title:"Daria")',
        force="Shuffle"),
}

# ============================================================================
# 3c. DISNEY
# ============================================================================

DISNEY_REGISTRY = {
    # --- THE SERIALIZED STRIPS ---
    # Star Wars and the modern Disney Channel shows are the only serialized
    # content on the channel, so they carry the chronological-weekday /
    # shuffle-weekend split. As on Nick, that is two content keys per show --
    # an ErsatzTV key carries its playback order, and one key would be pinned
    # to whichever order registered first in the build.
    "clone_wars_chronological_tv": playback_order(
        show_by_title("Star Wars The Clone Wars"), force="Chronological"),
    "clone_wars_shuffle_tv": playback_order(
        show_by_title("Star Wars The Clone Wars"), force="Shuffle"),
    "rebels_chronological_tv": playback_order(
        show_by_title("Star Wars Rebels"), force="Chronological"),
    "rebels_shuffle_tv": playback_order(
        show_by_title("Star Wars Rebels"), force="Shuffle"),
    "bad_batch_chronological_tv": playback_order(
        show_by_title("Star Wars The Bad Batch"), force="Chronological"),
    "bad_batch_shuffle_tv": playback_order(
        show_by_title("Star Wars The Bad Batch"), force="Shuffle"),

    "gravity_falls_chronological_tv": playback_order(
        show_by_title("Gravity Falls"), force="Chronological"),
    "gravity_falls_shuffle_tv": playback_order(
        show_by_title("Gravity Falls"), force="Shuffle"),
    "owl_house_chronological_tv": playback_order(
        show_by_title("The Owl House"), force="Chronological"),
    "owl_house_shuffle_tv": playback_order(
        show_by_title("The Owl House"), force="Shuffle"),
    "amphibia_chronological_tv": playback_order(
        show_by_title("Amphibia"), force="Chronological"),
    "amphibia_shuffle_tv": playback_order(
        show_by_title("Amphibia"), force="Shuffle"),

    # Everything animated with Star Wars on the front. The rerun bed the four
    # Saturday-night events fall back on for the ~30 weeks a year none of them
    # is in season, and the collection the May 4th marathon draws from.
    "star_wars_animation_tv": playback_order(
        f'{show_by_title("Star Wars")} AND show_genre:animation',
        force="Shuffle"),

    # The channel's emergency bed. `fallback_content` is handed to the circuit
    # breaker and must be a content key -- a Block is stringified into a key
    # that matches nothing (see engines/dispatcher.py::resolve_fallback_key).
    # Genre-qualified once for the whole OR, which also settles Hercules.
    "disney_vault_tv": playback_order(
        'type:episode AND show_genre:animation AND ('
        'show_title:"DuckTales" OR show_title:"Darkwing Duck"'
        ' OR show_title:"Chip \'n\' Dale Rescue Rangers" OR show_title:"TaleSpin"'
        ' OR show_title:"Gargoyles" OR show_title:"Goof Troop"'
        ' OR show_title:"Aladdin" OR show_title:"Hercules"'
        ' OR show_title:"Pepper Ann" OR show_title:"Kim Possible"'
        ' OR show_title:"Buzz Lightyear of Star Command"'
        ' OR show_title:"Mighty Ducks: The Animated Series")',
        force="Shuffle"),

    # --- DISAMBIGUATION ---
    # "Hercules" alone matches the 1998 Disney cartoon *and* Hercules: The
    # Legendary Journeys, which is live action and belongs to Other Worlds.
    # The genre is what separates them.
    "hercules_animated_tv":
        f'{show_by_title("Hercules")} AND show_genre:animation',
}

# ============================================================================
# 3d. CARTOON NETWORK
# ============================================================================

# Four disambiguations. Every one of them is a title that resolves to two shows
# now that the restructure airs both halves of the pair on the same channel.
CARTOON_NETWORK_REGISTRY = {
    # The 1941 Fleischer shorts (17, nine minutes each) open the Saturday
    # morning vault. Superman: The Animated Series is a different show and airs
    # in Action Hour the same afternoon; a bare title matches both.
    "superman_fleischer_tv": playback_order(
        f'{show_by_title("Superman")} AND release_date:[1941-01-01 TO 1945-12-31]',
        force="Chronological"),

    # X-Men (1992). A bare title also matches X-Men '97, which is 2024 and
    # Disney's.
    "xmen_animated_tv":
        f'{show_by_title("X-Men")} AND release_date:[1992-01-01 TO 1997-12-31]',

    # Attack on Titan proper. The phrase is also a prefix of Attack on Titan
    # Junior High, which is the Friday appointment this is the rerun bed for.
    "attack_on_titan_tv":
        f'{show_by_title("Attack on Titan")} AND NOT show_title:"Junior High"',

    # The rerun bed behind the Dragon Ball DAIMA appointment on Toonami
    # Saturday, for the 32 weeks a year DAIMA is not in season.
    "dragon_ball_super_tv": show_by_title("Dragon Ball Super"),

    # The rerun bed behind the six weekday Toonami strips. Each is an
    # `annual_show()` in Contiguous Mode, and a contiguous strip has dead
    # stretches -- before its anchor date, and between the end of a run and the
    # start of the next loop. Without a rerun bed the Program resolves to
    # nothing, the block skips it, and a whole item slot stalls into the
    # circuit breaker. This is what plays instead.
    "toonami_vault_tv": playback_order(
        'type:episode AND (show_title:"Dragon Ball Z" OR show_title:"Naruto"'
        ' OR show_title:"InuYasha" OR show_title:"Yu Yu Hakusho"'
        ' OR show_title:"Rurouni Kenshin" OR show_title:"Sailor Moon"'
        # 82 episodes on disk, named nowhere. Toonami's anime bench was four
        # shows behind six appointment strips; this is the fifth.
        ' OR show_title:"Pokémon")',
        force="Shuffle"),
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
    # Excludes every gate a kids or daytime block must not draw from. This is
    # the key such a block should use.
    #
    # `tobacco` was added with the 1950s US set: six of those 37 spots are
    # cigarette ads, and one of them -- a Flintstones cartoon that turns out to
    # be a Winston commercial -- is identifiable only from its closing frame.
    # Before the gate existed this query returned it as family-safe.
    #
    # `uncategorized` is everything whose category is not clear, which is most
    # of the US set. A gate is a positive determination, never the residue left
    # after some keywords failed to match -- a filename says almost nothing
    # about what is in a commercial. Broadcast ad breaks live here too, since
    # they carry whatever the network aired that night. Channels that want the
    # whole reel ask for it by name.
    "commercials_family_safe_spot":
        'type:"other_video" AND tag_full:"commercials"'
        ' AND NOT tag_full:"alcohol" AND NOT tag_full:"tobacco"'
        ' AND NOT tag_full:"uncategorized"',

    # audience gate
    "commercials_kids_spot": filler_source("commercials", "kids"),
    "commercials_alcohol_spot": filler_source("commercials", "alcohol"),
    "commercials_tobacco_spot": filler_source("commercials", "tobacco"),
    "commercials_christmas_spot": filler_source("commercials", "christmas"),
    "commercials_general_spot": filler_source("commercials", "general"),
    "commercials_uncategorized_spot": filler_source("commercials", "uncategorized"),

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
    # Across the Pond runs the UK reel channel-wide, but its Saturday-morning
    # block is Wallace & Gromit and Mr. Bean, so that one block overrides to the
    # family-safe cut -- 11 of the 116 UK spots are beer and spirits.
    "commercials_uk_family_safe_spot":
        'type:"other_video" AND tag_full:"commercials" AND tag_full:"uk"'
        ' AND NOT tag_full:"alcohol" AND NOT tag_full:"tobacco"'
        ' AND NOT tag_full:"uncategorized"',
    "commercials_uk_kids_spot": filler_source("commercials", "uk", "kids"),
    "commercials_uk_90s_kids_spot": filler_source("commercials", "uk", "90s", "kids"),
    "commercials_uk_90s_general_spot": filler_source("commercials", "uk", "90s", "general"),
    "commercials_uk_90s_alcohol_spot": filler_source("commercials", "uk", "90s", "alcohol"),

    # US, added 2026-09-05 with 208 spots from archive.org. The 50s decade is
    # the public-domain set, dated from frames rather than metadata; the rest
    # are year-prefixed at source. Anything over seven minutes was left out of
    # the tree entirely -- see filler-taxonomy.md.
    "commercials_us_family_safe_spot":
        'type:"other_video" AND tag_full:"commercials" AND tag_full:"us"'
        ' AND NOT tag_full:"alcohol" AND NOT tag_full:"tobacco"'
        ' AND NOT tag_full:"uncategorized"',
    "commercials_us_kids_spot": filler_source("commercials", "us", "kids"),
    "commercials_us_general_spot": filler_source("commercials", "us", "general"),
    "commercials_us_tobacco_spot": filler_source("commercials", "us", "tobacco"),
    "commercials_us_uncategorized_spot": filler_source("commercials", "us", "uncategorized"),
    # Decade lists differ per gate because they track what is actually on disk:
    # no decade after the eighties has a spot whose product is clear enough for
    # `general`, and the 2010s hold two uncategorized files and nothing else.
    **{f"commercials_us_{d}_spot": filler_source("commercials", "us", d)
       for d in ("50s", "60s", "70s", "80s", "90s", "00s", "10s")},
    **{f"commercials_us_{d}_general_spot":
       filler_source("commercials", "us", d, "general")
       for d in ("50s", "60s", "70s", "80s", "90s")},
    **{f"commercials_us_{d}_kids_spot":
       filler_source("commercials", "us", d, "kids")
       for d in ("50s", "60s", "70s", "80s", "90s", "00s")},
    **{f"commercials_us_{d}_uncategorized_spot":
       filler_source("commercials", "us", d, "uncategorized")
       for d in ("50s", "60s", "70s", "80s", "90s", "00s", "10s")},

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
    **JAPANORAMA_REGISTRY,
    **NICK_REGISTRY,
    **DISNEY_REGISTRY,
    **CARTOON_NETWORK_REGISTRY,
    **THEME_REGISTRY,
    **MARATHONS,
    **SEASONAL_VARIANTS,
    **FILLERS,
    **TEST_REGISTRY
}
