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
class Program:
    name: str
    content: Any
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None
    epg_title: Optional[str] = None
    commercials: Optional[str] = None
    commercial_duration: int = 0
    scheduling: Optional[Dict[str, Any]] = None
    fill_strategy: str = "yield" # "fill", "yield", "gap"
    filler: Optional[Any] = None

    def __post_init__(self):
        if self.fill_strategy not in ["fill", "yield", "gap"]:
            raise ValueError(f"Program '{self.name}': Invalid fill_strategy '{self.fill_strategy}'. Must be 'fill', 'yield', or 'gap'.")
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
    commercials: Optional[str] = None
    commercial_duration: int = 0
    use_epg_group: bool = False
    fill_strategy: str = "yield" # "fill", "yield", "gap"
    filler: Optional[Any] = None

    def __post_init__(self):
        if self.fill_strategy not in ["fill", "yield", "gap"]:
            raise ValueError(f"Block '{self.name}': Invalid fill_strategy '{self.fill_strategy}'. Must be 'fill', 'yield', or 'gap'.")
        if self.fill_strategy == "fill" and not self.filler:
            raise ValueError(f"Block '{self.name}': fill_strategy='fill' requires 'filler' content.")