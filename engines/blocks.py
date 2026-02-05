# scripts/engines/blocks.py
"""
Unified Program and Block Engine.
"""

from datetime import timedelta
from typing import Any, Dict, Optional, Union, TYPE_CHECKING
from scripts.logic.resolver import ContentResolver
from scripts.logic.resolution import resolve_target
from scripts.core.logger import ChannelLogger
from scripts.playout import play_item, toggle_marathon_branding, fill_until_time, play_with_fallback, play_smart_bumper, wait_until_time
from scripts.logic.models import Fallback, CommercialBreak
from scripts.logic.structures import Block, Program
from scripts.logic.playback import hour_in_window, calculate_boundary_dt
from scripts.logic.queries import extract_title_from_query, extract_episode_range
from etv_client.models import ControlSkipToItem
from scripts.logic.sequencing import resolve_scheduled_content

if TYPE_CHECKING:
    from scripts.schedule import ScheduleConfig

def _play_branding_element(api: Any, build_id: str, context: Any, key: Optional[str], element_type: str, resolver: Any, logger: ChannelLogger, boss: Any) -> Any:
    """Generic helper to play a branding element like an intro or outro."""
    if key and key in resolver.registry:
        try:
            resolved_key = resolver.resolve(key, boss)
            logger.info(f"   ↳ Playing {element_type}")
            context = play_item(api, build_id, resolved_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play {element_type}: {e}")
    return context

def play_block_intro(api: Any, build_id: str, context: Any, intro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """Helper to play a block intro."""
    return _play_branding_element(api, build_id, context, intro, "intro", resolver, logger, boss)

def play_block_outro(api: Any, build_id: str, context: Any, outro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """Helper to play a block outro."""
    return _play_branding_element(api, build_id, context, outro, "outro", resolver, logger, boss)

def _get_content_title(resolver: Any, content_key: str) -> Optional[str]:
    """Extract show title from a content key's query."""
    data = resolver.get_query_data(content_key)
    query = None
    if isinstance(data, dict):
        query = data.get("query")
    elif isinstance(data, str):
        query = data
    
    if query:
        return extract_title_from_query(query)
    return None


def play_block(api: Any, build_id: str, context: Any, item: Union[Block, Program], sources_registry: Dict[str, Any], logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, holiday_ctx: Any, config: "ScheduleConfig") -> Any:
    """Unified engine to play a Block or a single Program."""
    resolver = ContentResolver(api, build_id, sources_registry, logger)
    
    if isinstance(item, Program):
        return play_program(api, build_id, context, item, resolver, logger, boss, holiday_ctx, start_hour, end_hour, config)
    
    if isinstance(item, Block):
        return _play_block_internal(api, build_id, context, item, resolver, logger, start_hour, end_hour, boss, holiday_ctx, config)

    logger.warn(f"play_block received an unsupported type: {type(item)}")
    return context

def _play_block_internal(api: Any, build_id: str, context: Any, block: Block, resolver: Any, logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, holiday_ctx: Any, config: "ScheduleConfig") -> Any:
    """Internal logic to play a Block object (a container of Programs/content)."""
    logger.info(f"🎬 {block.name} ({start_hour}:00-{end_hour}:00)")

    if block.use_epg_group: toggle_marathon_branding(api, build_id, name=block.name, start=True)
    context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
    
    items_played = 0
    last_time = context.current_time
    
    iterator = block.items
    is_collection = hasattr(block.items, "pick")
    
    while not context.is_done:
        hour = context.current_time.hour
        if not hour_in_window(hour, start_hour, end_hour): logger.info(f"🕒 Block time window ended at {context.current_time.strftime('%H:%M')}"); break
            
        item_to_play = None
        if is_collection:
            item_to_play = iterator.pick(boss)
        else:
            if items_played < len(iterator): item_to_play = iterator[items_played]
            else: logger.info("Block items exhausted."); break
        
        if isinstance(item_to_play, Program):
            context = play_program(api, build_id, context, item_to_play, resolver, logger, boss, holiday_ctx, start_hour, end_hour, config)
        else:
            context = _play_raw_content_in_block(api, build_id, context, item_to_play, block, resolver, logger, boss, holiday_ctx, config)

        items_played += 1
        if context.current_time <= last_time: logger.warn("Block item failed to advance time. Breaking block."); break
        last_time = context.current_time

    # After loop, handle fill strategy for the block itself
    context = _handle_fill_strategy(api, build_id, context, block.fill_strategy, block.filler, start_hour, end_hour, config, resolver, logger, boss, holiday_ctx, log_indent="   ")

    context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
    if block.use_epg_group: toggle_marathon_branding(api, build_id, start=False)
    logger.info(f"🏁 {block.name} - {items_played} items played")
    return context


def _play_commercials(api: Any, build_id: str, context: Any, commercials_key: Optional[str], duration: int, config: "ScheduleConfig", resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, log_indent: str = "     ", log_prefix: str = "Program") -> Any:
    """Helper to play commercials (duration-based or content-based)."""
    if duration > 0:
        # Duration-based break. Use specific ad pool or channel default.
        ad_pool_key = commercials_key or config.commercial_content
        
        res = resolve_target(ad_pool_key, boss, holiday_ctx, config, resolver, logger)
        filler_key = res.resolved_content
        
        if filler_key:
            target_dt = context.current_time + timedelta(seconds=duration)
            target_time_str = target_dt.strftime("%H:%M")
            is_tomorrow = target_dt.day > context.current_time.day
            
            logger.info(f"{log_indent}☕ {log_prefix} Commercials ({duration}s from '{filler_key}')")
            context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=filler_key, tomorrow=is_tomorrow)
        else:
            logger.warn(f"Commercial break skipped: ad pool '{ad_pool_key}' could not be resolved.")
    elif commercials_key:
        # Content-based break (play entire block)
        res = resolve_target(commercials_key, boss, holiday_ctx, config, resolver, logger)
        if res.resolved_content:
            logger.info(f"{log_indent}↳ Playing {log_prefix.lower()} commercials: {res.resolved_content}")
            context = play_item(api, build_id, res.resolved_content, logger)
            
    return context

def _play_bumper(api: Any, build_id: str, context: Any, bumper_key: Optional[str], content_key: Any, resolver: Any, logger: ChannelLogger, boss: Any) -> Any:
    """Helper to play a bumper (smart or generic)."""
    # Try Smart Bumper first
    base_key = content_key.primary if isinstance(content_key, Fallback) else content_key
    title = _get_content_title(resolver, base_key)
    
    played_smart = False
    if title:
        context, played_smart = play_smart_bumper(api, build_id, context, title, resolver, logger, required_tags=["bumpers"])
        
    # Fallback to generic bumper
    if not played_smart and bumper_key and bumper_key in resolver.registry:
        try:
            resolved_key = resolver.resolve(bumper_key, boss)
            logger.info(f"   ↳ Playing bumper: {resolved_key}")
            context = play_item(api, build_id, resolved_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play bumper: {e}")
    return context

def _handle_fill_strategy(api: Any, build_id: str, context: Any, fill_strategy: str, filler: Any, start_hour: int, end_hour: int, config: "ScheduleConfig", resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, log_indent: str = "     ") -> Any:
    """Helper to handle fill strategies (gap, fill, yield) at the end of a slot."""
    if fill_strategy == "yield":
        logger.info(f"{log_indent}Fill Strategy: 'yield'. Stopping.")
        return context

    boundary_dt = calculate_boundary_dt(context, start_hour, end_hour)
    
    if context.current_time < boundary_dt:
        target_ts = boundary_dt.strftime("%H:%M")
        is_tomorrow = boundary_dt.day > context.current_time.day
        if fill_strategy == "gap":
            logger.info(f"{log_indent}Fill Strategy: 'gap'. Waiting until slot end at {target_ts}.")
            context = wait_until_time(api, build_id, context, logger, target_ts, tomorrow=is_tomorrow)
        elif fill_strategy == "fill":
            res = resolve_target(filler, boss, holiday_ctx, config, resolver, logger)
            if res.resolved_content:
                logger.info(f"{log_indent}Fill Strategy: 'fill'. Filling with '{res.resolved_content}' until {target_ts}.")
                context = fill_until_time(api, build_id, context, logger, target_ts, filler_key=res.resolved_content, tomorrow=is_tomorrow)
            else:
                logger.warn(f"{log_indent}Fill Strategy: 'fill' failed, filler '{filler}' not resolved. Waiting instead.")
                context = wait_until_time(api, build_id, context, logger, target_ts, tomorrow=is_tomorrow)
    
    return context

def play_program(api: Any, build_id: str, context: Any, program: Program, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, start_hour: int, end_hour: int, config: "ScheduleConfig") -> Any:
    """Executes a Program. Handles scheduling, branding, content playback, and fill strategy."""
    logger.info(f"   ▶ Program: {program.name}")
    
    content_key, count = None, 1
    scheduled_result = resolve_scheduled_content(program, boss.now.date())
    
    if scheduled_result:
        key, ep_count, ep_num = scheduled_result
        ep_per_slot = program.scheduling.get("episodes_per_slot", 1)
        end_ep = min(ep_num + ep_per_slot - 1, ep_count)
        ep_str = f"{ep_num}" if ep_num == end_ep else f"{ep_num}-{end_ep}"
        logger.info(f"     Scheduling active: Playing '{key}' (Episode {ep_str}/{ep_count})")
        content_key, count = resolver.resolve(key), ep_per_slot
        try:
            q_data = resolver.get_query_data(key)
            query = q_data.get("query") if isinstance(q_data, dict) else q_data
            if query and (q_season := extract_episode_range(query)[0]) is not None:
                api.skip_to_item(build_id, ControlSkipToItem(content=key, season=q_season, episode=ep_num))
        except Exception as e: logger.warn(f"Failed to force sequence for '{key}': {e}")
    else:
        logger.info(f"     Playing static content for '{program.name}'")
        res = resolve_target(program.content, boss, holiday_ctx, config, resolver, logger)
        content_key = res.resolved_content

    if not content_key: logger.warn(f"Could not resolve content for Program '{program.name}'. Skipping."); return context

    context = play_block_intro(api, build_id, context, program.intro, resolver, logger, boss)
    
    context = _play_bumper(api, build_id, context, program.bumpers, content_key, resolver, logger, boss)

    last_time = context.current_time
    context = play_with_fallback(api, build_id, content_key, logger, context=context, count=count)
    
    context = _play_commercials(api, build_id, context, program.commercials, program.commercial_duration, config, resolver, logger, boss, holiday_ctx, log_indent="     ", log_prefix="Program")

    if context.current_time > last_time:
        context = _handle_fill_strategy(api, build_id, context, program.fill_strategy, program.filler, start_hour, end_hour, config, resolver, logger, boss, holiday_ctx, log_indent="     ")

    context = play_block_outro(api, build_id, context, program.outro, resolver, logger, boss)
    return context

def _play_raw_content_in_block(api: Any, build_id: str, context: Any, content: Any, block: Block, resolver: Any, logger: ChannelLogger, boss: Any, holiday_ctx: Any, config: "ScheduleConfig") -> Any:
    """Plays raw content (string, collection) within a Block, applying block-level branding."""
    res = resolve_target(content, boss, holiday_ctx, config, resolver, logger)
    content_key = res.resolved_content

    # Handle CommercialBreak items within a block
    if isinstance(content_key, CommercialBreak):
        cb = content_key
        # Resolve the content of the break
        cb_res = resolve_target(cb.content, boss, holiday_ctx, config, resolver, logger)
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
        # If duration is 0, treat as regular content (fall through)
    
    if not content_key:
        logger.warn(f"Could not resolve raw content in block '{block.name}'. Skipping.")
        return context

    context = play_with_fallback(api, build_id, content_key, logger, context=context)

    context = _play_bumper(api, build_id, context, block.bumpers, content_key, resolver, logger, boss)

    # Block-level Commercials (between items)
    context = _play_commercials(api, build_id, context, block.commercials, block.commercial_duration, config, resolver, logger, boss, holiday_ctx, log_indent="   ", log_prefix="Block")
        
    return context