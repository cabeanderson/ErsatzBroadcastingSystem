# scripts/library/builders.py
"""
Query builder functions and constants for the content library.
Shared by sources and marathons to prevent circular dependencies.
"""

from typing import Optional, Union, Dict
import re

# 1. CORE DEFINITIONS & GLOBAL FILTERS

MOVIE = "type:movie"
SHOW = "type:show"
EPISODE = "type:episode"
ANIMATED = "genre:animation"
ANIME = "genre:anime"
NOT_ANIMATED = "NOT genre:animation"

# Logic Filters
NO_SITCOM = "NOT tag:sitcom"
NO_FANTASY = "NOT genre:fantasy"
NO_SCIFI = 'NOT genre:"science fiction"'
NO_COMEDY = "NOT genre:comedy"
NO_BBC = "NOT studio:bbc"
SHORT = "minutes:[* TO 40]"

# 2. ERA DEFINITIONS

# --- MOVIE ERAS ---
SILENT_ERA = "release_date:[* TO 1929-12-31]"
GOLDEN_AGE = "release_date:[1930-01-01 TO 1949-12-31]"
CLASSIC_ERA = "release_date:[1950-01-01 TO 1969-12-31]"
SEVENTIES = "release_date:[1970-01-01 TO 1979-12-31]"
EIGHTIES = "release_date:[1980-01-01 TO 1989-12-31]"
NINETIES = "release_date:[1990-01-01 TO 1999-12-31]"
Y2K_ERA = "release_date:[2000-01-01 TO 2009-12-31]"
TENS = "release_date:[2010-01-01 TO 2019-12-31]"
TWENTIES = "release_date:[2020-01-01 TO 2029-12-31]"
STREAMING_ERA = "release_date:[2010-01-01 TO *]"

# --- TV ERAS ---
TV_VINTAGE = "release_date:[* TO 1975-12-31]"
TV_CLASSIC = "release_date:[1976-01-01 TO 1989-12-31]"
TV_GOLDEN_AGE = "release_date:[1985-01-01 TO 2009-12-31]"
TV_HD = "release_date:[2010-01-01 TO *]"

# --- SITCOM VIBES ---
SITCOM_80S_VIBE = "release_date:[1979-01-01 TO 1989-12-31]"
SITCOM_90S_VIBE = "release_date:[1988-01-01 TO 1999-12-31]"

# --- DECADE RANGES ---
SIXTIES = "release_date:[1960-01-01 TO 1969-12-31]"

# --- SEASONAL TAGS ---
WINTER_TAGS = "(tag:snow OR tag:ice OR tag:blizzard OR tag:cold OR tag:winter OR tag:mountain OR tag:arctic OR tag:alaska OR tag:antarctica OR tag:glacier OR tag:ski OR tag:cabin OR tag:fireplace OR tag:storm OR tag:isolation OR tag:survival OR tag:holiday OR tag:christmas OR tag:newyear)"
FALL_TAGS = "(tag:rain OR tag:fog OR tag:overcast OR tag:autumn OR tag:fall OR tag:leaves OR tag:harvest OR tag:small-town OR tag:noir OR tag:detective OR tag:mystery OR tag:thriller OR tag:psychological OR tag:gothic OR tag:halloween OR tag:witch OR tag:ghost OR tag:haunted OR tag:school OR tag:college OR tag:campus)"
SPRING_TAGS = "(tag:spring OR tag:flowers OR tag:bloom OR tag:garden OR tag:nature OR tag:hiking OR tag:exploration OR tag:travel OR tag:roadtrip OR tag:romance OR tag:dating OR tag:wedding OR tag:coming-of-age OR tag:youth OR tag:festival OR tag:fair OR tag:farm OR tag:countryside OR tag:animals)"
SUMMER_TAGS = "(tag:summer OR tag:beach OR tag:ocean OR tag:lake OR tag:island OR tag:vacation OR tag:resort OR tag:cruise OR tag:camp OR tag:camping OR tag:amusement-park OR tag:festival OR tag:concert OR tag:roadtrip OR tag:sports OR tag:surf OR tag:pool OR tag:heat OR tag:desert OR tag:jungle OR tag:tropical OR tag:teen OR tag:party)"

SEASONAL_TAG_QUERIES = {
    "WINTER": WINTER_TAGS, "FALL": FALL_TAGS, "SPRING": SPRING_TAGS, "SUMMER": SUMMER_TAGS
}

# DEFINE ORDER
SHUFFLE_MODE_ON = True

def playback_order(query, force=None):
    """Returns a dictionary containing the search query and the playback order."""
    if force:
        return {"query": query, "order": force}
    order_logic = "Shuffle" if SHUFFLE_MODE_ON else "Chronological"
    return {"query": query, "order": order_logic}

# 3. BUILDER FUNCTIONS

def _escape_quotes(text: str) -> str:
    """Escape double quotes in text for Lucene queries."""
    # Escape backslashes first to avoid double-escaping, then escape quotes
    return text.replace('\\', '\\\\').replace('"', '\\"')

def movie_source(
    genre: Optional[str] = None,
    era: Optional[str] = None,
    tags: Optional[str] = None,
    rating: Optional[str] = None,
    studio: Optional[str] = None,
    year: Optional[Union[str, int]] = None,
    extra: Optional[str] = None,
    exclude: Optional[str] = None,
    animated: bool = False
) -> str:
    """Build a movie search query."""
    anim_logic = ANIMATED if animated else NOT_ANIMATED
    parts = [MOVIE, anim_logic]
    
    if genre: parts.append(f"genre:{genre}")
    if era: parts.append(era)
    if tags: parts.append(tags)
    if rating: parts.append(rating)
    if studio: parts.append(f"studio:{studio}")
    if year: parts.append(f"year:{year}")
    if extra: parts.append(extra)
    if exclude: parts.append(f"NOT ({exclude})")
    
    return " AND ".join(parts)

def show_source(
    genre: Optional[str] = None,
    era: Optional[str] = None,
    tags: Optional[str] = None,
    rating: Optional[str] = None,
    studio: Optional[str] = None,
    year: Optional[Union[str, int]] = None,
    extra: Optional[str] = None,
    exclude: Optional[str] = None,
    animated: bool = False
) -> str:
    """Build a TV show search query (genre/studio-based)."""
    anim_logic = ANIMATED if animated else NOT_ANIMATED
    parts = [SHOW, anim_logic]

    if genre: parts.append(f"genre:{genre}")
    if era: parts.append(era)
    if tags: parts.append(tags)
    if rating: parts.append(rating)
    if studio: parts.append(f"studio:{studio}")
    if year: parts.append(f"year:{year}")
    if extra: parts.append(extra)
    if exclude: parts.append(f"NOT ({exclude})")

    return " AND ".join(parts)

def show_by_title(title: str) -> str:
    """Build a TV show search by exact title."""
    safe_title = _escape_quotes(title)
    return f'show_title:"{safe_title}"'

def collection_source(name: str) -> str:
    """Build a search query for a specific collection (Jellyfin/Plex/Emby)."""
    safe_name = _escape_quotes(name)
    return f'collection:"{safe_name}"'

def playlist_ref(name: str, group: str) -> Dict[str, str]:
    """Reference an existing ErsatzTV playlist."""
    return {"type": "playlist", "playlist": name, "group": group}

def episode_source(
    show_genre: Optional[str] = None,
    era: Optional[str] = None,
    tags: Optional[str] = None,
    extra: Optional[str] = None,
    exclude: Optional[str] = None,
    animated: bool = False
) -> str:
    """Build an episode search query for themed/holiday episodes."""
    if animated:
        genre_filter = "show_genre:animation"
    elif show_genre:
        genre_filter = f"show_genre:{show_genre} AND NOT show_genre:animation"
    else:
        genre_filter = "NOT show_genre:animation"

    parts = [EPISODE, genre_filter]

    if era: parts.append(era)
    if tags: parts.append(tags)
    if extra: parts.append(extra)
    if exclude: parts.append(f"NOT ({exclude})")

    return " AND ".join(parts)

def apply_tags(base_query: str, tag_query: str) -> str:
    """Helper to combine a base query string with a seasonal tag query string."""
    return f"({base_query}) AND {tag_query}"


def extract_episode_range(query):
    """
    Extracts start season and episode from a Lucene query.
    Example: '... season_number:1 AND episode_number:[21 TO 36]' -> (1, 21)
    """
    if not query:
        return None, None
        
    # Regex for season
    s_match = re.search(r'season_number:(\d+)', query)
    season = int(s_match.group(1)) if s_match else None
    
    # Regex for episode (range or single)
    e_match = re.search(r'episode_number:\[(\d+)', query)
    if not e_match:
            e_match = re.search(r'episode_number:(\d+)', query)
            
    episode = int(e_match.group(1)) if e_match else None
    
    return season, episode


def count_episodes_in_range(query):
    """
    Calculates total episodes in a range query.
    Example: '... episode_number:[21 TO 36]' -> 16
    """
    if not query:
        return 0
        
    match = re.search(r'episode_number:\[(\d+)\s+TO\s+(\d+)\]', query, re.IGNORECASE)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        return end - start + 1
        
    # Handle single episode
    if 'episode_number:' in query:
        return 1
        
    return 0