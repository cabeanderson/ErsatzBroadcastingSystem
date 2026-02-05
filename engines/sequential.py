from typing import Any, Optional, Tuple, Dict, Union
from datetime import date, timedelta

from etv_client.models import ControlSkipToItem
from scripts.core import states
from scripts.logic.structures import AppointmentBlock, SeriesRelay, AppointmentLineup
from scripts.engines.blocks import play_block_intro, play_block_outro
from scripts.logic.resolution import resolve_target
from scripts.logic.queries import extract_episode_range, extract_title_from_query
from scripts.core.logger import ChannelLogger
from scripts.playout import play_with_fallback, play_item, fill_until_time, play_smart_bumper
from scripts.logic.sequencing import find_active_season

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
    # Register any auto-generated queries carried by the block
    if block.generated_queries:
        for key, query in block.generated_queries.items():
            resolver.register_dynamic_query(key, query, order="Chronological")

    result = find_active_season(block, context.current_time.date())

    if result:
        key, count, episode = result
        end_episode = min(episode + block.episodes_per_slot - 1, count)
        ep_str = f"{episode}" if episode == end_episode else f"{episode}-{end_episode}"
        
        logger.info(f"   ▶ Appointment Block: Playing '{key}' (Episode {ep_str}/{count})")
        resolver.resolve(key)
        
        # EXPLICIT SEQUENCING: Force the exact episode if possible
        # This fixes issues where ErsatzTV skips episodes in a collection
        query = None
        try:
            # Get the query for the key to extract season number
            query_data = resolver.get_query_data(key)
            query = query_data.get("query") if isinstance(query_data, dict) else query_data
            
            if query:
                q_season, _ = extract_episode_range(query)
                if q_season is not None:
                    # Force pointer to this specific episode
                    api.skip_to_item(build_id, ControlSkipToItem(content=key, season=q_season, episode=episode))
        except Exception as e:
            logger.warn(f"Failed to force sequence for '{key}': {e}")

        context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
        
        # Smart Bumper
        if query:
            title = extract_title_from_query(query)
            context, _ = play_smart_bumper(api, build_id, context, title, resolver, logger, required_tags=["bumpers"])
            
        context = play_with_fallback(api, build_id, key, logger, context=context, count=block.episodes_per_slot)
        
        context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
            
        return context

    # No active block found
    off_season_target = block.off_season_content

    if not off_season_target:
        logger.warn("AppointmentBlock: No active season and no default configured.")
        return context

    # Handle complex off-season objects by delegating to their respective engines
    if isinstance(off_season_target, SeriesRelay):
        logger.info("   ▶ Appointment Block: Off-season, delegating to SeriesRelay filler.")
        return play_series_relay(api, build_id, context, off_season_target, resolver, logger, boss)

    # Handle simple string or dictionary fallbacks
    off_season_key = None
    if isinstance(off_season_target, dict):
        # Smart off-season dictionary
        if boss:
            season_key = boss.season_vibe.upper()
            off_season_key = off_season_target.get(season_key, off_season_target.get("default"))
        else:
            # Fallback if boss is not available
            off_season_key = off_season_target.get("default")
    elif isinstance(off_season_target, str):
        # Simple string fallback
        off_season_key = off_season_target

    if off_season_key:
        resolver.resolve(off_season_key)
        logger.info(f"   ▶ Appointment Block: Off-season, playing fallback '{off_season_key}'")
        return play_with_fallback(api, build_id, off_season_key, logger, context=context)

    logger.warn(f"AppointmentBlock: Unsupported off_season_content type: {type(off_season_target)}")
    return context

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
    resolved_key = resolver.resolve(current_show)
    logger.info(f"   ▶ Series Relay: Playing '{resolved_key}' (Progress: {current_slot + 1}/{total_slots})")
    
    context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
    
    # Smart Bumper
    query_data = resolver.get_query_data(resolved_key)
    query = query_data.get("query") if isinstance(query_data, dict) else query_data
    if query:
        title = extract_title_from_query(query)
        context, _ = play_smart_bumper(api, build_id, context, title, resolver, logger, required_tags=["bumpers"])
    
    context = play_with_fallback(api, build_id, resolved_key, logger, context=context, count=block.episodes_per_slot)
    
    context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
    
    return context

def play_appointment_lineup(api: Any, build_id: str, context: Any, lineup: AppointmentLineup, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, config: Any, start_hour: int) -> Any:
    """
    Executes an AppointmentLineup.
    Iterates through slots and plays them either sequentially or aligned to hours.
    """
    logger.info(f"🎬 Appointment Lineup ({lineup.mode}) starting at {context.current_time.strftime('%H:%M')}")

    for i, slot in enumerate(lineup.slots):
        # 1. Determine Target (Anchor vs Filler)
        target = None
        anchor_result = find_active_season(slot.anchor, boss.now.date())
        
        if anchor_result:
            logger.info(f"   Slot {i+1}: Anchor active")
            target = slot.anchor
        else:
            logger.info(f"   Slot {i+1}: Anchor off-season, using fillers")
            target = slot.fillers

        # 2. Resolve and Play
        # We need to handle the target being an AppointmentBlock, SeriesRelay, or simple content
        if isinstance(target, AppointmentBlock):
            context = play_appointment_block(api, build_id, context, target, resolver, logger, boss)
        elif isinstance(target, SeriesRelay):
            context = play_series_relay(api, build_id, context, target, resolver, logger, boss)
        else:
            # Simple content (string, list, collection)
            # We use resolve_target to handle all the complexity (collections, etc)
            res = resolve_target(target, boss, holiday_ctx, config, resolver, logger)
            if res.resolved_content:
                context = play_with_fallback(api, build_id, res.resolved_content, logger, context=context)
            else:
                logger.warn(f"   Slot {i+1}: Could not resolve content")

        # 3. Handle Hourly Mode Alignment
        if lineup.mode == "hourly":
            # Calculate target time for next slot
            # Slot 0 starts at start_hour
            # Slot 1 starts at start_hour + 1
            target_hour = (start_hour + i + 1) % 24
            target_time_str = f"{target_hour:02d}:00"
            is_tomorrow = target_hour == 0 or (target_hour < start_hour and start_hour != 23) # Simple wrap check
            
            # Only fill if we haven't passed the target time
            # (Simple check: if we are in the previous hour)
            current_h = context.current_time.hour
            expected_prev_h = (target_hour - 1) % 24
            
            if current_h == expected_prev_h:
                logger.info(f"   ⏳ Hourly mode: Filling until {target_time_str}")
                context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=config.filler_content, tomorrow=is_tomorrow)

    return context