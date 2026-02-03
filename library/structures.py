# scripts/library/structures.py
"""
Smart collection classes for scheduling logic.
Separated from content definitions to keep the library clean.
"""

from datetime import date
from dataclasses import dataclass
from typing import List, Any, Set, Optional, Tuple, Union

class RandomCollection:
    """
    Picks randomly from items without repeats until all have been played.
    Resets after full cycle. Good for variety programming.
    """
    def __init__(self, items: List[Any]):
        self.items: List[Any] = items
        self.played: Set[Any] = set()
        self.last_played: Optional[Any] = None
    
    def pick(self, boss: Any) -> Any: # boss: DayDirector
        candidates = [i for i in self.items if i not in self.played]
        if not candidates:
            self.played.clear()
            candidates = self.items.copy()
        
        # Try to avoid the last played item to prevent back-to-back repeats
        choices = [x for x in candidates if x != self.last_played]
        if not choices:
            choices = candidates
        
        choice = boss._rng(f"random_collection_pick:{id(self)}").choice(choices)
        self.played.add(choice)
        self.last_played = choice
        return choice


class OrderedCollection:
    """
    Cycles through items in sequential order.
    Good for curated storytelling or episode progression.
    """
    def __init__(self, items: List[Any]):
        self.items: List[Any] = items
        self.index: int = 0
    
    def pick(self, boss: Any = None) -> Any: # boss is optional for OrderedCollection as it's deterministic
        choice = self.items[self.index % len(self.items)]
        self.index += 1
        return choice

class DailyOrderedCollection:
    """
    Cycles through items in order, but resets to the beginning on a new day.
    Ensures the first item (Anchor) always plays first in the block.
    """
    def __init__(self, items: List[Any]):
        """
        Initialize the collection.
        
        Args:
            items: List of content keys or objects to cycle through.
        """
        self.items: List[Any] = items
        self.index: int = 0
        self.last_date: Optional[date] = None
    
    def pick(self, boss: Any) -> Any:
        """
        Pick the next item in the sequence.
        Resets to index 0 if the date has changed since the last pick.
        
        Args:
            boss: DayDirector instance (provides current date).
            
        Returns:
            The selected content item.
        """
        current_date = boss.now.date()
        if self.last_date != current_date:
            self.index = 0
            self.last_date = current_date
            
        choice = self.items[self.index % len(self.items)]
        self.index += 1
        return choice

class WeightedCollection:
    """
    Picks items based on probability weights.
    Input: List of tuples [("show_a", 0.8), ("show_b", 0.2)]
    """
    def __init__(self, items: List[Tuple[Any, float]]):
        self.items: List[Tuple[Any, float]] = items # List of (key, weight)
        self.keys: List[Any] = [k for k, w in items]
        self.weights: List[float] = [w for k, w in items]

    def pick(self, boss: Any) -> Any: # boss: DayDirector
        return boss._rng(f"weighted_collection_pick:{id(self)}").choices(self.keys, weights=self.weights, k=1)[0]

@dataclass
class SeriesRelay:
    """
    Plays items in order based on a fixed schedule from a start date.
    Used for "Series Relay" (Show A finishes, then Show B starts).
    
    Attributes:
        items: List of (content_key, episode_count) tuples.
        start_date: The anchor date (date object) or season string (e.g. "WINTER").
        frequency: "daily" or "weekly" (how often the slot advances).
        episodes_per_slot: Number of episodes to play per slot (default 1).
        intro: Optional content key to play before the episode(s).
        outro: Optional content key to play after the episode(s).
    """
    items: List[Tuple[str, int]]
    start_date: Union[date, str]
    frequency: str = "weekly"
    episodes_per_slot: int = 1
    intro: Optional[str] = None
    outro: Optional[str] = None

@dataclass
class AppointmentBlock:
    """
    Plays specific seasons starting on specific absolute dates (Appointment TV).
    Falls back to off_season_content when no season is active.
    
    Attributes:
        seasons: List of (content_key, episode_count, start_date) tuples.
                 start_date can be a date object or (Year, Season) tuple.
        off_season_content: Content to play when no season is active.
        frequency: "daily" or "weekly".
        loop: If True, the entire block of seasons repeats after the last one ends.
        intro: Optional content key to play before the episode(s).
        outro: Optional content key to play after the episode(s).
        episodes_per_slot: Number of episodes to play per slot (default 1).
    """
    seasons: List[Tuple[str, int, Union[date, Tuple[int, str]]]]
    off_season_content: Optional[str] = None
    frequency: str = "weekly"
    loop: bool = False
    intro: Optional[str] = None
    outro: Optional[str] = None
    episodes_per_slot: int = 1
    
    def __post_init__(self):
        """Validate configuration with helpful errors."""
        
        # Check seasons exist
        if not self.seasons:
            raise ValueError(
                "AppointmentBlock requires at least one season.\n"
                "Example: seasons=[('lost_s1', 25, (2026, 'FALL'))]"
            )
        
        # Check frequency
        if self.frequency not in ["weekly", "daily"]:
            raise ValueError(
                f"Invalid frequency '{self.frequency}'. "
                f"Must be 'weekly' or 'daily'."
            )
            
        # Check episodes_per_slot
        if self.episodes_per_slot < 1:
            raise ValueError(f"episodes_per_slot must be >= 1, got {self.episodes_per_slot}")
        
        # Validate season format
        for i, season in enumerate(self.seasons):
            if not isinstance(season, tuple) or len(season) != 3:
                raise ValueError(
                    f"Season {i+1} has invalid format: {season}\n"
                    f"Expected: (content_key, episode_count, premiere_date)\n"
                    f"Example: ('lost_s1', 25, (2026, 'FALL'))"
                )
            
            content, episodes, premiere = season
            
            # Validate content key
            if not isinstance(content, str):
                raise ValueError(f"Season {i+1}: content_key must be string, got {type(content)}")
            
            # Validate episode count
            if not isinstance(episodes, int) or episodes <= 0:
                raise ValueError(f"Season {i+1}: episode_count must be positive integer, got {episodes}")
            
            # Validate premiere format
            if isinstance(premiere, tuple):
                if len(premiere) != 2:
                    raise ValueError(f"Season {i+1}: premiere tuple must be (year, season), got {premiere}")
                year, season_name = premiere
                if not isinstance(year, int):
                    raise ValueError(f"Season {i+1}: year must be integer, got {year}")
                if season_name.upper() not in ["SPRING", "SUMMER", "FALL", "WINTER"]:
                    raise ValueError(f"Season {i+1}: invalid season '{season_name}'. Must be SPRING, SUMMER, FALL, or WINTER")

def annual_show(
    content_pattern: str,
    seasons: int,
    episodes: List[int],
    premiere_year: int,
    start_season: str = "FALL",
    reruns: Optional[str] = None,
    frequency: str = "weekly",
    episodes_per_slot: int = 1
) -> AppointmentBlock:
    """
    Helper to create an AppointmentBlock for a show that airs annually.
    
    Automatically generates the season list based on a start year and episode counts.
    
    Args:
        content_pattern: String with {n} placeholder, e.g. "lost_s{n}"
        seasons: Total number of seasons
        episodes: List of episode counts per season
        premiere_year: Year the first season starts
        start_season: Season name (FALL, WINTER, SPRING, SUMMER)
        reruns: Content to play during off-season
        frequency: Playback frequency
        episodes_per_slot: Episodes to play per slot
    """
    if len(episodes) != seasons:
        raise ValueError(f"Episode count list length ({len(episodes)}) must match seasons count ({seasons})")
        
    season_list = []
    for i in range(seasons):
        season_num = i + 1
        key = content_pattern.format(n=season_num)
        count = episodes[i]
        year = premiere_year + i
        season_list.append((key, count, (year, start_season)))
        
    return AppointmentBlock(
        seasons=season_list,
        off_season_content=reruns,
        frequency=frequency,
        episodes_per_slot=episodes_per_slot
    )

def alternating_seasons(
    shows: List[Tuple[str, List[int]]],
    start_year: int,
    start_season: str = "FALL",
    reruns: Optional[str] = None,
    frequency: str = "weekly"
) -> AppointmentBlock:
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
                
    return AppointmentBlock(
        seasons=season_list,
        off_season_content=reruns,
        frequency=frequency
    )