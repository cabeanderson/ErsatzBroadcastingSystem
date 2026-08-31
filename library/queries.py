# scripts/library/queries.py
"""
Query builder functions and constants for the content library.
Shared by sources and marathons to prevent circular dependencies.
"""

import re
import hashlib
from typing import Optional, Union, Dict, Tuple, Any
from scripts.settings import DEFAULT_ORDER

# Per-run cache of injected tag queries: (base_key, tag_query, suffix) -> (key, query, order).
# Reset at the start of each build via reset_injection_cache() so it never grows
# unbounded across many builds in one process (e.g. the simulator).
_INJECTION_CACHE = {}


def reset_injection_cache() -> None:
    """Clear the per-run tag-injection cache. Called by ScheduleRunner.run()."""
    _INJECTION_CACHE.clear()

# 1. CORE DEFINITIONS & GLOBAL FILTERS

MOVIE = "type:movie"
SHOW = "type:show"
EPISODE = "type:episode"
ANIMATED = "genre:animation"
ANIME = "genre:anime"
NOT_ANIMATED = "NOT genre:animation"

def playback_order(query, force=None):
    """Returns a dictionary containing the search query and the playback order."""
    if force:
        return {"query": query, "order": force}
    return {"query": query, "order": DEFAULT_ORDER}

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
    """Build a TV show search by exact title (returns Episodes)."""
    safe_title = _escape_quotes(title)
    return f'type:episode AND show_title:"{safe_title}"'

def show_container_by_title(title: str) -> str:
    """Build a TV show search by exact title (returns Show Container)."""
    safe_title = _escape_quotes(title)
    return f'type:show AND title:"{safe_title}"'

def movie_by_title(title: str) -> str:
    """Build a movie search by exact title."""
    safe_title = _escape_quotes(title)
    return f'type:movie AND title:"{safe_title}"'

def movie_by_title_year(title: str, year: Union[str, int]) -> str:
    """Title match bounded to a single release year.

    `movie_by_title` builds a phrase match, so `title:"Psycho"` also returns
    American Psycho and Seven Psychopaths, and `title:"Gladiator"` returns
    Gladiator II. Any spotlight or marathon that names a film with a common
    word in its title needs the year bound or it quietly becomes a different
    collection -- the trap `library/horror.py` documents against the Halloween
    and Friday the 13th runs, hit here again by the director spotlights.
    """
    return f'{movie_by_title(title)} AND release_date:[{year}-01-01 TO {year}-12-31]'

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

def inject_tag(
    base_key: str,
    tag_query: str,
    suffix: str,
    resolver: Any,
    logger: Any = None,
    order: str = "Shuffle"
) -> Optional[str]:
    """
    Generic helper to inject a tag query into an existing content key.
    Creates a new dynamic key, registers it, and returns it.
    
    Args:
        base_key: The original content key (must exist in registry).
        tag_query: The Lucene query part to append (e.g. 'tag:winter').
        suffix: Unique suffix for the new key (e.g. '_auto_winter').
        resolver: ContentResolver instance.
        logger: ChannelLogger instance (optional).
        order: Playback order for the new key (default: Shuffle).
    """
    cache_key = (base_key, tag_query, suffix)
    if cache_key in _INJECTION_CACHE:
        new_key, new_query, cached_order = _INJECTION_CACHE[cache_key]
        resolver.register_dynamic_query(new_key, new_query, cached_order)
        return new_key

    data = resolver.get_query_data(base_key)
    base_query = None
    
    if isinstance(data, dict):
        base_query = data.get("query")
        order = data.get("order", order)
    elif isinstance(data, str):
        base_query = data
        
    if base_query and tag_query not in base_query:
        new_key = f"{base_key}{suffix}"
        new_query = f"({base_query}) AND {tag_query}"
        resolver.register_dynamic_query(new_key, new_query, order)
        if logger:
            logger.info(f"   💉 Injected tag '{tag_query}' into '{base_key}' -> '{new_key}'")
        _INJECTION_CACHE[cache_key] = (new_key, new_query, order)
        return new_key
    
    return None

# 4. PARSING UTILITIES

def extract_episode_range(query: str) -> Tuple[Optional[int], Optional[int]]:
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


def count_episodes_in_range(query: str) -> int:
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

def is_movie_query(query: str) -> bool:
    """
    Heuristic to check if a query targets a movie.
    Used to determine default play count (1 for movies, all for shows).
    """
    if not query: return False
    return "type:movie" in query or "type:\"movie\"" in query

def get_play_count(query: str) -> Optional[int]:
    """
    Determines how many items a query represents.
    Returns 1 for movies or single episodes.
    Returns count for episode ranges.
    Returns None for unbounded queries (entire shows/collections).
    """
    if not query:
        return None
    if is_movie_query(query):
        return 1
    count = count_episodes_in_range(query)
    return count if count > 0 else None

def extract_title_from_query(query: str) -> Optional[str]:
    """Extract show/movie title from a Lucene query."""
    if not query: return None
    # Handles: title:"Foo Bar", show_title:"Foo Bar", title:Foo
    match = re.search(r'(?:show_)?title:(?:"([^"]+)"|([^\s]+))', query)
    if match:
        return match.group(1) or match.group(2)
    return None
