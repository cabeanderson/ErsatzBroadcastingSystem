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
    from scripts.engines.blocks import PlayoutSession

# Per-run cache of failed bumper searches.
# Key: (safe_title, tags_tuple)
# Value: True (meaning "we checked, and it doesn't exist")
# Reset at the start of each build via reset_bumper_failure_cache() so results
# never bleed across channels (which may use different global_filters) or grow
# unbounded across many builds in one process (e.g. the simulator).
BUMPER_FAILURE_CACHE = {}


def reset_bumper_failure_cache() -> None:
    """Clear the per-run bumper-existence cache. Called by ScheduleRunner.run()."""
    BUMPER_FAILURE_CACHE.clear()

# --- UNIFIED HELPERS ---

def play_generic_branding(session: "PlayoutSession", key: Optional[str], element_type: str) -> Any:
    """
    Generic helper to play a branding element like an intro or outro.
    Checks registry existence before attempting resolve/play.
    """
    if key and key in session.resolver.registry:
        try:
            resolved_key = session.resolver.resolve(key, session.boss)
            session.logger.info(f"   ↳ Playing {element_type}")
            session.context = play_item(session.api, session.build_id, resolved_key, session.logger)
        except Exception as e:
            session.logger.warn(f"Failed to play {element_type}: {e}")
    return session.context

def play_commercials(
    session: "PlayoutSession",
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
        return session.context

    # 1. Duration-based break (Priority)
    if duration > 0:
        # Use specific content pool if provided, else channel default
        ad_pool_key = content or session.config.commercial_content
        
        res = resolve_content(ad_pool_key, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger, parent_item=parent_item)
        filler_key = res.resolved_content
        
        if isinstance(filler_key, Fallback):
            filler_key = filler_key.primary

        if filler_key:
            target_dt = session.context.current_time + timedelta(seconds=duration)

            session.logger.info(f"{log_indent}☕ Commercials ({duration}s)")
            session.context = fill_until_time(session.api, session.build_id, session.context, session.logger, target_dt, filler_key=filler_key)
        else:
            session.logger.warn(f"Commercial break skipped: ad pool '{ad_pool_key}' could not be resolved.")
            
    # 2. Content-based break (Play specific item/block)
    elif content:
        res = resolve_content(content, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger, parent_item=parent_item)
        if res.resolved_content:
            session.logger.info(f"{log_indent}↳ Playing commercial block: {res.resolved_content}")
            session.context = play_item(session.api, session.build_id, res.resolved_content, session.logger)

    return session.context

def play_smart_bumper(session: "PlayoutSession", title: Optional[str], required_tags: List[str] = None, fallback_tags: List[List[str]] = None) -> Tuple[Any, bool]:
    """
    Attempts to play a smart bumper, with support for fallbacks and caching.
    
    Args:
        required_tags: Primary tags to check (e.g. ["marathon", "bumpers"])
        fallback_tags: List of tag lists to try if primary fails (e.g. [["bumpers"]])
    """
    if not title or not ENABLE_SMART_BUMPERS:
        return session.context, False

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
        
        session.resolver.register_dynamic_query(bumper_key, bumper_query)
        
        # 3. Try Play
        try:
            old_time = session.context.current_time
            # suppress_errors=True prevents log spam for expected failures
            session.context = play_item(session.api, session.build_id, bumper_key, session.logger, suppress_errors=True)
            
            if session.context.current_time > old_time:
                session.logger.info(f"   ↳ Playing smart bumper: {bumper_key}")
                return session.context, True
            else:
                # 4. Log Failure in Cache
                BUMPER_FAILURE_CACHE[cache_key] = True
                
        except Exception:
            BUMPER_FAILURE_CACHE[cache_key] = True
            pass
        
    return session.context, False

def play_bumper(
    session: "PlayoutSession",
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
        return session.context
        
    # Try Smart Bumper first
    # Extract title from content key
    base_key = content_key.primary if isinstance(content_key, Fallback) else content_key
    
    title = None
    data = session.resolver.get_query_data(base_key)
    if data is None:
        return session.context

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
        session.context, played_smart = play_smart_bumper(session, title, required_tags=req, fallback_tags=fallback_tags)
        
    # Fallback to generic bumper
    if not played_smart and bumper_key and bumper_key in session.resolver.registry:
        try:
            resolved_key = session.resolver.resolve(bumper_key, session.boss)
            session.logger.info(f"   ↳ Playing bumper: {resolved_key}")
            session.context = play_item(session.api, session.build_id, resolved_key, session.logger)
        except Exception as e:
            session.logger.warn(f"Failed to play bumper: {e}")
            
    return session.context

def fill_to_boundary(
    session: "PlayoutSession",
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
        session.logger.info(f"{log_indent}Fill Strategy: 'yield'. Stopping.")
        return session.context
        
    if not enabled and strategy == "fill":
        session.logger.info(f"{log_indent}Fill strategy 'fill' ignored, filler disabled.")
        return session.context

    boundary_dt = calculate_boundary_dt(session.context, start_hour, end_hour)
    
    if session.context.current_time < boundary_dt:
        target_ts = boundary_dt.strftime("%H:%M")

        if strategy == "gap":
            session.logger.info(f"{log_indent}Fill Strategy: 'gap'. Waiting until {target_ts}.")
            session.context = wait_until_time(session.api, session.build_id, session.context, session.logger, boundary_dt)

        elif strategy == "fill":
            # Resolve filler
            filler_to_use = filler_content or session.config.filler_content
            res = resolve_content(filler_to_use, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger, parent_item=parent_item)

            if res.resolved_content:
                session.logger.info(f"{log_indent}Fill Strategy: 'fill'. Filling with '{res.resolved_content}' until {target_ts}.")
                session.context = fill_until_time(session.api, session.build_id, session.context, session.logger, boundary_dt, filler_key=res.resolved_content)
            else:
                session.logger.warn(f"{log_indent}Fill Strategy: 'fill' failed, filler not resolved. Waiting instead.")
                session.context = wait_until_time(session.api, session.build_id, session.context, session.logger, boundary_dt)

        # SAFETY: Ensure we actually reached the boundary. pad_until_exact stops
        # before the boundary when no whole item fits, which is expected; this
        # closes the remainder so the Runner cannot spin on the same slot.
        if session.context.current_time < boundary_dt:
            session.logger.warn(f"{log_indent}⚠️ Fill/Pad didn't reach boundary. Forcing wait until {target_ts}.")
            session.context = wait_until_time(session.api, session.build_id, session.context, session.logger, boundary_dt)
    
    return session.context

def maintain_playout_invariants(session: "PlayoutSession", last_time: Any) -> Any:
    """
    Handles fallback logic, circuit breaking, and filler at hour boundaries.
    """
    # Resolve fallback content only if stalled
    fallback_key = None
    if session.context.current_time <= last_time and session.config.fallback_content:
        try:
            fb_res = resolve_content(session.config.fallback_content, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger)
            if isinstance(fb_res.resolved_content, str):
                fallback_key = fb_res.resolved_content
        except Exception as e:
            session.logger.warn(f"Failed to resolve fallback content: {e}")

    session.context = circuit_breaker(session.api, session.build_id, session.context, last_time, session.logger, fallback_content=fallback_key, skip_minutes=session.config.circuit_breaker_skip)

    if session.config.enable_filler and session.config.filler_content and is_approaching_hour_boundary(session.context):
        # Resolve filler content
        filler_result = resolve_content(session.config.filler_content, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger)
        filler_content = filler_result.resolved_content
        
        if isinstance(filler_content, Fallback):
            filler_content = filler_content.primary

        session.context = fill_until_next_hour(session.api, session.build_id, session.context, session.logger, filler_content)
        
    return session.context

# --- SLOT EXECUTION ---

def play_schedule_slot(
    session: "PlayoutSession",
    result: Any, 
    current_slot_tuple: Tuple[int, int],
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
        return play_block(session, result.wrapper, start_hour=current_slot_tuple[0], end_hour=current_slot_tuple[1], day_schedule=day_schedule)

    # Check for CommercialBreak wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, CommercialBreak):
        cb = result.wrapper
        return play_commercials(
            session,
            duration=cb.duration_seconds,
            content=cb.content,
            enabled=True,
            log_indent=""
        )
    
    # Check for Program wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, Program):
        return play_program(session, result.wrapper, start_hour=current_slot_tuple[0], end_hour=current_slot_tuple[1], day_schedule=day_schedule)

    # Handle Standard Content (Key or Fallback)
    final_content = result.resolved_content
    
    if final_content:
        session.logger.info(
            f"{session.context.current_time.strftime('%a %H:%M')} | {final_content} (Source: {result.source})"
        )

        # Apply Injections (Holiday -> Seasonal)
        res = apply_injections(final_content, config=session.config, resolver=session.resolver, boss=session.boss, holiday_ctx=session.holiday_ctx, logger=session.logger, source="schedule_slot")
        final_content = res.resolved_content

        session.context = play_with_fallback(session.api, session.build_id, final_content, session.logger, context=session.context, count=1)
        
        # --- AUTO COMMERCIALS (CHANNEL LEVEL) ---
        if session.config.enable_commercials:
            slot_name = session.config.timeslot_reverse_map.get(current_slot_tuple)
            duration = session.config.timeslot_commercials.get(slot_name, session.config.commercial_duration)

            if duration > 0:
                play_commercials(session, duration=duration, enabled=True)

    else:
        session.logger.warn(f"Skipping slot {current_slot_tuple} due to resolution failure.")
        
    return session.context