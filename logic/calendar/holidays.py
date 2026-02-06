# scripts/calendar/holidays.py
"""
Holiday detection and override system.
Provides both signal strengths and boolean flags for holiday programming.
"""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.core import registry

if TYPE_CHECKING:
    from scripts.logic.resolution.resolver import ContentResolver
    from scripts.core import DayDirector
    from scripts.playout import ChannelLogger

class HolidayContext:
    """
    Captures the current holiday state for easy querying.
    Provides both signal strengths (0.0-1.0) and boolean flags.
    """
    
    def __init__(self, boss: Any):
        self.boss: Any = boss
        self.envelope: Dict[str, float] = {}
        
        # Dynamically load signals from profiles
        for holiday_name, profile in HOLIDAY_PROFILES.items():
            if holiday_name == "default":
                continue
                
            key = holiday_name.lower()
            # Main ramp
            self.envelope[key] = boss.signal(holiday_name, window=profile.window)
            
            # Hangover ramp (if defined)
            if profile.hangover_days > 0:
                self.envelope[f"{key}_hangover"] = boss.signal(holiday_name, window=profile.hangover_days, hangover=True)
        
        # Convenience properties
        self.halloween = self.envelope.get("halloween", 0.0)
        self.halloween_hangover = self.envelope.get("halloween_hangover", 0.0)
        self.christmas = self.envelope.get("christmas", 0.0)
        self.christmas_hangover = self.envelope.get("christmas_hangover", 0.0)
        self.thanksgiving = self.envelope.get("thanksgiving", 0.0)
    
    def is_active(self, holiday: str, threshold: float = 0.7) -> bool:
        """Check if a holiday is active above threshold."""
        return self.envelope.get(holiday, 0.0) > threshold
    
    @property
    def is_holiday_season(self) -> bool:
        """True if ANY major holiday is active."""
        return (self.is_active("halloween") or
                self.is_active("halloween_hangover", threshold=0.5) or
                self.is_active("christmas") or 
                self.is_active("christmas_hangover", threshold=0.5) or
                self.is_active("thanksgiving"))
    
    @property
    def active_holidays(self) -> List[str]:
        """Returns list of currently active holiday names."""
        return [name for name, signal in self.envelope.items() if signal > 0.7]


def get_holiday_target(holiday_ctx: HolidayContext, target: Any, global_overrides: Optional[Dict[str, Any]] = None) -> Any:
    """
    Apply holiday overrides to a target.
    Checks both target-specific overrides and optional global overrides.
    """
    # Combine target and global overrides, with target-specific taking precedence
    overrides = {}
    if isinstance(target, dict):
        # Normalize keys to lowercase for consistent lookup
        overrides = {k.lower(): v for k, v in target.items()}
    
    if global_overrides:
        # Global overrides are applied if no target-specific one exists
        for k, v in global_overrides.items():
            if k.lower() not in overrides:
                overrides[k.lower()] = v

    # Check holidays in priority order (from registry.py)
    for holiday_key in registry.HOLIDAY_PRIORITY:
        # Check for main ramp
        if holiday_ctx.envelope.get(holiday_key, 0.0) > 0.7 and holiday_key in overrides:
            return overrides[holiday_key]
        
        # Check for hangover ramp
        hangover_key = f"{holiday_key}_hangover"
        if holiday_ctx.envelope.get(hangover_key, 0.0) > 0.5 and holiday_key in overrides:
            return overrides[holiday_key]
    
    # No active holiday override found, return the default content from the target dict
    if isinstance(target, dict):
        return target.get("default", target)
    # If target was not a dict, return it as is
    return target

def with_holidays(default: Any, **overrides: Any) -> Dict[str, Any]:
    """
    Shorthand helper for creating holiday override blocks.
    Reduces boilerplate when defining schedules.
    
    Example:
        with_holidays(
            collections.FOX_PRIMETIME,
            halloween=collections.HALLOWEEN_TV_EVENT,
            christmas=collections.CHRISTMAS_TV_EVENT
        )
        
        # Returns:
        {
            "default": collections.FOX_PRIMETIME,
            "halloween": collections.HALLOWEEN_TV_EVENT,
            "christmas": collections.CHRISTMAS_TV_EVENT
        }
    """
    return {"default": default, **overrides}