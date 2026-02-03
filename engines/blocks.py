# scripts/engines/blocks.py
"""
Branded programming blocks with optional intro/outro/bumpers.
Gracefully handles missing assets.
"""

import re
from datetime import timedelta
from typing import Any, Dict, Optional
from scripts.library import ContentResolver
from scripts.playout import play_item, toggle_marathon_branding, ChannelLogger, fill_until_time, play_with_fallback
from scripts.logic.models import BrandedBlock, Fallback, CommercialBreak
from scripts.logic.resolution import apply_holiday_injection


def play_block_intro(api: Any, build_id: str, context: Any, intro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """
    Helper to play a block intro if it exists in the registry.
    """
    if intro and intro in resolver.registry:
        try:
            intro_key = resolver.resolve(intro, boss)
            logger.info(f"   ↳ Playing intro")
            context = play_item(api, build_id, intro_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play intro: {e}")
    return context

def play_block_outro(api: Any, build_id: str, context: Any, outro: Optional[str], resolver: Any, logger: ChannelLogger, boss: Any = None) -> Any:
    """
    Helper to play a block outro if it exists in the registry.
    """
    if outro and outro in resolver.registry:
        try:
            outro_key = resolver.resolve(outro, boss)
            logger.info(f"   ↳ Playing outro")
            context = play_item(api, build_id, outro_key, logger)
        except Exception as e:
            logger.warn(f"Failed to play outro: {e}")
    return context

def play_branded_block(api: Any, build_id: str, context: Any, block: BrandedBlock, sources_registry: Dict[str, Any], logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any = None, holiday_ctx: Any = None) -> Any:
    """
    Play a branded programming block with optional intro/outro/bumpers.
    
    Args:
        api: ErsatzTV API instance
        build_id: Build UUID
        context: Current playout context
        block: BrandedBlock instance
        sources_registry: MASTER_SOURCES dict
        logger: ChannelLogger instance
        start_hour: Block start hour
        end_hour: Block end hour
        boss: DayDirector instance (optional, for injection)
        holiday_ctx: HolidayContext instance (optional, for injection)
    
    Returns:
        Updated context after block completes
    """
    resolver = ContentResolver(api, build_id, sources_registry, logger)
    
    logger.info(f"🎬 {block.name} ({start_hour}:00-{end_hour}:00)")
    
    # Start EPG group if enabled
    if block.use_epg_group:
        toggle_marathon_branding(api, build_id, name=block.name, start=True)
    
    # Play intro if it exists
    context = play_block_intro(api, build_id, context, block.intro, resolver, logger, boss)
    
    # Play main content
    last_time = context.current_time
    items_played = 0
    consecutive_failures = 0
    
    while not context.is_done:
        hour = context.current_time.hour
        
        # Check time bounds
        in_window = False
        if start_hour < end_hour:
            in_window = start_hour <= hour < end_hour
        else: # Wraps midnight
            in_window = hour >= start_hour or hour < end_hour
            
        if not in_window:
            logger.info(f"🕒 Block time window ended at {context.current_time.strftime('%H:%M')}")
            break
        
        # Play content
        try:
            content_key = resolver.resolve(block.content, boss)
            if content_key is None:
                logger.warn(f"Resolver returned None for block content. Skipping.")
                consecutive_failures += 1
                continue
            
            # Apply holiday injection if context is available
            if boss and holiday_ctx:
                # apply_holiday_injection now returns ResolutionResult
                result = apply_holiday_injection(content_key, resolver, holiday_ctx, boss, logger)
                content_key = result.resolved_content

        except Exception as e:
            logger.warn(f"Error resolving content: {e}")
            consecutive_failures += 1
            continue

        # Handle CommercialBreak objects (from collections)
        if isinstance(content_key, CommercialBreak):
            # Resolve commercial content
            comm_key = resolver.resolve(content_key.content, boss)
            
            target_dt = context.current_time + timedelta(seconds=content_key.duration_seconds)
            target_time_str = target_dt.strftime("%H:%M")
            is_tomorrow = target_dt.day > context.current_time.day
            
            logger.info(f"   ☕ Commercial Break ({content_key.duration_seconds}s)")
            context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=comm_key, tomorrow=is_tomorrow)
            last_time = context.current_time
            continue

        # Log content for visibility
        display_key = content_key
        if isinstance(content_key, Fallback):
            display_key = f"{content_key.primary} (fallback: {content_key.secondary})"
        elif isinstance(content_key, tuple):
            display_key = f"{content_key[0]} (fallback: {content_key[1]})"
        logger.info(f"{context.current_time.strftime('%H:%M')} | {display_key}")
            
        # Determine base key for intro lookup (unwrap Fallback/tuple)
        base_key = content_key
        if isinstance(content_key, Fallback):
            base_key = content_key.secondary
        elif isinstance(content_key, tuple):
            base_key = content_key[1]
            
        # Check for specific intro (Explicit or Auto-discovered)
        intro_key = None
        is_dynamic_intro = False
        
        specific_intros = getattr(block, "specific_intros", None)
        if specific_intros and base_key in specific_intros:
            intro_key = specific_intros[base_key]
        elif isinstance(base_key, str):
            # 1. Try explicit key convention (cowboy_bebop_tv -> cowboy_bebop_intro)
            candidate = None
            if base_key.endswith("_tv"):
                candidate = base_key.replace("_tv", "_intro")
            elif base_key.endswith("_movie"):
                candidate = base_key.replace("_movie", "_intro")
            
            if candidate and candidate in sources_registry:
                intro_key = candidate
            
            # 2. Try dynamic generation from title
            if not intro_key and base_key in sources_registry:
                source_data = sources_registry[base_key]
                query = None
                if isinstance(source_data, dict):
                    query = source_data.get("query")
                elif isinstance(source_data, str):
                    query = source_data
                
                if query:
                    # Extract title from query (show_title:"..." or title:"...")
                    # Handles: title:"Foo Bar" and title:Foo
                    match = re.search(r'(?:show_)?title:(?:"([^"]+)"|([^\s]+))', query)
                    if match:
                        title = match.group(1) or match.group(2)
                        # Create a dynamic key for this specific show intro
                        # Sanitize title for key
                        safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()
                        dyn_key = f"auto_intro_{safe_title}"
                        
                        # Construct query: type:"other_videos" AND tag:"Title" AND (tag:intro OR tag:bumper)
                        dyn_query = f'type:"other_video" AND tag:"{title}" AND (tag:intro OR tag:bumper)'
                        
                        resolver.register_dynamic_query(dyn_key, dyn_query)
                        intro_key = dyn_key
                        is_dynamic_intro = True

        if intro_key and (intro_key in sources_registry or intro_key in resolver.active_keys):
            logger.info(f"   ↳ Playing intro: {intro_key}")
            # Note: We don't inject flavor into specific intros as they are usually show-specific
            try:
                context = play_item(api, build_id, intro_key, logger, suppress_errors=is_dynamic_intro)
            except Exception as e:
                logger.warn(f"Failed to play specific intro: {e}")

        # Handle content playback
        try:
            context = play_with_fallback(api, build_id, content_key, logger, context=context)
        except Exception as e:
            logger.warn(f"Failed to play content '{content_key}': {e}")
            # Fall through to progress check
        
        # Check progress
        if context.current_time <= last_time:
            logger.warn(f"Content '{content_key}' failed to advance time (missing/invalid?)")
            consecutive_failures += 1
            if consecutive_failures >= 5:
                logger.warn(f"🛑 Too many consecutive failures. Aborting block.")
                break
            continue # Try next item
        
        consecutive_failures = 0 # Reset on success
        last_time = context.current_time
        items_played += 1
        
        # Play Auto Commercials (if configured)
        if block.commercials_between_items > 0:
            # Resolve commercial content using resolver (handles collections and registration)
            comm_key = resolver.resolve(block.commercial_content, boss)
            
            if comm_key:
                target_dt = context.current_time + timedelta(seconds=block.commercials_between_items)
                target_time_str = target_dt.strftime("%H:%M")
                is_tomorrow = target_dt.day > context.current_time.day
                
                logger.info(f"   ☕ Auto Commercials ({block.commercials_between_items}s)")
                context = fill_until_time(api, build_id, context, logger, target_time_str, filler_key=comm_key, tomorrow=is_tomorrow)
        
        # Play bumper between items (if exists and not last item)
        if block.bumpers:
            if block.bumpers not in sources_registry:
                logger.warn(f"Bumper key '{block.bumpers}' not found in registry")
            else:
                # Check if we are still within the block's window
                h = context.current_time.hour
                still_in_window = False
                
                if start_hour < end_hour:
                    still_in_window = start_hour <= h < end_hour
                else: # Wraps midnight
                    still_in_window = h >= start_hour or h < end_hour
                
                if still_in_window:
                    try:
                        bumper_key = resolver.resolve(block.bumpers, boss)
                        logger.info(f"   ↳ Playing bumper: {bumper_key}")
                        old_time = context.current_time
                        context = play_item(api, build_id, bumper_key, logger)
                        if context.current_time <= old_time:
                            logger.warn(f"Bumper played but time didn't advance (0 duration? Check query results)")
                    except Exception as e:
                        logger.warn(f"Failed to play bumper: {e}")
    
    # Play outro if it exists and we are at the end of the window
    if block.outro:
        h = context.current_time.hour
        if start_hour < end_hour:
            should_play = h < end_hour or (h == end_hour and context.current_time.minute < 15)
        else: # Wraps midnight
            should_play = h >= start_hour or h < end_hour or (h == end_hour and context.current_time.minute < 15)
        if should_play:
            context = play_block_outro(api, build_id, context, block.outro, resolver, logger, boss)
    
    # End EPG group
    if block.use_epg_group:
        toggle_marathon_branding(api, build_id, start=False)
    
    logger.info(f"🏁 {block.name} - {items_played} items played")
    
    return context