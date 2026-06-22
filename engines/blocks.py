# scripts/engines/blocks.py
"""
Unified Program and Block Engine.
"""

from dataclasses import dataclass
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
    from scripts.core import DayDirector
    from scripts.logic.calendar.holidays import HolidayContext
    from scripts.scheduling.config import ScheduleConfig

MAX_BRIDGE_DEPTH = 5  # Safety limit for recursive bridging

@dataclass
class PlayoutSession:
    """Groups common objects used throughout a playout session."""
    api: Any
    build_id: str
    context: Any
    resolver: "ContentResolver"
    logger: ChannelLogger
    boss: "DayDirector"
    holiday_ctx: "HolidayContext"
    config: "ScheduleConfig"

def _get_next_block_item(block: Block, items_played: int, boss: "DayDirector") -> Optional[Any]:
    """Selects the next item from a block's iterator, handling collections and lists."""
    iterator = block.items
    is_collection = hasattr(iterator, "pick")

    if is_collection:
        return iterator.pick(boss)
    
    if isinstance(iterator, list) and items_played < len(iterator):
        return iterator[items_played]
    
    return None # Exhausted

def play_block_intro(session: PlayoutSession, intro: Optional[str]) -> Any:
    """Helper to play a block intro."""
    return play_generic_branding(session, intro, "intro")

def play_block_outro(session: PlayoutSession, outro: Optional[str]) -> Any:
    """Helper to play a block outro."""
    return play_generic_branding(session, outro, "outro")

def play_block(session: PlayoutSession, item: Union[Block, Program], start_hour: int, end_hour: int, day_schedule: Optional[Dict[Tuple[int, int], Any]] = None, force_end_hour: Optional[int] = None, ignore_start_window: bool = False, bridge_depth: int = 0) -> Any:
    """Unified engine to play a Block or a single Program."""
    # Resolver is passed in to maintain active_keys cache
    if isinstance(item, Program):
        return play_program(session, item, start_hour, end_hour, day_schedule=day_schedule, force_end_hour=force_end_hour, ignore_start_window=ignore_start_window, bridge_depth=bridge_depth)
    
    if isinstance(item, Block):
        return _play_block_internal(session, item, start_hour, end_hour, day_schedule=day_schedule, force_end_hour=force_end_hour, ignore_start_window=ignore_start_window, bridge_depth=bridge_depth)

    session.logger.warn(f"play_block received an unsupported type: {type(item)}")
    return session.context

def _play_block_internal(session: PlayoutSession, block: Block, start_hour: int, end_hour: int, day_schedule: Optional[Dict[Tuple[int, int], Any]] = None, force_end_hour: Optional[int] = None, ignore_start_window: bool = False, bridge_depth: int = 0) -> Any:
    """Internal logic to play a Block object (a container of Programs/content)."""
    from scripts.logic.resolution.playback import calculate_boundary_dt
    effective_end_hour = force_end_hour if force_end_hour is not None else end_hour
    log_suffix = f" (Forced stop at {effective_end_hour}:00)" if force_end_hour is not None else ""
    session.logger.info(f"🎬 {block.name} ({start_hour}:00-{end_hour}:00){log_suffix}")

    # Resolve features and context
    bumpers_enabled = resolve_feature(None, block.enable_bumpers, session.config.enable_bumpers)
    slot_name = session.config.timeslot_reverse_map.get((start_hour, end_hour))
    
    # Check for strict window adherence (Default: True)
    # True = Hard Stop: Block ends exactly when the timeslot ends (cutting off content if needed).
    # False = Soft Stop: Block allows the current item to finish even if it overflows the timeslot.
    strict_window = getattr(block, 'strict_window', True)

    # If this is a bridged block, it must adhere to the hard stop time.
    if ignore_start_window:
        strict_window = True

    boundary_dt = calculate_boundary_dt(session.context, start_hour, effective_end_hour)

    items_played = 0
    epg_name = block.name if block.use_epg_group else None
    with epg_group(session.api, session.build_id, epg_name):
        if bumpers_enabled: session.context = play_block_intro(session, block.intro)
        
        last_time = session.context.current_time
        
        while not session.context.is_done:
            # Check if we've passed the boundary for this block.
            if strict_window:
                if session.context.current_time >= boundary_dt:
                    session.logger.info(f"🕒 Block time window ended at {session.context.current_time.strftime('%H:%M')}")
                    break
                
            item_to_play = _get_next_block_item(block, items_played, session.boss)
            if item_to_play is None:
                session.logger.info("Block items exhausted.")
                break
            
            # --- Implicit Program Refactor ---
            # Dispatch based on the type of item. Raw items are wrapped in an implicit Program.

            # Handle nested blocks (error case)
            if isinstance(item_to_play, Block):
                session.logger.error(f"❌ Block '{block.name}' attempted to play nested Block '{item_to_play.name}'. This is not supported. Skipping.")
                continue

            # Handle CommercialBreak objects directly
            if isinstance(item_to_play, CommercialBreak):
                session.context = _handle_block_item_commercial_break(session, item_to_play, block) or session.context
            
            # Handle explicit Program objects
            elif isinstance(item_to_play, Program):
                session.context = play_program(session, item_to_play, start_hour, effective_end_hour, parent_block=block, day_schedule=day_schedule)
            
            # All other items (strings, dicts, collections) are wrapped in an implicit Program.
            else:
                program_name = str(item_to_play) if isinstance(item_to_play, str) else getattr(item_to_play, 'name', 'Unnamed Item')
                implicit_program = Program(
                    name=f"Item: {program_name}",
                    content=item_to_play,
                )
                session.context = play_program(session, implicit_program, start_hour, effective_end_hour, parent_block=block, day_schedule=day_schedule, bridge_depth=bridge_depth)

            items_played += 1
            
            session.context = circuit_breaker(session.api, session.build_id, session.context, last_time, session.logger, fallback_content=session.config.fallback_content, skip_minutes=session.config.circuit_breaker_skip)
            if session.context.current_time <= last_time:
                session.logger.warn("Block item failed to advance time. Breaking block.")
                break
            last_time = session.context.current_time

        # After loop, handle fill strategy for the block itself
        if block.fill_strategy == "bridge":
            session.context = _bridge_to_next_slot(session, (start_hour, effective_end_hour), day_schedule, bridge_depth=bridge_depth)
        else:
            # Always fill/wait to boundary if we finished early, to prevent Runner from re-scheduling this slot.
            # strict_window=False allows OVERflow, but we must handle UNDERflow.
            session.context = fill_to_boundary(session, start_hour, effective_end_hour, strategy=block.fill_strategy, filler_content=block.filler, log_indent="   ", parent_item=block)

        if bumpers_enabled: session.context = play_block_outro(session, block.outro)
    session.logger.info(f"🏁 {block.name} - {items_played} items played")
    return session.context

def _bridge_to_next_slot(
    session: PlayoutSession, current_slot_tuple: Tuple[int, int], day_schedule: Dict[Tuple[int, int], Any], bridge_depth: int = 0
) -> Any:
    """Fills the rest of a slot with content from the *next* scheduled block."""
    from scripts.logic.resolution.playback import calculate_boundary_dt

    start, end = current_slot_tuple
    boundary_dt = calculate_boundary_dt(session.context, start, end)

    # 1. Safety Check: Recursion Depth
    if bridge_depth >= MAX_BRIDGE_DEPTH:
        session.logger.warn(f"🛑 Max bridge depth ({MAX_BRIDGE_DEPTH}) reached. Stopping recursion to prevent infinite loop.")
        next_slot_item = None
        next_slot_tuple = None
    else:
        # 2. Find the next slot in the schedule
        next_slot_tuple = None
        next_slot_item = None
        if day_schedule:
            lookup_start = 0 if end == 24 else end
            for (s, e), entry in sorted(day_schedule.items()):
                if s == lookup_start:
                    next_slot_tuple = (s, e)
                    next_slot_item = entry
                    break

    if next_slot_item and next_slot_tuple:
        session.logger.info(f"  Bridging to next block. Handing off to playout engine. Hard stop at {end}:00")
        # Recursively call the main block player with the next item.
        # Pass our current slot's end time as a "force_end_hour" to ensure it stops on the boundary.
        # Also, tell it to ignore its own start time window, since we are starting it early.
        session.context = play_block(
            session, next_slot_item,
            start_hour=next_slot_tuple[0],
            end_hour=next_slot_tuple[1],
            day_schedule=day_schedule,
            ignore_start_window=True,
            bridge_depth=bridge_depth + 1
        )
    
    # After the bridge attempt (recursive call or not), we must ensure we are at the boundary.
    # This handles cases where there was no next block, or the bridged block finished early.
    if session.context.current_time < boundary_dt:
        session.logger.info(f"  Bridge handoff complete or skipped. Filling remaining gap until {boundary_dt.strftime('%H:%M')}.")
        session.context = fill_to_boundary(session, start, end, strategy="fill", log_indent="     ")

    return session.context

def _resolve_and_prepare_program_content(
    session: PlayoutSession, program: Program
) -> Tuple[Optional[Any], int]:
    """
    Resolves program content, handling Appointment TV scheduling and static content.
    Returns the content key and the number of items to play.
    """
    # 1. Appointment TV (Scheduled Content)
    scheduled_result = resolve_scheduled_content(program, session.boss.now.date())
    if scheduled_result:
        key, ep_count, ep_num = scheduled_result
        ep_per_slot = program.scheduling.get("episodes_per_slot", 1)
        end_ep = min(ep_num + ep_per_slot - 1, ep_count)
        ep_str = f"{ep_num}" if ep_num == end_ep else f"{ep_num}-{end_ep}"
        session.logger.info(f"     Scheduling active: Playing '{key}' (Episode {ep_str}/{ep_count})")
        
        content_key, count = session.resolver.resolve(key), ep_per_slot
        
        # Attempt to skip to the exact episode for robust playback
        try:
            q_data = session.resolver.get_query_data(key)
            query = q_data.get("query") if isinstance(q_data, dict) else q_data
            if query and (q_season := extract_episode_range(query)[0]) is not None:
                session.api.skip_to_item(session.build_id, ControlSkipToItem(content=key, season=q_season, episode=ep_num))
        except Exception as e: 
            session.logger.warn(f"Failed to force sequence for '{key}': {e}")

        return content_key, count

    # 2. Static Content
    session.logger.info(f"     Playing static content for '{program.name}'")
    res = resolve_content(program.content, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger, parent_item=program)
    
    content_key = res.resolved_content
    count = program.play_count or 1

    # Handle start_point for static content (marathon-converted programs)
    if program.start_point and isinstance(program.start_point, tuple) and len(program.start_point) == 2:
        season, episode = program.start_point
        try:
            session.api.skip_to_item(session.build_id, ControlSkipToItem(content=content_key, season=season, episode=episode))
        except Exception as e:
            session.logger.warn(f"Failed to force sequence for '{content_key}' via start_point: {e}")

    return content_key, count

def _handle_program_bumpers(
    session: PlayoutSession, program: Program, parent_block: Optional[Block], content_key: str, enabled: bool
) -> Any:
    """Helper to resolve and play bumpers for a program."""
    bumper_key = resolve_bumper_collection(program, parent_block, session.config)
    return play_bumper(session, content_key, bumper_key=bumper_key, enabled=enabled)

def _handle_program_commercials(
    session: PlayoutSession, program: Program, parent_block: Optional[Block], slot_name: Optional[str]
) -> Any:
    """Helper to resolve and play commercials for a program."""
    block_commercials = parent_block.enable_commercials if parent_block else None
    comm_duration = resolve_commercial_duration(program, parent_block, session.config, slot_name=slot_name)
    commercials_enabled = resolve_feature(program.enable_commercials, block_commercials, session.config.enable_commercials)
    
    return play_commercials(
        session,
        duration=comm_duration, content=program.commercials, enabled=commercials_enabled,
        log_indent="     ", parent_item=program
    )

def _handle_program_filler(
    session: PlayoutSession, program: Program, parent_block: Optional[Block], start_hour: int, end_hour: int
) -> Any:
    """Helper to resolve and play filler for a program."""
    # Check parent block strictness - Special Blocks shouldn't fill gaps
    if parent_block and not getattr(parent_block, 'strict_window', True):
        return session.context

    block_filler = parent_block.enable_filler if parent_block and hasattr(parent_block, 'enable_filler') else None
    filler_enabled = resolve_feature(program.enable_filler, block_filler, session.config.enable_filler)
    filler_content = resolve_filler_content(program, parent_block, session.config)
    
    return fill_to_boundary(
        session,
        start_hour, end_hour, strategy=program.fill_strategy, filler_content=filler_content,
        enabled=filler_enabled, log_indent="     ", parent_item=program
    )

def play_program(session: PlayoutSession, program: Program, start_hour: int, end_hour: int, parent_block: Optional[Block] = None, day_schedule: Optional[Dict[Tuple[int, int], Any]] = None, force_end_hour: Optional[int] = None, ignore_start_window: bool = False, bridge_depth: int = 0) -> Any:
    """Executes a Program. Handles scheduling, branding, content playback, and fill strategy."""
    effective_end_hour = force_end_hour if force_end_hour is not None else end_hour
    log_suffix = f" (Forced stop at {effective_end_hour}:00)" if force_end_hour is not None else ""
    session.logger.info(f"   ▶ Program: {program.name} ({start_hour}:00-{end_hour}:00){log_suffix}")
    
    # Resolve features and context
    block_bumpers = parent_block.enable_bumpers if parent_block else None
    bumpers_enabled = resolve_feature(program.enable_bumpers, block_bumpers, session.config.enable_bumpers)
    slot_name = session.config.timeslot_reverse_map.get((start_hour, end_hour))

    content_key, count = _resolve_and_prepare_program_content(session, program)

    if not content_key: 
        session.logger.warn(f"Could not resolve content for Program '{program.name}'. Skipping.")
        return session.context

    # Apply Injections (Holiday -> Seasonal)
    res = apply_injections(content_key, program=program, block=parent_block, config=session.config, resolver=session.resolver, boss=session.boss, holiday_ctx=session.holiday_ctx, logger=session.logger, source="program")

    content_key = res.resolved_content

    if bumpers_enabled: 
        session.context = play_block_intro(session, program.intro)

    session.context = _handle_program_bumpers(session, program, parent_block, content_key, bumpers_enabled)

    last_time = session.context.current_time
    session.context = play_with_fallback(session.api, session.build_id, content_key, session.logger, context=session.context, count=count)
    
    session.context = _handle_program_commercials(session, program, parent_block, slot_name)

    effective_end_hour = force_end_hour if force_end_hour is not None else end_hour
    if session.context.current_time > last_time:
        if program.fill_strategy == "bridge":
            session.context = _bridge_to_next_slot(session, (start_hour, effective_end_hour), day_schedule, bridge_depth=bridge_depth)
        else:
            session.context = _handle_program_filler(session, program, parent_block, start_hour, effective_end_hour)

    if bumpers_enabled: 
        session.context = play_block_outro(session, program.outro)
    return session.context

def _handle_block_item_commercial_break(
    session: PlayoutSession, cb: CommercialBreak, block: Block
) -> Optional[Any]:
    """Handles a CommercialBreak object found as an item in a block."""
    # Resolve the content of the break
    cb_res = resolve_content(cb.content, session.boss, session.holiday_ctx, session.config, session.resolver, session.logger, parent_item=block)
    cb_key = cb_res.resolved_content
    
    if isinstance(cb_key, Fallback):
        cb_key = cb_key.primary
        
    if cb.duration_seconds > 0:
        target_dt = session.context.current_time + timedelta(seconds=cb.duration_seconds)
        target_time_str = target_dt.strftime("%H:%M")
        is_tomorrow = target_dt.day > session.context.current_time.day
        
        session.logger.info(f"   ☕ Block Item: Commercial Break ({cb.duration_seconds}s)")
        return fill_until_time(session.api, session.build_id, session.context, session.logger, target_time_str, filler_key=cb_key, tomorrow=is_tomorrow)
    
    # If duration is 0, fall through by returning None
    return None