# scripts/engines/slots.py
"""
Engine for handling specific slot behaviors, such as Single Play slots
that require filling the remainder of the hour with the next block's content.
"""

from datetime import timedelta
from typing import Any, Dict, Tuple, Optional
from scripts.core.logger import ChannelLogger
from scripts.playout import fill_until_time, circuit_breaker, play_with_fallback
from scripts.logic.resolution import resolve_target
from scripts.logic.models import Fallback, PlayOnce, CommercialBreak
from scripts.logic.structures import Block, Program
from scripts.logic.playback import calculate_boundary_dt


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
    boundary_dt = calculate_boundary_dt(context, start, end)
    
    # Find next slot (once)
    next_slot_entry = None
    lookup_start = 0 if end == 24 else end
    
    # Sort slots to ensure deterministic lookup
    for (s, e), entry in sorted(day_schedule.items()):
        if s == lookup_start:
            next_slot_entry = entry
            break

    last_time = context.current_time
    # Loop to fill remaining time with NEXT block content
    while context.current_time < boundary_dt:
        if next_slot_entry:
            try:
                logger.info(f"  Starting next block early to fill gap")
                
                # Handle Block/Program in fallthrough
                target_for_resolution = next_slot_entry
                if isinstance(target_for_resolution, Block):
                    # If it's a block, try to grab the first item or just use the block itself?
                    # For gap filling, we usually want the *content*.
                    # If Block has items, pick one?
                    # Simplest approach: Treat Block as a collection source if possible, or unwrap.
                    if target_for_resolution.items:
                        target_for_resolution = target_for_resolution.items
                
                next_result = resolve_target(target_for_resolution, boss, holiday_ctx, config, resolver, logger)
                next_key = next_result.resolved_content
                
                # If resolved content is None, check for a wrapper
                if next_key is None and next_result.wrapper:
                    next_key = next_result.wrapper
                
                # Unwrap wrappers for simple playback
                if isinstance(next_key, Block):
                    # Attempt to extract content from the Block to fill the gap
                    if next_key.items:
                        # If items is a collection (has pick), use it
                        if hasattr(next_key.items, 'pick'):
                            next_key = next_key.items.pick(boss)
                        # If items is a list, pick the first one (or random?)
                        elif isinstance(next_key.items, list) and len(next_key.items) > 0:
                            next_key = next_key.items[0]

                if isinstance(next_key, PlayOnce):
                    # If we resolved to a PlayOnce, just take its content (we are already playing once)
                    # We might need to resolve the inner content if it's not a string yet
                    inner_res = resolve_target(next_key.content, boss, holiday_ctx, config, resolver, logger)
                    next_key = inner_res.resolved_content

                if isinstance(next_key, CommercialBreak):
                    # If filling gap into a CommercialBreak, resolve its content
                    inner_res = resolve_target(next_key.content, boss, holiday_ctx, config, resolver, logger)
                    next_key = inner_res.resolved_content

                if isinstance(next_key, Program):
                    # Programs are complex; for gap filling, we might just want their content
                    next_key = next_key.content

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
                logger.error("Gap fill failed: circuit breaker couldn't advance time")
                break # Circuit breaker failed or skipped, break loop to return control to main schedule
        
        last_time = context.current_time
            
    return context