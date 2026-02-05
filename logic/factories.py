# scripts/logic/factories.py
"""
Factory functions to build complex scheduling structures like AppointmentBlock.
"""

from typing import List, Optional, Tuple, Union, Dict, Any
import re
from .structures import Program, OrderedCollection
from .models import MarathonDefinition
from .queries import show_by_title, _escape_quotes

def annual_show(
    seasons: int,
    episodes_per_season: List[int],
    premiere_year: int,
    content_pattern: Optional[str] = None,
    show_title: Optional[str] = None,
    premiere_season: str = "FALL",
    reruns: Optional[Any] = None,
    finale: Optional[str] = None,
    frequency: str = "weekly",
    episodes_per_slot: int = 1,
    loop: bool = False,
    loop_restart_season: Union[str, bool, None] = None
) -> Program:
    """
    Helper to create an AppointmentBlock for a show that airs annually.
    
    Automatically generates the season list based on a start year and episode counts.

    Args:
        loop_restart_season: Season when loop should restart (e.g., "FALL").
                             If None, uses premiere_season.
                             If False, loops immediately after final episode.
    """
    if len(episodes_per_season) != seasons:
        raise ValueError(f"Episode count list length ({len(episodes_per_season)}) must match seasons count ({seasons})")
    
    if not content_pattern and not show_title:
        raise ValueError("Must provide either 'content_pattern' or 'show_title'")

    # Default: loop restarts in same season as premiere
    if loop and loop_restart_season is None:
        loop_restart_season = premiere_season

    season_list = []
    generated_queries = {}

    for i in range(seasons):
        season_num = i + 1
        
        if show_title:
            # Auto-generate key and query
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', show_title).lower()
            key = f"__auto_{safe_title}_s{season_num}"
            generated_queries[key] = f'{show_by_title(show_title)} AND season_number:{season_num}'
        else:
            key = content_pattern.format(n=season_num)
            
        count = episodes_per_season[i]
        year = premiere_year + i
        season_list.append((key, count, (year, premiere_season)))
        
    return Program(
        name=show_title or "Annual Show",
        content=reruns,
        scheduling={
            "seasons": season_list,
            "frequency": frequency,
            "episodes_per_slot": episodes_per_slot,
            "loop": loop,
            "loop_restart_season": loop_restart_season,
            "generated_queries": generated_queries
        }
    )

def alternating_seasons(
    shows: List[Tuple[str, List[int]]],
    start_year: int,
    start_season: str = "FALL",
    reruns: Optional[Union[str, Dict[str, str]]] = None,
    frequency: str = "weekly",
    loop: bool = False
) -> Program:
    """
    Interleaves seasons of multiple shows annually.
    
    Example: Show A S1 (2026), Show B S1 (2027), Show A S2 (2028)...
    """
    max_seasons = max(len(s[1]) for s in shows)
    season_list = []
    current_year = start_year
    
    for season_idx in range(max_seasons):
        for show_pattern, episode_counts in shows:
            if season_idx < len(episode_counts):
                season_num = season_idx + 1
                key = show_pattern.format(n=season_num)
                count = episode_counts[season_idx]
                season_list.append((key, count, (current_year, start_season)))
                current_year += 1
                
    return Program(
        name="Alternating Seasons",
        content=reruns,
        scheduling={
            "seasons": season_list,
            "frequency": frequency,
            "loop": loop
        }
    )

def themed_marathon(
    show_title: str,
    title: str = None,
    description: str = None,
    theme_tag: str = None,
    season: int = None,
    episode_range: str = None,
    start_hour: int = 10,
    order: str = "Chronological",
    is_movie: bool = False,
    **kwargs
) -> MarathonDefinition:
    """
    Helper to build a marathon definition with an auto-generated query.
    Ensures themed blocks are distinct and chronological.
    """
    if is_movie:
        safe_title = _escape_quotes(show_title)
        query = f'type:movie AND title:"{safe_title}"'
    else:
        query = show_by_title(show_title)
    
    if theme_tag:
        query += f' AND tag:"{theme_tag}"'
    
    if season:
        query += f' AND season_number:{season}'
        
    if episode_range:
        query += f' AND episode_number:{episode_range}'
        
    return MarathonDefinition(
        name=title or f"{show_title} Marathon",
        description=description,
        query=query,
        order=order,
        start_hour=start_hour,
        media_type="movie" if is_movie else "show",
        **kwargs
    )

def episode_list(show_title: str, seasons: Union[int, List[int]], counts: Union[int, List[int]]) -> OrderedCollection:
    """
    Creates an OrderedCollection of individual episode queries.
    Forces strict sequential playback by resolving one episode at a time.
    
    Args:
        show_title: Name of the show
        seasons: Single int (1) or list of ints ([1, 2])
        counts: Single int (26) or list of ints ([26, 13]) matching seasons
    """
    # Normalize inputs to lists
    if isinstance(seasons, int): seasons = [seasons]
    if isinstance(counts, int): counts = [counts]
    
    if len(seasons) != len(counts):
        raise ValueError(f"Seasons count ({len(seasons)}) must match episode counts length ({len(counts)})")

    items = []
    base_query = show_by_title(show_title)
    
    for s_idx, season_num in enumerate(seasons):
        count = counts[s_idx]
        for i in range(1, count + 1):
            items.append({
                "title": f"{show_title} S{season_num} E{i}",
                "query": f"{base_query} AND season_number:{season_num} AND episode_number:{i}",
                "order": "Chronological"
            })
            
    return OrderedCollection(items)