# scripts/core/states.py
"""
Temporal state derivation and date range calculations.
"""

from datetime import date, datetime, timedelta
import calendar
from typing import Tuple, Optional, Dict, Any, Union, Set
from . import registry


def get_season_transition(month: int) -> Tuple[str, str]:
    """Returns the current and next season for a given month."""
    if 12 == month or month <= 2: return "WINTER", "SPRING"
    elif 3 <= month <= 5:      return "SPRING", "SUMMER"
    elif 6 <= month <= 8:      return "SUMMER", "FALL"
    else:                      return "FALL",   "WINTER"


def is_nth_weekday(dt: Union[datetime, date], weekday: int, n: int) -> bool:
    """Check if today is the Nth occurrence of a weekday in the month."""
    return dt.weekday() == weekday and (dt.day - 1) // 7 + 1 == n


def is_last_weekday(dt: Union[datetime, date], weekday: int) -> bool:
    """Check if today is the absolute last occurrence of a weekday in the month."""
    return dt.weekday() == weekday and (dt + timedelta(days=7)).month != dt.month

def get_floating_date(year: int, rule: Dict[str, Any]) -> Optional[date]:
    """Calculate the specific date for a floating rule in a given year."""
    month = rule.get("month")
    if not month: return None # Can't calculate without month (e.g. Friday 13th)
    
    c = calendar.monthcalendar(year, month)
    weekday = rule["weekday"]
    occurrence = rule["occurrence"]
    
    # Get all dates for this weekday in the month
    dates = [week[weekday] for week in c if week[weekday] != 0]
    
    if occurrence == "last":
        day = dates[-1]
    elif isinstance(occurrence, int):
        if occurrence > len(dates): return None
        day = dates[occurrence - 1]
    else:
        return None
        
    return date(year, month, day)

def is_in_date_range(dt: Union[datetime, date], start_month: int, start_day: int, end_month: int, end_day: int) -> bool:
    """
    Check if datetime is within a date range, handling year wraparound.
    Example: (12, 15, 1, 15) for Mid-Dec to Mid-Jan.
    """
    dt_date = dt.date() if hasattr(dt, 'date') else dt
    
    try:
        start_date = date(dt_date.year, start_month, start_day)
        end_date = date(dt_date.year, end_month, end_day)
    except ValueError:
        return False
    
    if start_date <= end_date:
        # Standard range (e.g., June 15 to July 15)
        return start_date <= dt_date <= end_date
    else:
        # Wraps year (e.g., Dec 15 to Jan 15)
        return dt_date >= start_date or dt_date <= end_date


def days_until(dt: Union[datetime, date], target_month: int, target_day: int) -> int:
    """Calculate days until the next occurrence of a target date."""
    dt_date = dt.date() if isinstance(dt, (datetime, date)) else dt
    target = date(dt_date.year, target_month, target_day)
    if target < dt_date:
        target = target.replace(year=dt_date.year + 1)
    return (target - dt_date).days


def days_since(dt: Union[datetime, date], target_month: int, target_day: int) -> int:
    """Calculate days elapsed since the most recent occurrence."""
    dt_date = dt.date() if isinstance(dt, (datetime, date)) else dt
    target = date(dt_date.year, target_month, target_day)
    if dt_date < target:
        target = target.replace(year=dt_date.year - 1)
    return (dt_date - target).days

def in_window(dt: Union[datetime, date], event_month: int, event_day: int, before: int = 0, after: int = 0) -> bool:
    """
    Check if datetime is within a window around an event date.
    Handles year wraparound for events like New Year's.
    """
    dt_date = dt.date() if hasattr(dt, 'date') else dt
    
    # Create event date for current year
    try:
        event_this_year = date(dt_date.year, event_month, event_day)
    except ValueError: # Handle cases like Feb 29 on non-leap year
        return False

    # Calculate start and end of the window
    window_start = event_this_year - timedelta(days=before)
    window_end = event_this_year + timedelta(days=after)

    if window_start <= dt_date <= window_end:
        return True

    # Also check for events that might wrap around the year
    # e.g., an event in late Dec, and the window extends into Jan of next year
    try:
        event_next_year = date(dt_date.year + 1, event_month, event_day)
        window_start_next = event_next_year - timedelta(days=before)
        window_end_next = event_next_year + timedelta(days=after)
        if window_start_next <= dt_date <= window_end_next:
            return True
    except ValueError:
        pass # Ignore if date is invalid (e.g. Feb 29)

    return False

def derive_labels(dt: datetime) -> Set[str]:
    """Derives a set of categorical strings for the given datetime."""
    m, d, w, h = dt.month, dt.day, dt.weekday(), dt.hour
    weekday_name = dt.strftime('%A').upper()
    
    labels = {weekday_name}

    # 1. Weekday Grouping
    if w >= 5:
        labels.add("WEEKEND")
    else:
        labels.add("WEEKDAY")
        for label, days in registry.WEEKDAY_GROUPS.items():
            if w in days:
                labels.add(label)
                break

    # 2. Seasons (Meteorological)
    for season, months in registry.SEASONS.items():
        if m in months:
            labels.add(season)
            break
            
    # 3. Seasonal Periods (Broadcasting Peaks)
    for season, config in registry.SEASONAL_RAMPS.items():
        peak_start = config["peak_start"]
        peak_end = config["peak_end"]
        if is_in_date_range(dt, peak_start[0], peak_start[1], peak_end[0], peak_end[1]):
            labels.add(f"{season}_PEAK")

    # 4. Dayparts
    for (start, end), name in registry.DAYPARTS.items():
        if start > end:  # Wraps midnight
            if h >= start or h < end:
                labels.add(name)
        elif start <= h < end:
            labels.add(name)

    # 5. Static Holidays
    if (m, d) in registry.HOLIDAYS:
        labels.add(registry.HOLIDAYS[(m, d)])

    # 6. Semantic Floating Holidays
    for rule in registry.FLOATING_RULES:
        if rule.get("month") and m != rule["month"]:
            continue

        if "day" in rule:
            if d == rule["day"] and w == rule["weekday"]:
                labels.add(rule["name"])
        elif "occurrence" in rule:
            occ = rule["occurrence"]
            if (occ == "last" and is_last_weekday(dt, rule["weekday"])) or \
               (isinstance(occ, int) and is_nth_weekday(dt, rule["weekday"], occ)):
                labels.add(rule["name"])

    # 7. Positional Label (e.g., FIRST_MONDAY)
    nth = (d - 1) // 7 + 1
    occ_names = ["FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"]
    labels.add(f"{occ_names[nth - 1]}_{weekday_name}")

    return labels

def resolve_season_date(value: Union[date, tuple, str], current_date: Optional[date] = None) -> Optional[date]:
    """
    Resolves a date from a date object, (Year, Season) tuple, or Season string.
    
    Args:
        value: The input to resolve.
        current_date: Reference date for relative season strings (e.g. "WINTER").
    
    Returns:
        Resolved date object, or None if resolution fails.
    """
    if isinstance(value, date):
        return value
        
    # Handle (Year, Season) tuple: (2026, "FALL")
    if isinstance(value, tuple) and len(value) == 2:
        year, season = value
        if isinstance(year, int) and isinstance(season, str):
            season = season.upper()
            if season in registry.SEASONAL_RAMPS:
                month, day = registry.SEASONAL_RAMPS[season]["peak_start"]
                return date(year, month, day)

    # Handle bare season string: "WINTER"
    if isinstance(value, str) and current_date:
        season = value.upper()
        if season in registry.SEASONAL_RAMPS:
            month, day = registry.SEASONAL_RAMPS[season]["peak_start"]
            current_year = current_date.year
            season_start_this_year = date(current_year, month, day)
            
            # If today is Jan 2026, and Winter starts Dec 15, we want Dec 2025
            if season_start_this_year > current_date:
                return date(current_year - 1, month, day)
            else:
                return season_start_this_year
                
    return None
