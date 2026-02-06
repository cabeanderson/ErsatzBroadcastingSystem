# scripts/logic/playback.py
"""
Playback strategies and utilities.
Helpers for time calculations and boundary checks.
"""

from typing import Any
from datetime import timedelta

def hour_in_window(hour: int, start: int, end: int) -> bool:
    """
    Check if a specific hour falls within a start/end window.
    Handles windows that wrap around midnight (e.g. 22 to 6).
    """
    if start < end:
        # Standard window (e.g. 9 to 17)
        return start <= hour < end
    # Wraparound window (e.g. 22 to 6)
    return hour >= start or hour < end


def is_approaching_hour_boundary(context: Any, minutes_threshold: int = 13) -> bool:
    """
    Check if we're close to the next hour boundary.
    
    Used to decide whether to pad remaining time with filler content
    or start the next scheduled block early.
    
    Args:
        context: Current playout context
        minutes_threshold: Minutes before hour to trigger (default 13)
            - 13 minutes = typical for half-hour shows (22 min + ads)
            - Adjust based on content type
    
    Returns:
        True if within threshold minutes of next hour
    
    Example:
        # Current time: 19:50 (10 minutes to 20:00)
        is_approaching_hour_boundary(context, minutes_threshold=13)
        # Returns: True (10 < 13)
    """
    minute = context.current_time.minute
    if minute == 0:
        return False
    
    minutes_until_next_hour = 60 - minute
    return minutes_until_next_hour <= minutes_threshold

def calculate_boundary_dt(context: Any, start_hour: int, end_hour: int) -> Any:
    """
    Calculates the datetime boundary for the end of a time slot.
    Handles standard slots and slots that wrap over midnight.
    
    Args:
        context: Current playout context
        start_hour: Start hour of the slot (0-23)
        end_hour: End hour of the slot (0-24)
    """
    boundary_dt = context.current_time.replace(minute=0, second=0, microsecond=0)
    
    if end_hour == 24:
        boundary_dt = boundary_dt.replace(hour=0) + timedelta(days=1)
    elif end_hour < start_hour:  # Wraps over midnight
        if context.current_time.hour >= start_hour:
            boundary_dt = boundary_dt.replace(hour=end_hour) + timedelta(days=1)
        else:
            boundary_dt = boundary_dt.replace(hour=end_hour)
    else:
        boundary_dt = boundary_dt.replace(hour=end_hour)
        
    return boundary_dt