# scripts/calendar/holidays.py
"""
Holiday detection and override system.
Provides both signal strengths and boolean flags for holiday programming.
"""

from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.core import registry
from scripts.logic.models import Fallback, ResolutionResult
from scripts.config import ENABLE_HOLIDAY_INJECTION

if TYPE_CHECKING:
    from scripts.logic.resolver import ContentResolver
    from scripts.core import DayDirector
    from scripts.playout import ChannelLogger

class HolidayContext:
    """
    Captures the current holiday state for easy querying.
    Provides both signal strengths (0.0-1.0) and boolean flags.
    """
    
    def __init__(self, boss: Any):
        self.boss: Any = boss
        self.envelope: Dict[str, float] = {
            "halloween": boss.signal("HALLOWEEN", window=14),
            "halloween_hangover": boss.signal("HALLOWEEN", window=1, hangover=True),
            "christmas": boss.signal("CHRISTMAS", window=30),
            "christmas_hangover": boss.signal("CHRISTMAS", window=3, hangover=True),
            "thanksgiving": boss.signal("THANKSGIVING", window=7),
            "new_years": boss.signal("NEW_YEARS_EVE", window=3),
            "new_years_hangover": boss.signal("NEW_YEARS_DAY", window=1), # Jan 1 is the hangover
            "valentines": boss.signal("VALENTINES_DAY", window=7),
            "st_patricks": boss.signal("ST_PATRICKS_DAY", window=5),
            "star_wars": boss.signal("STAR_WARS_DAY", window=2),
            "july_4": boss.signal("JULY_4", window=5),
        }
        
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
    # If target is not a dict, check global overrides only
    if not isinstance(target, dict):
        if global_overrides:
            # Check holidays in priority order (Christmas > Halloween > Others)
            for holiday in ["christmas", "halloween", "thanksgiving", "valentines"]:
                if holiday in global_overrides and holiday_ctx.is_active(holiday):
                    return global_overrides[holiday]
        return target
    
    # Target is a dict - check target-specific overrides first
    # Priority order: Christmas > Christmas Hangover > Halloween > Thanksgiving > Default
    
    # Christmas (highest priority)
    tgt = target.get("christmas") or target.get("CHRISTMAS")
    if tgt:
        if (holiday_ctx.is_active("christmas") or 
            holiday_ctx.is_active("christmas_hangover", threshold=0.5)):
            return tgt
    
    # New Year's (High priority, overlaps with Christmas hangover)
    tgt = target.get("new_years") or target.get("NEW_YEARS_EVE") or target.get("NEW_YEARS_DAY")
    if tgt and (holiday_ctx.is_active("new_years") or 
                holiday_ctx.is_active("new_years_hangover", threshold=0.5)):
        return tgt

    # Halloween
    tgt = target.get("halloween") or target.get("HALLOWEEN")
    if tgt and holiday_ctx.is_active("halloween"):
        return tgt
    
    # Thanksgiving
    tgt = target.get("thanksgiving") or target.get("THANKSGIVING")
    if tgt and holiday_ctx.is_active("thanksgiving"):
        return tgt
    
    # Other holidays
    tgt = target.get("valentines") or target.get("VALENTINES_DAY")
    if tgt and holiday_ctx.is_active("valentines"):
        return tgt
    
    tgt = target.get("st_patricks") or target.get("ST_PATRICKS_DAY")
    if tgt and holiday_ctx.is_active("st_patricks"):
        return tgt

    tgt = target.get("star_wars") or target.get("STAR_WARS_DAY")
    if tgt and holiday_ctx.is_active("star_wars"):
        return tgt

    tgt = target.get("july_4") or target.get("JULY_4")
    if tgt and holiday_ctx.is_active("july_4"):
        return tgt
    
    # No holiday active or no override defined
    return target.get("default", target)

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

def apply_holiday_injection(final_key: Any, resolver: 'ContentResolver', holiday_ctx: HolidayContext, boss: 'DayDirector', logger: 'ChannelLogger', source: str = "schedule") -> ResolutionResult:
    """Check if any major holiday is active and try to inject a tagged variant."""
    if isinstance(final_key, str) and ENABLE_HOLIDAY_INJECTION:
        active_tag = None
        
        for holiday in registry.HOLIDAY_PRIORITY:
            strength = holiday_ctx.envelope.get(holiday, 0.0)
            # Roll based on signal strength (e.g. 0.1 signal = 10% chance)
            if strength > 0.01 and boss.roll(strength, key=f"inject_{holiday}_{final_key}"):
                active_tag = holiday
                break
            
        if active_tag:
            # Get original query to see if we can modify it
            data = resolver.get_query_data(final_key)
            
            base_query = None
            order = "Shuffle"
            if isinstance(data, dict):
                base_query = data.get("query")
                order = data.get("order", "Shuffle")
            elif isinstance(data, str):
                base_query = data
                
            # Only inject if it's a valid query and not already tagged
            if base_query and f"tag:{active_tag}" not in base_query:
                holiday_key = f"{final_key}_auto_{active_tag}"
                holiday_query = f"({base_query}) AND tag:{active_tag}"
                resolver.register_dynamic_query(holiday_key, holiday_query, order)
                return ResolutionResult(wrapper=Fallback(primary=holiday_key, secondary=final_key), source="injection")

    return ResolutionResult(key=final_key, source=source)