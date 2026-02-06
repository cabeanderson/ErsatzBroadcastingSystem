# scripts/logic/triggers.py
"""
Factory functions for schedule triggers.
Simplifies marathon and event definitions in channel configs.
"""

from scripts.core import states

def chance(probability, key="default"):
    """
    Random roll with probability (0.0 - 1.0).
    Example: triggers.chance(0.05, "simpsons_marathon")
    """
    return lambda boss: boss.roll(probability, key)

def on_date(month, day):
    """
    True on a specific date.
    Example: triggers.on_date(12, 25)
    """
    return lambda boss: boss.now.month == month and boss.now.day == day

def in_range(start_month, start_day, end_month, end_day):
    """
    True within a date range (inclusive).
    Example: triggers.in_range(10, 1, 10, 31)
    """
    return lambda boss: states.is_in_date_range(boss.now, start_month, start_day, end_month, end_day)

def has_label(label):
    """
    True if the day has a specific label.
    Example: triggers.has_label("FRIDAY_THE_13TH")
    """
    return lambda boss: boss.has(label)