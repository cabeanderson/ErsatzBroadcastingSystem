"""
Data models for marathons, events, and blocks.
"""

from dataclasses import dataclass, field
from typing import Callable, Tuple, Optional, Any, Dict, List, Union
from scripts.logic.queries import is_movie_query


@dataclass
class Marathon:
    """Marathon configuration."""
    name: str
    trigger: Callable
    collection: Any
    hours: Optional[Tuple[int, int]] = None
    priority: int = 1

@dataclass
class MarathonDefinition:
    """A self-contained definition for a marathon's content and metadata."""
    name: str  # The EPG title for the marathon
    query: str # The Lucene query for the content
    description: Optional[str] = None
    order: str = "Chronological"
    start_hour: Optional[int] = None # Optional override for start time within the marathon window
    # For skipping to a specific point
    start_mode: str = "beginning" # "beginning" or "random"
    start_season: Optional[Union[int, List[int]]] = None
    start_episode: Optional[int] = None
    episode_count: Optional[int] = None # For sagas that aren't a full season
    media_type: Optional[str] = None # "movie" or "show"

    def __post_init__(self):
        if self.start_mode not in ["beginning", "random"]:
            raise ValueError(f"start_mode must be 'beginning' or 'random', got '{self.start_mode}'")
        if self.start_mode == "random" and self.start_season is None:
            raise ValueError("Random start_mode requires start_season")

    def is_movie(self) -> bool:
        """Determine if this item is a movie based on metadata or query."""
        if self.media_type == "movie":
            return True
        # Fallback to query inspection
        return is_movie_query(self.query)


@dataclass
class Branding:
    """Reusable branding profile for BrandedBlocks."""
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None


@dataclass
class ContentItem:
    """A single item of content within a collection or block."""
    title: str
    query: Optional[str] = None
    order: str = "Shuffle"
    media_type: Optional[str] = None # "movie" or "show"

    def is_movie(self) -> bool:
        """Determine if this item is a movie based on metadata or query."""
        if self.media_type == "movie":
            return True
        # Fallback to query inspection
        return is_movie_query(self.query)

@dataclass
class BrandedBlock:
    """Branded programming block."""
    name: str
    content: Any
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None
    use_epg_group: bool = True
    branding: Optional[Branding] = None
    specific_intros: Optional[Dict[str, str]] = None
    commercials_between_items: int = 0
    commercial_content: Any = "commercials_spot"

    def __post_init__(self):
        """Apply branding profile defaults if specific fields are missing."""
        if self.branding:
            if self.intro is None: self.intro = self.branding.intro
            if self.outro is None: self.outro = self.branding.outro
            if self.bumpers is None: self.bumpers = self.branding.bumpers

    def has_branding(self, sources: Dict[str, Any]) -> bool:
        """Check if block has any active branding elements."""
        # Otherwise check if source clips exist
        has_intro = self.intro and self.intro in sources
        has_outro = self.outro and self.outro in sources
        has_bumpers = self.bumpers and self.bumpers in sources
        return has_intro or has_outro or has_bumpers


@dataclass
class BlockProfile:
    """
    Defines how a time block blends default/seasonal/holiday content.
    
    Args:
        max_ratio: Maximum ratio of alt content at peak (0.0-1.0)
        bias: Adjust ratio up/down (-1.0 to +1.0)
        hangover_ratio: Ratio during hangover (0.0-1.0, default: 0.5)
    """
    max_ratio: float = 1.0
    bias: float = 0.0
    hangover_ratio: float = 0.5

    def respond(self, ramp_signal: float, hangover_signal: float) -> float:
        """
        Shape an incoming signal into a blend ratio.
        """
        if hangover_signal > 0:
            return self.hangover_ratio * hangover_signal

        if ramp_signal > 0:
            # Apply bias and clamp
            val = (ramp_signal * self.max_ratio) + self.bias
            return max(0.0, min(1.0, val))
            
        return 0.0

@dataclass
class PlayOnce:
    """
    Wrapper to signal that content should play exactly one item,
    then fill the remainder of the timeslot with the NEXT block's content.
    """
    content: Any

@dataclass
class Fallback:
    """
    Represents a content choice with a fallback option.
    The scheduler will try to play `primary`. If it's empty or fails,
    it will immediately play `secondary`.
    """
    primary: Any
    secondary: Any

@dataclass
class Swap:
    """
    Signals a 100% replacement of base content in a SeasonalBlock.
    """
    content: Any

@dataclass
class Feather:
    """
    Signals a probabilistic blend of content in a SeasonalBlock.
    """
    content: Any
    ratio: float = 0.5

@dataclass(frozen=True)
class CommercialBreak:
    """
    Signals an explicit commercial break of a specific duration.
    """
    duration_seconds: int = 120
    content: Any = "commercials_spot"

@dataclass
class ResolutionResult:
    """
    Standardized output from the resolution pipeline.
    Carries the final content key, any wrappers, and metadata about the source.
    """
    key: Optional[str] = None          # The final registry key to play
    wrapper: Optional[Any] = None      # BrandedBlock, PlayOnce, or Fallback
    source: str = "schedule"           # Origin: "schedule", "holiday", "seasonal", "injection"

    @property
    def resolved_content(self) -> Optional[Any]:
        """
        Get the final resolved content (wrapper or key).
        Returns the wrapper if present, otherwise returns the key.
        """
        return self.wrapper if self.wrapper else self.key

    def __bool__(self) -> bool:
        """Allow truthiness checks on ResolutionResult."""
        return self.key is not None or self.wrapper is not None