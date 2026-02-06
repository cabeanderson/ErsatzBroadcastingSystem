# scripts/engines/blocks.py
"""
Unified Program and Block Engine.
"""

from datetime import timedelta
from typing import Any, Dict, Optional, Union, Tuple, List, TYPE_CHECKING
from scripts.logic.resolution.resolver import ContentResolver
from scripts.logic.resolution.pipeline import resolve_content, apply_injections, resolve_scheduled_content
from scripts.core.logger import ChannelLogger
from scripts.playout import play_item, epg_group, fill_until_time, play_with_fallback, wait_until_time, circuit_breaker
from scripts.logic.models import Fallback, CommercialBreak
from scripts.logic.structures import Block, Program
from scripts.logic.resolution.playback import hour_in_window
from scripts.library.queries import extract_episode_range
from etv_client.models import ControlSkipToItem
from scripts.logic.resolution.config_utils import resolve_feature, resolve_commercial_duration, resolve_filler_content, resolve_bumper_collection
from scripts.engines.dispatcher import play_commercials, play_bumper, fill_to_boundary, play_generic_branding

if TYPE_CHECKING:
    from scripts.scheduling.config import ScheduleConfig

def play_block_intro(api: Any, build_id: str, context: Any, intro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """Helper to play a block intro."""
    return play_generic_branding(api, build_id, context, intro, "intro", resolver, logger, boss)

def play_block_outro(api: Any, build_id: str, context: Any, outro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """Helper to play a block outro."""
    return play_generic_branding(api, build_id, context, outro, "outro", resolver, logger, boss)

def play_block(api: Any, build_id: str, context: Any, item: Union[Block, Program], resolver: Any, logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, holiday_ctx: Any, config: "ScheduleConfig", day_schedule: Optional[Dict[Tuple[int, int], Any]] = None) -> Any:
    """Unified engine to play a Block or a single Program."""
    # Resolver is passed in to maintain active_keys cache
    if isinstance(item, Program):
        return play_program(api, build_id, context, item, resolver, logger, boss, holiday_ctx, start_hour, end_hour, config, day_schedule=day_schedule)
    
    if isinstance(item, Block):
        return _play_block_internal(api, build_id, context, item, resolver, logger, start_hour, end_hour, boss, holiday_ctx, config, day_schedule=day_schedule)

    logger.warn(f"play_block received an unsupported type: {type(item)}")
    return context

def _play_block_internal(api: Any, build_id: str, context: Any, block: Block, resolver: Any, logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, holiday_ctx: Any, config: "ScheduleConfig", day_schedule: Optional[Dict[Tuple[int, int], Any]] = None) -> Any:
    """Internal logic to play a Block object (a container of Programs/content)."""
    logger.info(f"🎬 {block.name} ({start_hour}:00-{end_hour}:00)")

    # Resolve features and context
    bumpers_enabled = resolve_feature(None, block.enable_bumpers, config.enable_bumpers)
    slot_name = config.timeslot_reverse_map.get((start_hour, end_hour))
    
    # Check for strict window adherence (Default: True)
    # True = Hard Stop: Block ends exactly when the timeslot ends (cutting off content if needed).
    # False = Soft Stop: Block allows the current item to finish even if it overflows the timeslot.
    strict_window = getattr(block, 'strict_window', True)

    items_played = 0
    epg_name = block.name if block.use_epg_group else None
    with epg_group(api, build_id, epg_name):
        if bumpers_enabled: context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
        
        last_time = context.current_time
        
        iterator = block.items
        is_collection = hasattr(block.items, "pick")
        
        while not context.is_done:
            # Only check window if strict
            if strict_window:
                hour = context.current_time.hour
                if not hour_in_window(hour, start_hour, end_hour): logger.info(f"🕒 Block time window ended at {context.current_time.strftime('%H:%M')}"); break
                
            item_to_play = None
            if is_collection:
                item_to_play = iterator.pick(boss)
            else:
                if items_played < len(iterator): item_to_play = iterator[items_played]
                else: logger.info("Block items exhausted."); break
            
            if isinstance(item_to_play, Program):
                context = play_program(api, build_id, context, item_to_play, resolver, logger, boss, holiday_ctx, start_hour, end_hour, config, parent_block=block)
            else:
                context = play_block_item(api, build_id, context, item_to_play, block, resolver, logger, boss, holiday_ctx, config, slot_name=slot_name)

            items_played += 1
            
            context = circuit_breaker(api, build_id, context, last_time, logger, fallback_content=config.fallback_content, skip_minutes=config.circuit_breaker_skip)
            if context.current_time <= last_time:
                logger.warn("Block item failed to advance time. Breaking block.")
                break
            last_time = context.current_time

        # After loop, handle fill strategy for the block itself
        if block.fill_strategy == "bridge":
            context = _bridge_to_next_slot(api, build_id, context, (start_hour, end_hour), day_schedule, boss, holiday_ctx, config, resolver, logger)
        else:
            # Always fill/wait to boundary if we finished early, to prevent Runner from re-scheduling this slot.
            # strict_window=False allows OVERflow, but we must handle UNDERflow.
            context = fill_to_boundary(api, build_id, context, config, resolver, logger, boss, holiday_ctx, start_hour, end_hour, strategy=block.fill_strategy, filler_content=block.filler, log_indent="   ", parent_item=block)

        if bumpers_enabled: context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
    logger.info(f"🏁 {block.name} - {items_played} items played")
    return context

def _bridge_to_next_slot(
    api: Any, build_id: str, context: Any, current_slot_tuple: Tuple[int, int], day_schedule: Dict[Tuple[int, int], Any], boss: Any, holiday_ctx: Any, config: "ScheduleConfig", resolver: Any, logger: ChannelLogger
) -> Any:
    """Fills the rest of a slot with content from the *next* scheduled block."""
    from scripts.logic.resolution.playback import calculate_boundary_dt
    from scripts.logic.resolution.pipeline import extract_primary_content
    from scripts.engines.dispatcher import maintain_playout_invariants

    start, end = current_slot_tuple
    boundary_dt = calculate_boundary_dt(context, start, end)
    
    next_slot_entry = None
    if day_schedule:
        lookup_start = 0 if end == 24 else end
        for (s, e), entry in sorted(day_schedule.items()):
            if s == lookup_start:
                next_slot_entry = entry
                break

    last_time = context.current_time
    while context.current_time < boundary_dt:
        if next_slot_entry:
            try:
                logger.info("  Bridging to next block to fill gap")
                next_key = extract_primary_content(next_slot_entry, boss, holiday_ctx, config, resolver, logger)
                res = apply_injections(next_key, config=config, resolver=resolver, boss=boss, holiday_ctx=holiday_ctx, logger=logger, source="slot_fill")
                next_key = res.resolved_content

                if next_key:
                    context = play_with_fallback(api, build_id, next_key, logger, context=context)
                else:
                    raise ValueError("Content resolution returned None")
            except Exception as e:
                logger.warn(f"  ⚠️ Error resolving next block for bridge: {e}")
                next_slot_entry = None
        
        if not next_slot_entry:
            # No next slot, use standard filler/wait
            target_hour = boundary_dt.hour
            target_time_str = f"{target_hour:02d}:00"
            is_tomorrow = boundary_dt.day > context.current_time.day
            
            filler_key = None
            if config.enable_filler:
                try:
                    filler_content = resolve_filler_content(None, None, config)
                    filler_result = resolve_content(filler_content, boss, holiday_ctx, config, resolver, logger)
                    filler_key = filler_result.resolved_content
                    if isinstance(filler_key, Fallback):
                        filler_key = filler_key.primary
                except Exception as e:
                    logger.warn(f"  ⚠️ Bridge filler content unavailable: {e}")
            
            if filler_key:
                logger.info(f"  Bridge complete. Filling until {target_time_str}")
            else:
                logger.info(f"  Bridge complete. Waiting until {target_time_str}")
            
            context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key, tomorrow=is_tomorrow)
            break
        
        context = maintain_playout_invariants(api, build_id, context, last_time, config, boss, holiday_ctx, resolver)
        if context.current_time <= last_time:
            logger.error("Bridge fill failed: circuit breaker couldn't advance time")
            break 
        last_time = context.current_time
            
    return context

def _resolve_and_prepare_program_content(
    api: Any, build_id: str, program: Program, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, config: "ScheduleConfig"
) -> Tuple[Optional[Any], int]:
    """
    Resolves program content, handling Appointment TV scheduling and static content.
    Returns the content key and the number of items to play.
    """
    # 1. Appointment TV (Scheduled Content)
    scheduled_result = resolve_scheduled_content(program, boss.now.date())
    if scheduled_result:
        key, ep_count, ep_num = scheduled_result
        ep_per_slot = program.scheduling.get("episodes_per_slot", 1)
        end_ep = min(ep_num + ep_per_slot - 1, ep_count)
        ep_str = f"{ep_num}" if ep_num == end_ep else f"{ep_num}-{end_ep}"
        logger.info(f"     Scheduling active: Playing '{key}' (Episode {ep_str}/{ep_count})")
        
        content_key, count = resolver.resolve(key), ep_per_slot
        
        # Attempt to skip to the exact episode for robust playback
        try:
            q_data = resolver.get_query_data(key)
            query = q_data.get("query") if isinstance(q_data, dict) else q_data
            if query and (q_season := extract_episode_range(query)[0]) is not None:
                api.skip_to_item(build_id, ControlSkipToItem(content=key, season=q_season, episode=ep_num))
        except Exception as e: 
            logger.warn(f"Failed to force sequence for '{key}': {e}")

        return content_key, count

    # 2. Static Content
    logger.info(f"     Playing static content for '{program.name}'")
    res = resolve_content(program.content, boss, holiday_ctx, config, resolver, logger, parent_item=program)
    
    content_key = res.resolved_content
    count = program.play_count or 1

    # Handle start_point for static content (marathon-converted programs)
    if program.start_point and isinstance(program.start_point, tuple) and len(program.start_point) == 2:
        season, episode = program.start_point
        try:
            api.skip_to_item(build_id, ControlSkipToItem(content=content_key, season=season, episode=episode))
        except Exception as e:
            logger.warn(f"Failed to force sequence for '{content_key}' via start_point: {e}")

    return content_key, count

def _handle_program_bumpers(
    api: Any, build_id: str, context: Any, program: Program, parent_block: Optional[Block], config: "ScheduleConfig", resolver: Any, logger: ChannelLogger, boss: Any, content_key: str, enabled: bool
) -> Any:
    """Helper to resolve and play bumpers for a program."""
    bumper_key = resolve_bumper_collection(program, parent_block, config)
    return play_bumper(api, build_id, context, config, resolver, logger, boss, content_key, bumper_key=bumper_key, enabled=enabled)

def _handle_program_commercials(
    api: Any, build_id: str, context: Any, program: Program, parent_block: Optional[Block], config: "ScheduleConfig", resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, slot_name: Optional[str]
) -> Any:
    """Helper to resolve and play commercials for a program."""
    block_commercials = parent_block.enable_commercials if parent_block else None
    comm_duration = resolve_commercial_duration(program, parent_block, config, slot_name=slot_name)
    commercials_enabled = resolve_feature(program.enable_commercials, block_commercials, config.enable_commercials)
    
    return play_commercials(
        api, build_id, context, config, resolver, logger, boss, holiday_ctx,
        duration=comm_duration, content=program.commercials, enabled=commercials_enabled,
        log_indent="     ", parent_item=program
    )

def _handle_program_filler(
    api: Any, build_id: str, context: Any, program: Program, parent_block: Optional[Block], config: "ScheduleConfig", resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, start_hour: int, end_hour: int
) -> Any:
    """Helper to resolve and play filler for a program."""
    # Check parent block strictness - Special Blocks shouldn't fill gaps
    if parent_block and not getattr(parent_block, 'strict_window', True):
        return context

    block_filler = parent_block.enable_filler if parent_block and hasattr(parent_block, 'enable_filler') else None
    filler_enabled = resolve_feature(program.enable_filler, block_filler, config.enable_filler)
    filler_content = resolve_filler_content(program, parent_block, config)
    
    return fill_to_boundary(
        api, build_id, context, config, resolver, logger, boss, holiday_ctx,
        start_hour, end_hour, strategy=program.fill_strategy, filler_content=filler_content,
        enabled=filler_enabled, log_indent="     ", parent_item=program
    )

def play_program(api: Any, build_id: str, context: Any, program: Program, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, start_hour: int, end_hour: int, config: "ScheduleConfig", parent_block: Optional[Block] = None, day_schedule: Optional[Dict[Tuple[int, int], Any]] = None) -> Any:
    """Executes a Program. Handles scheduling, branding, content playback, and fill strategy."""
    logger.info(f"   ▶ Program: {program.name}")
    
    # Resolve features and context
    block_bumpers = parent_block.enable_bumpers if parent_block else None
    bumpers_enabled = resolve_feature(program.enable_bumpers, block_bumpers, config.enable_bumpers)
    slot_name = config.timeslot_reverse_map.get((start_hour, end_hour))

    content_key, count = _resolve_and_prepare_program_content(
        api, build_id, program, resolver, logger, boss, holiday_ctx, config
    )

    if not content_key: 
        logger.warn(f"Could not resolve content for Program '{program.name}'. Skipping.")
        return context

    # Apply Injections (Holiday -> Seasonal)
    res = apply_injections(
        content_key,
        program=program,
        block=parent_block,
        config=config,
        resolver=resolver,
        boss=boss,
        holiday_ctx=holiday_ctx,
        logger=logger,
        source="program"
    )

    content_key = res.resolved_content

    if bumpers_enabled: 
        context = play_block_intro(api, build_id, context, program.intro, resolver, logger, boss)

    context = _handle_program_bumpers(
        api, build_id, context, program, parent_block, config, resolver, logger, boss, content_key, bumpers_enabled
    )

    last_time = context.current_time
    context = play_with_fallback(api, build_id, content_key, logger, context=context, count=count)
    
    context = _handle_program_commercials(
        api, build_id, context, program, parent_block, config, resolver, logger, boss, holiday_ctx, slot_name
    )

    if context.current_time > last_time:
        if program.fill_strategy == "bridge":
            context = _bridge_to_next_slot(api, build_id, context, (start_hour, end_hour), day_schedule, boss, holiday_ctx, config, resolver, logger)
        else:
            context = _handle_program_filler(
                api, build_id, context, program, parent_block, config, resolver, logger, boss, holiday_ctx, start_hour, end_hour
            )

    if bumpers_enabled: 
        context = play_block_outro(api, build_id, context, program.outro, resolver, logger, boss)
    return context

def _handle_block_item_commercial_break(
    api: Any, build_id: str, context: Any, cb: CommercialBreak, block: Block, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, config: "ScheduleConfig"
) -> Optional[Any]:
    """Handles a CommercialBreak object found as an item in a block."""
    # Resolve the content of the break
    cb_res = resolve_content(cb.content, boss, holiday_ctx, config, resolver, logger, parent_item=block)
    cb_key = cb_res.resolved_content
    
    if isinstance(cb_key, Fallback):
        cb_key = cb_key.primary
        
    if cb.duration_seconds > 0:
        target_dt = context.current_time + timedelta(seconds=cb.duration_seconds)
        target_time_str = target_dt.strftime("%H:%M")
        is_tomorrow = target_dt.day > context.current_time.day
        
        logger.info(f"   ☕ Block Item: Commercial Break ({cb.duration_seconds}s)")
        context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=cb_key, tomorrow=is_tomorrow)
        return context
    
    # If duration is 0, fall through by returning None
    return None

def play_block_item(api: Any, build_id: str, context: Any, content: Any, block: Block, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, config: "ScheduleConfig", slot_name: Optional[str] = None) -> Any:
    """Plays raw content (string, collection) within a Block, applying block-level branding."""
    res = resolve_content(content, boss, holiday_ctx, config, resolver, logger, parent_item=block)
    content_key = res.resolved_content

    # Handle CommercialBreak items within a block.
    if isinstance(content_key, CommercialBreak):
        new_context = _handle_block_item_commercial_break(
            api, build_id, context, content_key, block, resolver, logger, boss, holiday_ctx, config
        )
        if new_context:
            return new_context
        # If duration is 0, fall through to treat as regular content
    
    if not content_key:
        logger.warn(f"Could not resolve raw content in block '{block.name}'. Skipping.")
        return context

    # Apply Injections (Holiday -> Seasonal)
    res = apply_injections(
        content_key,
        block=block,
        config=config,
        resolver=resolver,
        boss=boss,
        holiday_ctx=holiday_ctx,
        logger=logger,
        source="block_item"
    )

    content_key = res.resolved_content

    context = play_with_fallback(api, build_id, content_key, logger, context=context)

    # Resolve bumper flag
    bumpers_enabled = resolve_feature(None, block.enable_bumpers, config.enable_bumpers)
    bumper_key = resolve_bumper_collection(None, block, config)
    context = play_bumper(api, build_id, context, config, resolver, logger, boss, content_key, bumper_key=bumper_key, enabled=bumpers_enabled)

    # Block-level Commercials (between items)
    # Resolve commercials flag
    commercials_enabled = resolve_feature(None, block.enable_commercials, config.enable_commercials)
    comm_duration = resolve_commercial_duration(None, block, config, slot_name=slot_name)
    context = play_commercials(api, build_id, context, config, resolver, logger, boss, holiday_ctx, duration=comm_duration, content=block.commercials, enabled=commercials_enabled, log_indent="   ", parent_item=block)
        
    return context