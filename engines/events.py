# scripts/engines/events.py
"""
Multi-day event system for themed programming weeks.
Handles Shark Week, 13 Days of Halloween, 25 Days of Christmas, etc.
"""

from datetime import timedelta
from scripts.logic.models import MultiDayEvent


def get_active_events(events, boss):
    """
    Check which events are currently active.
    
    Args:
        events: List of MultiDayEvent instances
        boss: DayDirector instance
    
    Returns:
        List of active events, sorted by priority (highest first)
    """
    active = []
    
    for event in events:
        if event.trigger(boss):
            # Check if we're within duration
            # (Simple version - just checks trigger is True)
            # Could be enhanced to track start dates
            active.append(event)
    
    # Sort by priority (highest first)
    return sorted(active, key=lambda e: e.priority, reverse=True)


def apply_event_overrides(target, slot_name, boss, events):
    """
    Apply event overrides to a schedule target.
    
    Args:
        target: Original schedule target
        slot_name: Name of current timeslot (e.g., "prime")
        boss: DayDirector instance
        events: List of MultiDayEvent instances
    
    Returns:
        Overridden target if event is active, else original target
    """
    active_events = get_active_events(events, boss)
    
    for event in active_events:
        # Check if event affects this timeslot
        if not event.timeslots or slot_name in event.timeslots:
            return event.content
    
    return target