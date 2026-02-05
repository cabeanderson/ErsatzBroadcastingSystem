"""
Logic for date-based sequential scheduling (Appointment TV).
"""

from datetime import date, timedelta
from typing import Optional, Tuple, List, Dict, Any

from scripts.core import registry, states
from scripts.logic.structures import AppointmentBlock


def find_active_season(block: AppointmentBlock, current_date: date) -> Optional[Tuple[str, int, int]]:
    """
    Find which season is active on current_date, with looping support.
    
    Returns:
        (content_key, episode_count, episode_number) or None
    """
    # Build list of all (start_date, end_date, key, count) for each season
    season_windows: List[Tuple[date, date, str, int]] = []
    for key, count, start_raw in block.seasons:
        start_dt: Optional[date] = states.resolve_season_date(start_raw, current_date)
        if not isinstance(start_dt, date):
            continue
            
        # Calculate duration based on slots, not just raw count
        slots_needed: int = (count + block.episodes_per_slot - 1) // block.episodes_per_slot
        duration: timedelta = timedelta(days=(slots_needed * 7 if block.frequency == "weekly" else slots_needed))
        end_dt: date = start_dt + duration
        season_windows.append((start_dt, end_dt, key, count))
    
    if not season_windows:
        return None
        
    # Sort by start date to ensure correct processing
    season_windows.sort(key=lambda x: x[0])
    
    # --- LOOPING LOGIC ---
    first_start_date: date = season_windows[0][0]
    last_end_date: date = season_windows[-1][1]

    if block.loop and current_date >= last_end_date:
        if block.loop_restart_season and isinstance(block.loop_restart_season, str):
            season_config: Optional[Dict[str, Any]] = registry.SEASONAL_RAMPS.get(block.loop_restart_season.upper())
            
            if season_config:
                restart_month, restart_day = season_config["peak_start"]
                next_restart_year: int = last_end_date.year
                first_restart_date: date = date(next_restart_year, restart_month, restart_day)
                
                if first_restart_date < last_end_date:
                    first_restart_date = date(next_restart_year + 1, restart_month, restart_day)
                
                cycle_length: timedelta = first_restart_date - first_start_date
                if cycle_length.days <= 0: return None # Avoid division by zero

                total_elapsed: timedelta = current_date - first_start_date
                days_into_cycle: int = total_elapsed.days % cycle_length.days
                virtual_date: date = first_start_date + timedelta(days=days_into_cycle)
                
                if virtual_date >= last_end_date:
                    return None
                current_date = virtual_date
        else: # Immediate loop
            cycle_length_days: int = (last_end_date - first_start_date).days
            if cycle_length_days <= 0: return None # Avoid division by zero

            days_past_end: int = (current_date - last_end_date).days
            days_into_cycle: int = days_past_end % cycle_length_days
            current_date = first_start_date + timedelta(days=days_into_cycle)

    for start, end, key, count in season_windows:
        if start <= current_date < end:
            elapsed: int = (current_date - start).days
            slot_idx: int = (elapsed // 7) if block.frequency == "weekly" else elapsed
            episode: int = (slot_idx * block.episodes_per_slot) + 1
            return (key, count, episode)
    
    return None