"""
The Dispatcher - Central orchestration for playback logic.
Handles slot execution, commercial insertion, bumpers, and gap filling.
"""

import re
from datetime import timedelta
from typing import Any, Dict, Tuple, Optional, Union, List, TYPE_CHECKING

from scripts.core.logger import ChannelLogger
from scripts.playout import (
    fill_until_time, play_with_fallback, play_item, 
    wait_until_time, fill_until_next_hour,
    circuit_breaker
)
from scripts.logic.resolution.pipeline import (
    resolve_content, apply_injections, extract_primary_content
)
from scripts.logic.models import Fallback, CommercialBreak
from scripts.logic.structures import Block, Program
from scripts.logic.resolution.playback import (
    calculate_boundary_dt, is_approaching_hour_boundary
)
from scripts.logic.resolution.config_utils import (
    resolve_filler_content
)
from scripts.settings import ENABLE_SMART_BUMPERS

if TYPE_CHECKING:
    from scripts.scheduling.config import ScheduleConfig
    from scripts.logic.resolution.resolver import ContentResolver
    from scripts.core import DayDirector
    from scripts.logic.calendar.holidays import HolidayContext

# Global cache to store failed bumper searches during this run
# Key: (safe_title, tags_tuple)
# Value: True (meaning "we checked, and it doesn't exist")
BUMPER_FAILURE_CACHE = {}

# --- UNIFIED HELPERS ---

def play_generic_branding(api: Any, build_id: str, context: Any, key: Optional[str], element_type: str, resolver: Any, logger: ChannelLogger, boss: Any) -> Any:
    """
    Generic helper to play a branding element like an intro or outro.
    Checks registry existence before attempting resolve/play.
    """
    if key and key in resolver.registry:
        try:
            resolved_key = resolver.resolve(key, boss)
            logger.info(f"   ↳ Playing {element_type}")
            context = play_item(api, build_id, resolved_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play {element_type}: {e}")
    return context

def play_commercials(
    api: Any, 
    build_id: str, 
    context: Any, 
    config: "ScheduleConfig", 
    resolver: Any, 
    logger: ChannelLogger, 
    boss: Any, 
    holiday_ctx: Any, 
    duration: int = 0, 
    content: Optional[str] = None,
    enabled: bool = True,
    log_indent: str = "",
    parent_item: Optional[Union[Block, Program]] = None
) -> Any:
    """
    Unified commercial playback logic.
    Handles both duration-based (fill) and content-based (play item) breaks.
    """
    if not enabled:
        return context

    # 1. Duration-based break (Priority)
    if duration > 0:
        # Use specific content pool if provided, else channel default
        ad_pool_key = content or config.commercial_content
        
        res = resolve_content(ad_pool_key, boss, holiday_ctx, config, resolver, logger, parent_item=parent_item)
        filler_key = res.resolved_content
        
        if isinstance(filler_key, Fallback):
            filler_key = filler_key.primary

        if filler_key:
            target_dt = context.current_time + timedelta(seconds=duration)
            target_time_str = target_dt.strftime("%H:%M")
            is_tomorrow = target_dt.day > context.current_time.day
            
            logger.info(f"{log_indent}☕ Commercials ({duration}s)")
            context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=filler_key, tomorrow=is_tomorrow)
        else:
            logger.warn(f"Commercial break skipped: ad pool '{ad_pool_key}' could not be resolved.")
            
    # 2. Content-based break (Play specific item/block)
    elif content:
        res = resolve_content(content, boss, holiday_ctx, config, resolver, logger, parent_item=parent_item)
        if res.resolved_content:
            logger.info(f"{log_indent}↳ Playing commercial block: {res.resolved_content}")
            context = play_item(api, build_id, res.resolved_content, logger)

    return context

def play_smart_bumper(api: Any, build_id: str, context: Any, title: Optional[str], resolver: Any, logger: ChannelLogger, required_tags: List[str] = None, fallback_tags: List[List[str]] = None) -> Tuple[Any, bool]:
    """
    Attempts to play a smart bumper, with support for fallbacks and caching.
    
    Args:
        required_tags: Primary tags to check (e.g. ["marathon", "bumpers"])
        fallback_tags: List of tag lists to try if primary fails (e.g. [["bumpers"]])
    """
    if not title or not ENABLE_SMART_BUMPERS:
        return context, False

    safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()
    
    # Construct the list of attempts: Primary + Fallbacks
    attempts = []
    if required_tags:
        attempts.append(required_tags)
    if fallback_tags:
        attempts.extend(fallback_tags)
    
    if not attempts:
        attempts = [["bumpers"]] # Default

    for tags in attempts:
        # 1. Check Cache
        cache_key = (safe_title, tuple(sorted(tags)))
        if cache_key in BUMPER_FAILURE_CACHE:
            continue # Skip API call, we know it fails

        # 2. Prepare Query
        tag_queries = [f'tag:"{t}"' for t in tags]
        bumper_query = f'type:"other_video" AND tag:"{title}" AND {" AND ".join(tag_queries)}'
        
        tags_suffix = "_".join(tags).lower().replace(" ", "")
        bumper_key = f"auto_bumper_{safe_title}_{tags_suffix}"
        
        resolver.register_dynamic_query(bumper_key, bumper_query)
        
        # 3. Try Play
        try:
            old_time = context.current_time
            # suppress_errors=True prevents log spam for expected failures
            context = play_item(api, build_id, bumper_key, logger, suppress_errors=True)
            
            if context.current_time > old_time:
                logger.info(f"   ↳ Playing smart bumper: {bumper_key}")
                return context, True
            else:
                # 4. Log Failure in Cache
                BUMPER_FAILURE_CACHE[cache_key] = True
                
        except Exception:
            BUMPER_FAILURE_CACHE[cache_key] = True
            pass
        
    return context, False

def play_bumper(
    api: Any, 
    build_id: str, 
    context: Any, 
    config: "ScheduleConfig", 
    resolver: Any, 
    logger: ChannelLogger, 
    boss: Any, 
    content_key: Any, 
    bumper_key: Optional[str] = None,
    enabled: bool = True,
    required_tags: Optional[List[str]] = None,
    fallback_tags: Optional[List[List[str]]] = None
) -> Any:
    """
    Unified bumper playback logic.
    Tries smart bumpers first, then falls back to generic bumpers.
    """
    if not enabled:
        return context
        
    # Try Smart Bumper first
    # Extract title from content key
    base_key = content_key.primary if isinstance(content_key, Fallback) else content_key
    
    title = None
    data = resolver.get_query_data(base_key)
    if data is None:
        return context

    query = None
    if isinstance(data, dict):
        query = data.get("query")
    elif isinstance(data, str):
        query = data
    elif hasattr(data, "query"): # Handle MarathonDefinition or other objects
        query = data.query
    
    if query:
        from scripts.library.queries import extract_title_from_query
        title = extract_title_from_query(query)
    
    played_smart = False
    if title:
        # Use provided tags or default to ["bumpers"]
        req = required_tags if required_tags else ["bumpers"]
        context, played_smart = play_smart_bumper(api, build_id, context, title, resolver, logger, required_tags=req, fallback_tags=fallback_tags)
        
    # Fallback to generic bumper
    if not played_smart and bumper_key and bumper_key in resolver.registry:
        try:
            resolved_key = resolver.resolve(bumper_key, boss)
            logger.info(f"   ↳ Playing bumper: {resolved_key}")
            context = play_item(api, build_id, resolved_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play bumper: {e}")
            
    return context

def fill_to_boundary(
    api: Any, 
    build_id: str, 
    context: Any, 
    config: "ScheduleConfig", 
    resolver: Any, 
    logger: ChannelLogger, 
    boss: Any, 
    holiday_ctx: Any, 
    start_hour: int, 
    end_hour: int, 
    strategy: str = "yield", 
    filler_content: Any = None,
    enabled: bool = True,
    log_indent: str = "",
    parent_item: Optional[Union[Block, Program]] = None
) -> Any:
    """
    Unified logic for filling time at the end of a slot/block.
    Handles 'yield', 'gap', and 'fill' strategies.
    """
    if strategy == "yield":
        logger.info(f"{log_indent}Fill Strategy: 'yield'. Stopping.")
        return context
        
    if not enabled and strategy == "fill":
        logger.info(f"{log_indent}Fill strategy 'fill' ignored, filler disabled.")
        return context

    boundary_dt = calculate_boundary_dt(context, start_hour, end_hour)
    
    if context.current_time < boundary_dt:
        target_ts = boundary_dt.strftime("%H:%M")
        is_tomorrow = boundary_dt.day > context.current_time.day
        
        if strategy == "gap":
            logger.info(f"{log_indent}Fill Strategy: 'gap'. Waiting until {target_ts}.")
            context = wait_until_time(api, build_id, context, logger, target_ts, tomorrow=is_tomorrow)
            
        elif strategy == "fill":
            # Resolve filler
            filler_to_use = filler_content or config.filler_content
            res = resolve_content(filler_to_use, boss, holiday_ctx, config, resolver, logger, parent_item=parent_item)
            
            if res.resolved_content:
                logger.info(f"{log_indent}Fill Strategy: 'fill'. Filling with '{res.resolved_content}' until {target_ts}.")
                context = fill_until_time(api, build_id, context, logger, target_ts, filler_key=res.resolved_content, tomorrow=is_tomorrow)
            else:
                logger.warn(f"{log_indent}Fill Strategy: 'fill' failed, filler not resolved. Waiting instead.")
                context = wait_until_time(api, build_id, context, logger, target_ts, tomorrow=is_tomorrow)
        
        # SAFETY: Ensure we actually reached the boundary.
        # If pad_until under-filled or failed silently, force a hard wait to prevent infinite loops in Runner.
        if context.current_time < boundary_dt:
            logger.warn(f"{log_indent}⚠️ Fill/Pad didn't reach boundary. Forcing wait until {target_ts}.")
            context = wait_until_time(api, build_id, context, logger, target_ts, tomorrow=is_tomorrow)
    
    return context

def maintain_playout_invariants(
    api: Any, 
    build_id: str, 
    context: Any, 
    last_time: Any, 
    config: "ScheduleConfig", 
    boss: "DayDirector", 
    holiday_ctx: "HolidayContext", 
    resolver: "ContentResolver"
) -> Any:
    """
    Handles fallback logic, circuit breaking, and filler at hour boundaries.
    """
    # Resolve fallback content only if stalled
    fallback_key = None
    if context.current_time <= last_time and config.fallback_content:
        try:
            fb_res = resolve_content(config.fallback_content, boss, holiday_ctx, config, resolver, config.logger)
            if isinstance(fb_res.resolved_content, str):
                fallback_key = fb_res.resolved_content
        except Exception as e:
            config.logger.warn(f"Failed to resolve fallback content: {e}")

    context = circuit_breaker(api, build_id, context, last_time, config.logger, fallback_content=fallback_key, skip_minutes=config.circuit_breaker_skip)

    if config.enable_filler and config.filler_content and is_approaching_hour_boundary(context):
        # Resolve filler content
        filler_result = resolve_content(config.filler_content, boss, holiday_ctx, config, resolver, config.logger)
        filler_content = filler_result.resolved_content
        
        if isinstance(filler_content, Fallback):
            filler_content = filler_content.primary

        context = fill_until_next_hour(api, build_id, context, config.logger, filler_content)
        
    return context

# --- SLOT EXECUTION ---

def play_schedule_slot(
    api: Any, 
    build_id: str, 
    context: Any, 
    result: Any, 
    current_slot_tuple: Tuple[int, int],
    config: "ScheduleConfig", 
    resolver: "ContentResolver", 
    boss: "DayDirector",
    holiday_ctx: "HolidayContext",
    day_schedule: Optional[Dict[Tuple[int, int], Any]] = None
) -> Any:
    """
    Handles the playback logic for a single resolved schedule slot.
    Dispatches to the correct engine (Block, Program, etc.) or plays simple content.
    """
    # Runtime import to avoid circular dependency
    from scripts.engines.blocks import play_block, play_program

    # Check for Block (Resolved)
    if result.wrapper and isinstance(result.wrapper, Block):
        return play_block(
            api, build_id, context, result.wrapper, resolver, config.logger,
            current_slot_tuple[0], current_slot_tuple[1],
            boss=boss, holiday_ctx=holiday_ctx, config=config, day_schedule=day_schedule
        )

    # Check for CommercialBreak wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, CommercialBreak):
        cb = result.wrapper
        return play_commercials(
            api, build_id, context, config, resolver, config.logger, boss, holiday_ctx,
            duration=cb.duration_seconds,
            content=cb.content,
            enabled=True,
            log_indent=""
        )
    
    # Check for Program wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, Program):
        return play_program(
            api, build_id, context, result.wrapper, resolver, config.logger, 
            boss, holiday_ctx, 
            current_slot_tuple[0], current_slot_tuple[1], config=config,
            day_schedule=day_schedule
        )

    # Handle Standard Content (Key or Fallback)
    final_content = result.resolved_content
    
    if final_content:
        config.logger.info(
            f"{context.current_time.strftime('%a %H:%M')} | {final_content} (Source: {result.source})"
        )

        # Apply Injections (Holiday -> Seasonal)
        res = apply_injections(
            final_content,
            config=config,
            resolver=resolver,
            boss=boss,
            holiday_ctx=holiday_ctx,
            logger=config.logger,
            source="schedule_slot"
        )
        final_content = res.resolved_content

        context = play_with_fallback(api, build_id, final_content, config.logger, context=context, count=1)
        
        # --- AUTO COMMERCIALS (CHANNEL LEVEL) ---
        if config.enable_commercials:
            slot_name = config.timeslot_reverse_map.get(current_slot_tuple)
            duration = config.timeslot_commercials.get(slot_name, config.commercial_duration)

            if duration > 0:
                play_commercials(
                    api, build_id, context, config, resolver, config.logger, boss, holiday_ctx,
                    duration=duration,
                    enabled=True
                )

    else:
        config.logger.warn(f"Skipping slot {current_slot_tuple} due to resolution failure.")
        
    return context