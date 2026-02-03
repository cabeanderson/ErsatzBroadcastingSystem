from typing import Any, Optional, Tuple
from scripts.playout import play_with_fallback, play_item, ChannelLogger
from datetime import date, timedelta
from scripts.core import states
from scripts.library.structures import AppointmentBlock, SeriesRelay
from scripts.engines.blocks import play_block_intro, play_block_outro

def play_appointment_block(api: Any, build_id: str, context: Any, block: AppointmentBlock, resolver: Any, logger: ChannelLogger, boss: Optional[Any] = None) -> Any:
    """
    Executes an AppointmentBlock by calculating the current show based on date.
    Handles absolute scheduled seasons with optional looping.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        block: AppointmentBlock configuration
        resolver: ContentResolver instance
        logger: ChannelLogger instance
        boss: DayDirector instance (optional)
    """
    result = find_active_season(block, context.current_time.date())

    if result:
        key, count, episode = result
        end_episode = min(episode + block.episodes_per_slot - 1, count)
        ep_str = f"{episode}" if episode == end_episode else f"{episode}-{end_episode}"
        
        logger.info(f"   ▶ Appointment Block: Playing '{key}' (Episode {ep_str}/{count})")
        resolver.resolve(key)
        
        context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
            
        context = play_with_fallback(api, build_id, key, logger, context=context, count=block.episodes_per_slot)
        
        context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
            
        return context

    # No active block found
    if block.off_season_content:
        resolver.resolve(block.off_season_content)
        logger.info(f"   ▶ Appointment Block: Off-season, playing default '{block.off_season_content}'")
        return play_with_fallback(api, build_id, block.off_season_content, logger, context=context)
        
    logger.warn("AppointmentBlock: No active season and no default configured.")
    return context

def find_active_season(block: AppointmentBlock, current_date: date) -> Optional[Tuple[str, int, int]]:
    """
    Find which season is active on current_date, with looping support.
    
    If the block is configured to loop, and the current date is past the last season,
    it calculates a 'virtual date' by projecting the current date back into the 
    first cycle based on the total duration of the block.
    
    Returns:
        (content_key, episode_count, episode_number) or None
    """
    # Build list of all (start_date, end_date, key, count) for each season
    season_windows = []
    for key, count, start_raw in block.seasons:
        start_dt = states.resolve_season_date(start_raw, current_date)
        if not isinstance(start_dt, date):
            continue
            
        # Calculate duration based on slots, not just raw count
        slots_needed = (count + block.episodes_per_slot - 1) // block.episodes_per_slot
        duration = timedelta(days=(slots_needed * 7 if block.frequency == "weekly" else slots_needed))
        end_dt = start_dt + duration
        season_windows.append((start_dt, end_dt, key, count))
    
    if not season_windows:
        return None
        
    # Sort by start date to ensure cycle logic works correctly
    season_windows.sort(key=lambda x: x[0])
    
    # Check if current_date falls in any window
    for start, end, key, count in season_windows:
        if start <= current_date < end:
            # Found it!
            elapsed = (current_date - start).days
            slot_idx = (elapsed // 7) if block.frequency == "weekly" else elapsed
            episode = (slot_idx * block.episodes_per_slot) + 1
            return (key, count, episode)
    
    # Not in any window - check if we should loop
    if not block.loop:
        return None
    
    # Find cycle length and offset
    first_start = season_windows[0][0]
    last_end = season_windows[-1][1]
    cycle_length = (last_end - first_start).days
    
    # Are we past the end?
    if cycle_length > 0 and current_date >= last_end:
        # Calculate offset into the repeating cycle
        days_past_end = (current_date - last_end).days
        offset = days_past_end % cycle_length
        virtual_date = first_start + timedelta(days=offset)
        
        # Recursively check which season the virtual date is in
        # (but don't loop again - just check the original windows)
        for start, end, key, count in season_windows:
            if start <= virtual_date < end:
                elapsed = (virtual_date - start).days
                slot_idx = (elapsed // 7) if block.frequency == "weekly" else elapsed
                episode = (slot_idx * block.episodes_per_slot) + 1
                return (key, count, episode)
    
    return None

def play_series_relay(api: Any, build_id: str, context: Any, block: SeriesRelay, resolver: Any, logger: ChannelLogger, boss: Optional[Any] = None) -> Any:
    """
    Executes a SeriesRelay by calculating the current show based on a relative start date.
    
    Unlike AppointmentBlock which uses absolute dates, SeriesRelay starts counting
    weeks from a single start_date (e.g. "WINTER"). It loops automatically when
    the sequence finishes.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        block: SeriesRelay configuration
        resolver: ContentResolver instance
        logger: ChannelLogger instance
        boss: DayDirector instance (optional)
        
    Returns:
        Updated PlayoutContext.
    """
    current_date = context.current_time.date()
    # 1. Calculate slots elapsed since start
    start_date = states.resolve_season_date(block.start_date, current_date)

    if not isinstance(start_date, date):
        logger.warn("SeriesRelay missing a valid start_date.")
        return context

    delta = (current_date - start_date).days
    
    if delta < 0:
        logger.warn(f"SeriesRelay starts in future ({start_date}). Playing first item.")
        delta = 0

    if block.frequency == "weekly":
        slot_index = delta // 7
    else: # daily
        slot_index = delta

    # 2. Handle Looping
    # Calculate total slots accounting for episodes_per_slot
    total_slots = sum((count + block.episodes_per_slot - 1) // block.episodes_per_slot for _, count in block.items)
    if total_slots == 0:
        logger.warn("SeriesRelay has no items/counts.")
        return context
        
    current_slot = slot_index % total_slots
    
    # 3. Find which show corresponds to this slot index
    current_show = None
    accumulated_slots = 0
    
    for key, count in block.items:
        slots_for_show = (count + block.episodes_per_slot - 1) // block.episodes_per_slot
        if current_slot < accumulated_slots + slots_for_show:
            current_show = key
            break
        accumulated_slots += slots_for_show
    
    # 4. Play it
    resolver.resolve(current_show)
    logger.info(f"   ▶ Series Relay: Playing '{current_show}' (Progress: {current_slot + 1}/{total_slots})")
    
    context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
    
    context = play_with_fallback(api, build_id, current_show, logger, context=context, count=block.episodes_per_slot)
    
    context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
    
    return context