"""
Playback strategies and utilities.
Handles complex scheduling behaviors like single-play slots and gap filling.
"""

from datetime import timedelta
from typing import Any, List, Tuple, Optional, Dict, Callable
from scripts.playout import play_item, fill_until_time, ChannelLogger, circuit_breaker, play_with_fallback
from scripts.logic.resolution import resolve_target
from scripts.logic.models import BrandedBlock, Fallback, PlayOnce, CommercialBreak
from scripts.library.structures import AppointmentBlock, SeriesRelay
from scripts.engines.sequential import play_appointment_block, play_series_relay


def select_content_by_time(remaining_minutes: int, content_options: List[Tuple[str, int]], resolver: Any, prefer_exact: bool = True) -> Optional[str]:
    """
    Select appropriate content based on time remaining in slot.
    
    Args:
        remaining_minutes: Minutes left in current time slot
        content_options: List of (content_key, duration_minutes) tuples
        resolver: ContentResolver instance
        prefer_exact: If True, prefer content that fills time exactly
    
    Returns:
        Best content_key for the remaining time
    """
    if not content_options:
        return None
    
    # Sort by how well they fit the time
    def time_fit_score(option):
        content_key, duration = option
        
        if duration > remaining_minutes:
            # Too long - penalize
            return -1000 + duration
        
        if prefer_exact and duration == remaining_minutes:
            # Perfect fit!
            return 10000
        
        # Score based on how close to filling the time
        # Prefer content that leaves less dead air
        unused_time = remaining_minutes - duration
        return -unused_time  # Negative so smaller unused = higher score
    
    sorted_options = sorted(content_options, key=time_fit_score, reverse=True)
    best_content, _ = sorted_options[0]
    
    return best_content


def handle_single_play_slot(api: Any, build_id: str, context: Any, current_slot_tuple: Tuple[int, int], day_schedule: Dict[Tuple[int, int], Any], boss: Any, holiday_ctx: Any, config: Any, resolver: Any, logger: ChannelLogger) -> Any:
    """
    Handles a single-play slot: plays one item, then fills the rest of the slot
    with content from the *next* scheduled block.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        current_slot_tuple: (start_hour, end_hour) tuple
        day_schedule: Full day schedule dict
        boss: DayDirector instance
        holiday_ctx: HolidayContext instance
        config: ScheduleConfig instance
        logger: ChannelLogger instance
        resolver: ContentResolver instance
    
    Returns:
        Updated context after filling slot
    """
    start, end = current_slot_tuple
    
    # Calculate boundary datetime for the end of this slot
    boundary_dt = context.current_time.replace(minute=0, second=0, microsecond=0)
    
    if end == 24:
        boundary_dt = boundary_dt.replace(hour=0) + timedelta(days=1)
    elif end < start:  # Wraps over midnight
        if context.current_time.hour >= start:
            boundary_dt = boundary_dt.replace(hour=end) + timedelta(days=1)
        else:
            boundary_dt = boundary_dt.replace(hour=end)
    else:
        boundary_dt = boundary_dt.replace(hour=end)
    
    last_time = context.current_time
    # Loop to fill remaining time with NEXT block content
    while context.current_time < boundary_dt:
        # Find next slot
        next_slot_entry = None
        lookup_start = 0 if end == 24 else end
        
        # Sort slots to ensure deterministic lookup
        for (s, e), entry in sorted(day_schedule.items()):
            if s == lookup_start:
                next_slot_entry = entry
                break
        
        if next_slot_entry:
            try:
                logger.info(f"  Starting next block early to fill gap")
                
                # Handle BrandedBlock in fallthrough (unwrap to content)
                target_for_resolution = next_slot_entry
                if isinstance(target_for_resolution, BrandedBlock):
                    target_for_resolution = target_for_resolution.content
                
                next_result = resolve_target(target_for_resolution, boss, holiday_ctx, config, resolver, logger)
                next_key = next_result.resolved_content
                
                # If resolved content is None, check for a wrapper
                if next_key is None and next_result.wrapper:
                    next_key = next_result.wrapper
                
                # Unwrap wrappers for simple playback
                if isinstance(next_key, BrandedBlock):
                    # If filling a gap into a BrandedBlock, just play its content (skip intro/branding)
                    inner_res = resolve_target(next_key.content, boss, holiday_ctx, config, resolver, logger)
                    next_key = inner_res.resolved_content

                if isinstance(next_key, PlayOnce):
                    # If we resolved to a PlayOnce, just take its content (we are already playing once)
                    # We might need to resolve the inner content if it's not a string yet
                    inner_res = resolve_target(next_key.content, boss, holiday_ctx, config, resolver, logger)
                    next_key = inner_res.resolved_content

                if isinstance(next_key, CommercialBreak):
                    # If filling gap into a CommercialBreak, resolve its content
                    inner_res = resolve_target(next_key.content, boss, holiday_ctx, config, resolver, logger)
                    next_key = inner_res.resolved_content

                if isinstance(next_key, AppointmentBlock):
                    context = play_appointment_block(api, build_id, context, next_key, resolver, logger, boss=boss)
                    next_key = None # Handled by engine
                
                if isinstance(next_key, SeriesRelay):
                    context = play_series_relay(api, build_id, context, next_key, resolver, logger, boss=boss)
                    next_key = None # Handled by engine

                if next_key:
                    context = play_with_fallback(api, build_id, next_key, logger, context=context)
                else:
                    # Resolution failed, try filler
                    raise ValueError("Content resolution returned None")
                    
            except Exception as e:
                logger.warn(f"  ⚠️ Error resolving next block: {e}")
                # Fall through to filler logic
                next_slot_entry = None
        
        if not next_slot_entry:
            # No next slot found, use filler/wait
            target_hour = end if end != 24 else 0
            target_time_str = f"{target_hour:02d}:00"
            is_tomorrow = (end < start) or (end == 24)
            
            filler_key = None
            if config.filler_content:
                try:
                    filler_result = resolve_target(config.filler_content, boss, holiday_ctx, config, resolver, logger)
                    filler_key = filler_result.resolved_content
                    if isinstance(filler_key, Fallback):
                        filler_key = filler_key.primary
                except Exception as e:
                    logger.warn(f"  ⚠️ Filler content unavailable: {e}")
            
            if filler_key:
                logger.info(f"  Single play complete. Filling until {target_time_str}")
            else:
                logger.info(f"  Single play complete. Waiting until {target_time_str}")
            
            context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key, tomorrow=is_tomorrow)
            break  # We filled to boundary
        
        # Circuit Breaker: Prevent infinite loops if content fails to advance time
        if context.current_time <= last_time:
            fallback_key = None
            if config.fallback_content:
                try:
                    # Resolve fallback content
                    fb_res = resolve_target(config.fallback_content, boss, holiday_ctx, config, resolver, logger)
                    content = fb_res.resolved_content
                    
                    # Unwrap Fallback object if present (use primary)
                    if isinstance(content, Fallback):
                        content = content.primary
                    if isinstance(content, str):
                        fallback_key = content
                except Exception as e:
                    logger.warn(f"Failed to resolve fallback content: {e}")
            
            context = circuit_breaker(api, build_id, context, last_time, logger, fallback_content=fallback_key)

        if context.current_time <= last_time:
            break # Circuit breaker failed or skipped, break loop to return control to main schedule
        last_time = context.current_time
            
    return context


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


def fill_until_next_hour(api: Any, build_id: str, context: Any, logger: ChannelLogger, filler_key: str) -> Any:
    """
    Convenience wrapper - pads to next hour boundary.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        logger: ChannelLogger instance
        filler_key: Content key for filler content
    
    Returns:
        Updated context after padding to next hour
    """
    next_hour = (context.current_time.hour + 1) % 24
    tomorrow = (next_hour == 0)
    return fill_until_time(api, build_id, context, logger, f"{next_hour:02d}:00", filler_key, tomorrow=tomorrow)