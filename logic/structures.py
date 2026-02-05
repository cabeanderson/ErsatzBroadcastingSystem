# scripts/logic/structures.py
"""
Smart collection classes for scheduling logic.
Separated from content definitions to keep the library clean.
"""

from datetime import date
from dataclasses import dataclass
from typing import List, Any, Set, Optional, Tuple, Union, Dict
from scripts.logic.models import ContentItem

class RandomCollection:
    """
    Picks randomly from items without repeats until all have been played.
    Resets after full cycle. Good for variety programming.
    """
    def __init__(self, items: List[Any]):
        self.items: List[Any] = []
        for item in items:
            if isinstance(item, dict):
                self.items.append(ContentItem(**item))
            else:
                self.items.append(item)
        # Track played items by index to handle unhashable types (like dicts)
        self.played_indices: Set[int] = set()
        self.last_played_index: Optional[int] = None
    
    def pick(self, boss: Any) -> Any: # boss: DayDirector
        # Filter indices that haven't been played
        candidates = [i for i in range(len(self.items)) if i not in self.played_indices]
        if not candidates:
            self.played_indices.clear()
            candidates = list(range(len(self.items)))
        
        # Try to avoid the last played index to prevent back-to-back repeats
        choices = [x for x in candidates if x != self.last_played_index]
        if not choices:
            choices = candidates
        
        choice_index = boss._rng(f"random_collection_pick:{id(self)}").choice(choices)
        self.played_indices.add(choice_index)
        self.last_played_index = choice_index
        return self.items[choice_index]


class OrderedCollection:
    """
    Cycles through items in sequential order.
    Good for curated storytelling or episode progression.
    """
    def __init__(self, items: List[Any]):
        self.items: List[Any] = []
        for item in items:
            if isinstance(item, dict):
                self.items.append(ContentItem(**item))
            else:
                self.items.append(item)
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
class MarathonSequence:
    """
    A sequence of content items to be played in order during a marathon.
    """
    items: List[Any]
    
    def __post_init__(self):
        # Auto-convert dicts to ContentItem
        new_items = []
        for item in self.items:
            if isinstance(item, dict):
                new_items.append(ContentItem(**item))
            else:
                new_items.append(item)
        self.items = new_items

@dataclass
class SeriesRelay:
    """
    Plays items in order based on a fixed schedule from a start date.
    Used for "Series Relay" (Show A finishes, then Show B starts).
    
    NOTE: This timeline runs continuously based on the start_date. It does NOT
    pause when the slot is taken over by an Anchor show. It behaves like a 
    syndicated rerun cycle running in the background.
    """
    items: List[Any] # List of (content, count) tuples OR dicts with "count" key
    start_date: Union[date, str]
    frequency: str = "weekly"
    episodes_per_slot: int = 1
    intro: Optional[str] = None
    outro: Optional[str] = None

    def __post_init__(self):
        # Normalize items to List[Tuple[Content, int]]
        normalized = []
        for item in self.items:
            # 1. Handle clean dict syntax: {"title": "Show", "count": 5}
            if isinstance(item, dict) and "count" in item:
                # Extract count, use rest for ContentItem
                item_copy = item.copy()
                count = item_copy.pop("count")
                normalized.append((ContentItem(**item_copy), count))
            
            # 2. Handle legacy tuple syntax: ("key", 5) or ({"title":...}, 5)
            elif isinstance(item, tuple) and len(item) == 2:
                content, count = item
                if isinstance(content, dict):
                    content = ContentItem(**content)
                normalized.append((content, count))
            
            else:
                normalized.append(item)
        
        self.items = normalized

@dataclass
class AppointmentBlock:
    """
    Plays specific seasons starting on specific absolute dates (Appointment TV).
    Falls back to off_season_content when no season is active.
    """
    seasons: List[Tuple[str, int, Union[date, Tuple[int, str]]]]
    off_season_content: Optional[Union[str, Dict[str, str], "SeriesRelay"]] = None
    generated_queries: Optional[Dict[str, str]] = None
    finale_content: Optional[str] = None
    frequency: str = "weekly"
    loop: bool = False
    intro: Optional[str] = None
    outro: Optional[str] = None
    episodes_per_slot: int = 1
    loop_restart_season: Union[str, bool, None] = None
    
    def __post_init__(self):
        # Validation logic omitted for brevity, but should be here
        pass

@dataclass
class AppointmentSlot:
    """A single time-slot within a larger AppointmentLineup."""
    anchor: AppointmentBlock
    fillers: Optional[Union[str, List[str], Dict[str, str], "SeriesRelay", "RandomCollection", "OrderedCollection"]] = None

@dataclass
class AppointmentLineup:
    """
    A container for multiple, hour-specific appointment slots, creating a sequential block.
    """
    slots: List[AppointmentSlot]
    mode: str = "sequential" # "sequential" (no gaps) or "hourly" (strict slots)