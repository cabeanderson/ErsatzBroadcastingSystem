# scripts/logic/timeslots.py
"""
Standard broadcast time slots and time calculation helpers.
"""

DEFAULT_TIMESLOTS = {
    "overnight": (2, 6),
    "early": (6, 8),
    "morning": (8, 10),
    "midday": (10, 12),
    "noon": (12, 14),
    "afternoon": (14, 17),
    "evening": (17, 20),
    "prime": (20, 23),
    "night": (23, 2),
}

ALT_TIMESLOTS = {
    "movies": {
        "overnight": (0, 6),
        "morning": (6, 12),
        "afternoon": (12, 18),
        "prime": (18, 24),
    },
}

def hour_in_window(hour, start, end):
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end

def get_timeslot_map(timeslot_preset="default", custom_timeslots=None):
    """Resolves the final timeslot dictionary from presets and custom overrides."""
    if isinstance(timeslot_preset, dict):
        timeslots = timeslot_preset
    elif timeslot_preset in ALT_TIMESLOTS:
        timeslots = ALT_TIMESLOTS[timeslot_preset]
    else:
        timeslots = DEFAULT_TIMESLOTS

    if custom_timeslots:
        timeslots = {**timeslots, **custom_timeslots}
    
    return timeslots

def expand_timeslots(schedule, timeslot_preset="default", custom_timeslots=None):
    timeslots = get_timeslot_map(timeslot_preset, custom_timeslots)   
    expanded = {}
    for key, value in schedule.items():
        if isinstance(key, str):
            if key not in timeslots:
                raise ValueError(f"Unknown timeslot '{key}'")
            expanded[timeslots[key]] = value
        else:
            expanded[key] = value

    return expanded