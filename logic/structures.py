# scripts/logic/structures.py
"""
Smart collection classes for scheduling logic.
Separated from content definitions to keep the library clean.
"""

from datetime import date
from dataclasses import dataclass
from typing import List, Any, Set, Optional, Tuple, Union, Dict
from scripts.logic.models import ContentItem
from scripts.core.identity import stable_hash
from scripts.settings import DEFAULT_APPOINTMENT_START_DATE

# Fixed anchor used to map a calendar date to a deterministic position in
# sequential collections, so the same date always resolves to the same item.
_EPOCH = DEFAULT_APPOINTMENT_START_DATE

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
        # Track unplayed indices directly for better performance
        self.unplayed_indices: List[int] = list(range(len(self.items)))
        self.last_played_index: Optional[int] = None
        # Content-derived identity keeps the RNG seed stable across process
        # restarts (id() would not). See core/identity.py.
        self._identity: str = stable_hash(self.items)
        self._last_date: Optional[date] = None

    def pick(self, boss: Any) -> Any: # boss: DayDirector
        if not self.items:
            return None

        # Reset the no-repeat state at the start of each day so a day's
        # selection depends only on the date, not on how many picks happened
        # on previous days. This makes the output reproducible across restarts.
        current_date = boss.now.date() if boss is not None else None
        if current_date is not None and current_date != self._last_date:
            self.unplayed_indices = list(range(len(self.items)))
            self.last_played_index = None
            self._last_date = current_date

        # Reset if exhausted within the day
        if not self.unplayed_indices:
            self.unplayed_indices = list(range(len(self.items)))

        choices = self.unplayed_indices

        # Try to avoid the last played index to prevent back-to-back repeats (relevant on reset)
        if self.last_played_index is not None and len(self.items) > 1:
            if self.last_played_index in choices:
                choices = [x for x in choices if x != self.last_played_index]

        choice_index = boss._rng(f"random_collection_pick:{self._identity}").choice(choices)

        self.unplayed_indices.remove(choice_index)
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
        self._last_date: Optional[date] = None
        self._intraday: int = 0

    def pick(self, boss: Any = None) -> Any: # boss is optional for OrderedCollection
        n = len(self.items)
        if n == 0:
            return None

        if boss is not None:
            # Anchor progression to the calendar: advance one step per day, plus
            # one per pick within a day. The result is a pure function of the
            # date, so it is reproducible across restarts and "moves on" while
            # the server is offline (matching the appointment-TV philosophy).
            current_date = boss.now.date()
            if current_date != self._last_date:
                self._last_date = current_date
                self._intraday = 0
            day_offset = (current_date - _EPOCH).days
            idx = (day_offset + self._intraday) % n
            self._intraday += 1
            return self.items[idx]

        # No director context: fall back to a simple running counter.
        choice = self.items[self.index % n]
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
        self.items: List[Any] = []
        for item in items:
            if isinstance(item, dict):
                self.items.append(ContentItem(**item))
            else:
                self.items.append(item)
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
        # Stable seed identity (see core/identity.py) instead of id().
        self._identity: str = stable_hash(self.keys)

    def pick(self, boss: Any) -> Any: # boss: DayDirector
        return boss._rng(f"weighted_collection_pick:{self._identity}").choices(self.keys, weights=self.weights, k=1)[0]

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
class Program:
    name: str
    content: Any
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None
    # "none" | "some" | "all"; None defers to the parent in the cascade.
    smart_bumpers: Optional[str] = None
    epg_title: Optional[str] = None
    commercials: Optional[str] = None
    commercial_duration: int = 0
    scheduling: Optional[Dict[str, Any]] = None
    fill_strategy: str = "yield" # "fill", "yield", "gap"
    play_count: Optional[int] = None # For marathon items
    # For marathon items whose content is unbounded (a whole show, no episode
    # range). Instead of guessing a huge play_count -- which ErsatzTV commits in
    # full, with no time bound, overrunning the slot by days -- the engine asks
    # for exactly the remaining window via add_duration.
    fill_window: bool = False
    start_point: Optional[Tuple[int, int]] = None # For marathon items (season, episode)
    force_start: bool = False # If True, force skip to start_point on every play (for Marathons)
    filler: Optional[Any] = None
    # Feature Overrides
    enable_commercials: Optional[bool] = None
    enable_bumpers: Optional[bool] = None
    enable_filler: Optional[bool] = None
    enable_holiday_injection: Optional[bool] = None
    enable_seasonal_injection: Optional[bool] = None

    def __post_init__(self):
        if self.fill_strategy not in ["fill", "yield", "gap", "bridge"]:
            raise ValueError(f"Program '{self.name}': Invalid fill_strategy '{self.fill_strategy}'. Must be 'fill', 'yield', 'gap', or 'bridge'.")
        if self.fill_strategy == "fill" and not self.filler:
            raise ValueError(f"Program '{self.name}': fill_strategy='fill' requires 'filler' content.")
        if not self.content and not self.scheduling:
            raise ValueError(f"Program '{self.name}': Must have either 'content' or 'scheduling'.")

@dataclass
class Block:
    name: str
    items: List[Any] # List of Programs or content
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None
    # "none" | "some" | "all"; None defers to the parent in the cascade.
    smart_bumpers: Optional[str] = None
    commercials: Optional[str] = None
    commercial_duration: int = 0
    use_epg_group: bool = False
    fill_strategy: str = "yield" # "fill", "yield", "gap", "bridge"
    strict_window: bool = True # If False, allows content to overflow timeslot
    filler: Optional[Any] = None
    # Feature Overrides
    enable_commercials: Optional[bool] = None
    enable_bumpers: Optional[bool] = None
    enable_filler: Optional[bool] = None
    enable_holiday_injection: Optional[bool] = None
    enable_seasonal_injection: Optional[bool] = None

    def __post_init__(self):
        if self.fill_strategy not in ["fill", "yield", "gap", "bridge"]:
            raise ValueError(f"Block '{self.name}': Invalid fill_strategy '{self.fill_strategy}'. Must be 'fill', 'yield', 'gap', or 'bridge'.")
        if self.fill_strategy == "fill" and not self.filler:
            raise ValueError(f"Block '{self.name}': fill_strategy='fill' requires 'filler' content.")

        # Validate against nested blocks to prevent recursion crashes
        items_to_check = self.items
        # Unpack items if passed as a Collection object
        if hasattr(self.items, "items") and isinstance(self.items.items, list):
            items_to_check = self.items.items
            
        if isinstance(items_to_check, list):
            for item in items_to_check:
                self._validate_item(item)

    def _validate_item(self, item: Any) -> None:
        if isinstance(item, Block):
            raise ValueError(f"Configuration Error: Block '{self.name}' contains nested Block '{item.name}'. Nested blocks are not supported.")
        
        if isinstance(item, Program) and isinstance(item.content, Block):
            raise ValueError(f"Configuration Error: Block '{self.name}' contains Program '{item.name}' holding a nested Block.")

        # Check collections (duck typing for 'items' list)
        if hasattr(item, "items") and isinstance(item.items, list) and not isinstance(item, (str, dict)):
            for sub_item in item.items:
                if isinstance(sub_item, Block):
                    raise ValueError(f"Configuration Error: Block '{self.name}' contains a Collection with nested Block '{sub_item.name}'.")