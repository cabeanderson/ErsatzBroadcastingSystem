# scripts/core/signals.py
# Pure math for calculating signal strength (0.0 to 1.0) over date ranges.

from typing import Dict, Any, Union
from datetime import datetime, date
from . import registry, states
import math

def get_parabolic_surge(days_until: int, window: int) -> float:
    """
    Exponential build-up. Probability stays low and then explodes near the date.
    Best for: Holiday 'hype' (Halloween, Christmas).
    """
    if days_until > window or days_until < 0:
        return 0.0
    if window == 0:
        return 1.0
    progress = (window - days_until) / window
    return float(progress ** 2)

def get_decay_signal(days_since: int, window: int) -> float:
    """
    Fast drop-off. Starts at 1.0 and hits 0.0 quickly.
    Best for: Post-holiday 'Hangover' vibe.
    """
    if days_since == 0:
        return 1.0
    if days_since > window or days_since < 0:
        return 0.0
    # Square root creates a steep drop
    progress = days_since / (window + 1)
    return float(max(0.0, 1 - (progress ** 0.5)))

def get_sigmoid_ramp(days_distance: int, window: int) -> float:
    """
    Smooth S-curve transition using cosine interpolation.
    Starts at 1.0 (dist=0) and eases down to 0.0 (dist=window).
    """
    if days_distance > window or days_distance < 0:
        return 0.0
    if window == 0:
        return 1.0
    return 0.5 * (1 + math.cos(math.pi * days_distance / window))

def get_seasonal_signal_with_plateau(now: Union[datetime, date], season_config: Dict[str, Any]) -> float:
    """
    Calculate seasonal signal with sigmoid ramps + plateau peak.
    
    Timeline:
    - Sigmoid ramp-up (8 weeks)
    - Plateau at 100% (4 weeks)
    - Sigmoid ramp-down (8 weeks)
    
    Args:
        now: Current datetime
        season_config: Dict with peak_start, peak_end, ramp_up_weeks, ramp_down_weeks
    
    Returns:
        0.0-1.0 signal strength
    """
    
    peak_start = season_config["peak_start"]
    peak_end = season_config["peak_end"]
    ramp_up_weeks = season_config["ramp_up_weeks"]
    ramp_down_weeks = season_config["ramp_down_weeks"]
    
    # Check if in peak plateau
    if states.is_in_date_range(now, peak_start[0], peak_start[1], peak_end[0], peak_end[1]):
        return 1.0
    
    # Check if in ramp-up period
    days_to_peak = states.days_until(now, peak_start[0], peak_start[1])
    ramp_up_days = ramp_up_weeks * 7
    
    if 0 <= days_to_peak <= ramp_up_days:
        # Use sigmoid directly (starts at 0 when far, ends at 1 when close)
        return get_sigmoid_ramp(days_to_peak, ramp_up_days)
    
    # Check if in ramp-down period
    days_since_peak = states.days_since(now, peak_end[0], peak_end[1])
    ramp_down_days = ramp_down_weeks * 7
    
    if 0 <= days_since_peak <= ramp_down_days:
        # Use sigmoid (normal - starts at 1, ends at 0)
        return get_sigmoid_ramp(days_since_peak, ramp_down_days)
    
    return 0.0

def get_season_strength(now: Union[datetime, date], season_name: str) -> float:
    """
    Calculate strength of a season with sigmoid ramps + plateau.
    
    Uses new SEASONAL_RAMPS config for plateau-based seasons.
    """
    if season_name not in registry.SEASONAL_RAMPS:
        return 0.0
    
    season_config = registry.SEASONAL_RAMPS[season_name]
    return get_seasonal_signal_with_plateau(now, season_config)
