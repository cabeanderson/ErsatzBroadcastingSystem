"""
Data models for marathons, events, and blocks.
"""

from dataclasses import dataclass, field
from typing import Callable, Tuple, Optional, Any, Dict, List


@dataclass
class Marathon:
    """Marathon configuration."""
    name: str
    trigger: Callable
    collection: Any
    hours: Optional[Tuple[int, int]] = None
    priority: int = 1


@dataclass
class MultiDayEvent:
    """Multi-day event configuration."""
    name: str
    trigger: Callable
    duration_days: int
    content: Any
    timeslots: List[str] = field(default_factory=list)
    priority: int = 1


@dataclass
class Branding:
    """Reusable branding profile for BrandedBlocks."""
    intro: Optional[str] = None
    outro: Optional[str] = None
    bumpers: Optional[str] = None


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