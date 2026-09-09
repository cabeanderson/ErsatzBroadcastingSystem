# scripts/logic/factories.py
"""
Factory functions to build complex scheduling structures like AppointmentBlock.
"""

from typing import List, Optional, Tuple, Union, Dict, Any
from datetime import date, timedelta
import re
from .structures import Program, OrderedCollection
from scripts.core import registry, states
from .models import MarathonDefinition
from scripts.library.queries import show_by_title

def annual_show(
    episodes_per_season: List[int],
    show_title: Optional[str] = None,
    content_pattern: Optional[str] = None,
    # Broadcast Mode
    premiere_year: Optional[int] = None,
    premiere_season: Union[str, Tuple[str, str]] = "FALL",
    # Contiguous Mode
    start_date: Optional[date] = None,
    reruns: Optional[Any] = None,
    finale: Optional[str] = None,
    frequency: Union[str, List[str]] = "weekly",
    episodes_per_slot: int = 1,
    loop: bool = False,
    loop_restart_season: Union[str, bool, None] = None
) -> Program:
    """
    Helper to create an AppointmentBlock for a show that airs annually.
    
    Supports two modes:
    1. Broadcast Mode: Uses `premiere_year` and `premiere_season` for gapped, yearly seasons.
    2. Contiguous Mode: Uses `start_date` for gapless sequential playback on a specific frequency.

    Args:
        frequency: "weekly", "daily", or a list of day labels like ["MONDAY", "FRIDAY"].
        loop_restart_season: Season when loop should restart (e.g., "FALL").
                             If None, uses premiere_season.
                             If False, loops immediately after final episode.
    """
    seasons = len(episodes_per_season)

    if premiere_year is None and start_date is None:
        raise ValueError("Must provide either 'premiere_year' (Broadcast Mode) or 'start_date' (Contiguous Mode)")
    if premiere_year is not None and start_date is not None:
        raise ValueError("Cannot use 'premiere_year' and 'start_date' at the same time.")
    if len(episodes_per_season) != seasons:
        raise ValueError(f"Episode count list length ({len(episodes_per_season)}) must match seasons count ({seasons})")
    
    if not content_pattern and not show_title:
        raise ValueError("Must provide either 'content_pattern' or 'show_title'")

    # Default: loop restarts in same season as premiere. Only the season half
    # matters -- `frequency` already carries the day of the week.
    #
    # Contiguous Mode has no premiere season to restart in. The caller passed
    # `start_date` and never named one, so `premiere_season` is still sitting
    # at its "FALL" default -- and taking it meant a weekday strip that
    # finished its run in June resolved to nothing until mid-September: the
    # block skips the item, time does not advance, and the slot falls through
    # to the circuit breaker. A contiguous strip loops immediately, which is
    # what `start_date` means. Cartoon Network's six Toonami strips pass
    # `loop_restart_season=False` by hand today for exactly this reason.
    if loop and loop_restart_season is None:
        loop_restart_season = False if start_date else states.season_label(premiere_season)

    season_list = []
    generated_queries = {}

    if start_date: # Contiguous Mode
        current_start = start_date
        for i in range(seasons):
            season_num = i + 1
            key = _get_content_key(show_title, content_pattern, season_num, generated_queries)
            count = episodes_per_season[i]
            season_list.append((key, count, current_start))
            # The resolver will calculate the end date based on frequency, so we just need the start.
            # We pass the start date of the *entire series* for each season.
    else: # Broadcast Mode
        for i in range(seasons):
            season_num = i + 1
            key = _get_content_key(show_title, content_pattern, season_num, generated_queries)
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

def monthly_rotation(items: List[Any], start_month: int = 1) -> Dict[str, Any]:
    """
    Builds a month-keyed variant dict that cycles through `items`.

    Returns a plain dict of {MONTH_LABEL: item}, which the resolution pipeline
    already understands -- no new resolution logic. Use it anywhere a block or
    item is accepted, to keep a rotation on the air without repeating a short
    show into the ground:

        MIDDAY = monthly_rotation([BLOCK_A, BLOCK_B, BLOCK_C])
        # Jan -> A, Feb -> B, Mar -> C, Apr -> A, ...

    **Twelve items is the ceiling, and a thirteenth is refused rather than
    dropped.** The returned dict has one key per month, so items[12:] could
    never be indexed and never aired -- which is how Be Kind Rewind's
    spotlights ran eight directors for months while the author believed a
    longer list was on the channel. Use `multiyear_rotation` for a longer list;
    it delegates here below thirteen, so switching is free.

    Args:
        items: Content to cycle, at most 12. 12 gives each month its own.
        start_month: Month (1-12) that receives items[0]. Defaults to January.

    Raises:
        ValueError: on an empty list, a start_month outside 1-12, or more than
            twelve items.
    """
    if not items:
        raise ValueError("monthly_rotation() needs at least one item")
    if not 1 <= start_month <= 12:
        raise ValueError(f"start_month must be 1-12, got {start_month}")
    if len(items) > 12:
        raise ValueError(
            f"monthly_rotation() got {len(items)} items but a year has 12 "
            f"months, so {len(items) - 12} of them could never air. Use "
            f"multiyear_rotation() for a rotation this long."
        )

    return {
        registry.MONTHS[m]: items[(m - start_month) % len(items)]
        for m in range(1, 13)
    }


def multiyear_rotation(
    items: List[Any], start_month: int = 1, start_year: Optional[int] = None
) -> Dict[str, Any]:
    """
    Builds a rotation that takes more than one year to come back around.

    `monthly_rotation` can only ever express twelve slots, because every label
    it keys on is a function of the calendar *within* a year. This keys on the
    year-cycle labels as well, so a list of 36 gets 36 distinct months:

        SPOTLIGHT = multiyear_rotation([A, B, C, ... 36 items])
        # 2027 Jan -> A ... Dec -> L
        # 2028 Jan -> M ... Dec -> X
        # 2029 Jan -> Y ... Dec -> AJ
        # 2030 Jan -> A, and round again

    Returns a nested dict, {YEAR_LABEL: {MONTH_LABEL: item}}. The resolution
    pipeline already unwraps nested label dicts, so this needs no new
    resolution logic either -- `_unwrap_nested_structure` resolves the year
    dict, then the month dict inside it, on successive passes.

    Cycle length is derived from the list: 13-24 items is a two-year rotation,
    25-36 a three-year, up to the five years `registry.YEAR_CYCLES` allows.
    A list of 12 or fewer is delegated to `monthly_rotation`, so this is safe
    to use wherever the list might grow later.

    **Phase is absolute, not relative to a start date.** Year `Y` of an
    `n`-year cycle is the year where `year % n == Y`, which means the rotation
    cannot drift the way an appointment anchored on a raw day count does --
    the defect that had 21 of 35 annual appointments opening on episode 2.
    The cost is that `items[0]` lands in whichever calendar year the modulo
    picks, which for an unnamed rotation does not matter and for a curated one
    does: pass `start_year` to say which year the front of the list belongs to.

    Args:
        items: Content to cycle. Up to 12 * max(registry.YEAR_CYCLES) items.
        start_month: Month (1-12) that receives items[0], within the first
            year of the cycle. Defaults to January.
        start_year: Calendar year that airs the front of the list. Defaults to
            None, which leaves phase to the modulo. Only the year's residue
            matters -- for a three-year cycle 2027, 2030 and 2033 are the same
            instruction -- so this anchors the cycle without dating it.

    Raises:
        ValueError: on an empty list, a start_month outside 1-12, or more
            items than the longest supported cycle can hold.
    """
    if not items:
        raise ValueError("multiyear_rotation() needs at least one item")
    if not 1 <= start_month <= 12:
        raise ValueError(f"start_month must be 1-12, got {start_month}")

    if len(items) <= 12:
        return monthly_rotation(items, start_month)


    years = -(-len(items) // 12)          # ceil, in whole years
    longest = max(registry.YEAR_CYCLES)
    if years > longest:
        raise ValueError(
            f"multiyear_rotation() got {len(items)} items, which needs a "
            f"{years}-year cycle; the longest labelled cycle is {longest} "
            f"years ({longest * 12} items). Widen registry.YEAR_CYCLES or "
            f"split the rotation."
        )

    # The cycle is one flat run of `years * 12` months. Slot 0 is start_month
    # of cycle-year 0, and the list is indexed modulo its own length, so a
    # partly-filled final year repeats from the front rather than going dark.
    span = years * 12
    offset = start_year % years if start_year is not None else 0
    return {
        f"YEAR_OF_{years}_{(y + offset) % years}": {
            registry.MONTHS[m]: items[((y * 12) + (m - start_month)) % span % len(items)]
            for m in range(1, 13)
        }
        for y in range(years)
    }


def _get_content_key(show_title, content_pattern, season_num, generated_queries):
    """Helper to generate and register a content key for a season."""
    if show_title:
        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', show_title).lower()
        key = f"__auto_{safe_title}_s{season_num}"
        generated_queries[key] = f'{show_by_title(show_title)} AND season_number:{season_num}'
    else:
        key = content_pattern.format(n=season_num)
    return key


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
        safe_title = show_title.replace('"', '\\"')
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