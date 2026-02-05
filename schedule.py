"""
The Architect - Orchestrates daily channel flow.
Coordinates time, rules, and intent without touching physical execution.

RESOLUTION ORDER (enforced):
1. Find time window
2. Resolve day-of-week override
3. Resolve SeasonalBlock
4. Resolve holiday override
5. Resolve seasonal_blocks reference
6. Send final string to playout
"""

from datetime import timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from scripts.core import DayDirector
from scripts.logic.holidays import HolidayContext
from scripts.logic.resolution import resolve_target
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic.playback import is_approaching_hour_boundary, hour_in_window
from scripts.engines.slots import (
    handle_single_play_slot
)
from scripts.logic.resolver import ContentResolver
from scripts.core.logger import ChannelLogger
from scripts.playout import (
    circuit_breaker,
    fill_until_time,
    play_item, play_with_fallback, fill_until_next_hour
)
from scripts.engines import run_marathon, play_block, play_program
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.timeslots import (
    DEFAULT_TIMESLOTS, ALT_TIMESLOTS, 
    expand_timeslots, get_timeslot_map
)
from scripts.logic.models import (
    Marathon, MarathonDefinition, BlockProfile, HolidayProfile, PlayOnce, Fallback, Swap, Feather, CommercialBreak
)
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.logic.structures import Block, Program, MarathonSequence
from scripts.config import ENABLE_SEASONAL_BLOCKS

# 5. SCHEDULE CONFIGURATION

class ScheduleConfig:
    def __init__(
        self,
        schedules: Dict[str, Any],
        marathons: Optional[List[Marathon]] = None,
        seasonal_blocks: Optional[Dict[str, Dict[str, Any]]] = None,
        timeslot_preset: Union[str, Dict[str, Tuple[int, int]]] = "default",
        custom_timeslots: Optional[Dict[str, Tuple[int, int]]] = None,
        single_play_slots: Optional[List[str]] = None,
        global_holiday_overrides: Optional[Dict[str, Any]] = None,
        global_seasonal_ramps: Optional[Dict[str, Dict[str, Any]]] = None,
        holiday_schedules: Optional[Dict[str, Dict[str, Any]]] = None,
        block_profiles: Optional[Dict[str, Any]] = None,
        filler_content: Optional[Any] = None,
        logger: Optional[ChannelLogger] = None,
        fallback_content: Optional[Any] = None,
        commercials_between_items: int = 0,
        commercial_content: Any = "commercials_spot",
        commercial_duration: int = 0,
    ):
        # Resolve timeslots map locally to handle single_play_slots resolution
        timeslots = get_timeslot_map(timeslot_preset, custom_timeslots)

        self.schedules = {
            k: expand_timeslots(v, timeslot_preset, custom_timeslots)
            for k, v in schedules.items()
        }
        self.marathons = marathons or []
        self.seasonal_blocks = seasonal_blocks or {}
        
        self.single_play_tuples = set()
        if single_play_slots:
            for name in single_play_slots:
                if name in timeslots:
                    self.single_play_tuples.add(timeslots[name])

        self.global_holiday_overrides = global_holiday_overrides
        self.global_seasonal_ramps = global_seasonal_ramps
        
        self.holiday_schedules = {}
        if holiday_schedules:
            self.holiday_schedules = {
                k: expand_timeslots(v, timeslot_preset, custom_timeslots)
                for k, v in holiday_schedules.items()
            }
        
        # Merge custom profiles with global defaults
        # Custom overrides take precedence
        self.block_profiles = {**HOLIDAY_PROFILES, **(block_profiles or {})}

        self.filler_content = filler_content
        self.logger = logger or ChannelLogger() # Default to a basic logger
        self.fallback_content = fallback_content
        # Support both old and new naming, prefer new
        self.commercial_duration = commercial_duration or commercials_between_items
        self.commercial_content = commercial_content
        self.commercials_between_items = self.commercial_duration # Backwards compat alias


# 6. PRE-REGISTRATION (CRITICAL)

def pre_register_all_content(resolver: ContentResolver, config: ScheduleConfig) -> None:
    """Register all content before playout begins."""
    visited = set()
    
    # Create a dummy boss for collections that need it during pre-registration
    class DummyContext:
        def __init__(self):
            from datetime import datetime
            self.current_time = datetime.now()
    dummy_boss = DayDirector(DummyContext())

    def walk(obj: Any, depth: int = 0) -> None:
        if obj is None or depth > 10:  # Prevent infinite recursion
            return

        # Optimization: Avoid re-walking shared objects (Collections, Blocks, Dicts)
        if id(obj) in visited:
            return
        visited.add(id(obj))

        if isinstance(obj, SeasonalBlock) or (hasattr(obj, 'base') and hasattr(obj, 'seasonal')):
            walk(obj.base, depth + 1)
            walk(obj.seasonal, depth + 1)
            return

        if isinstance(obj, (Swap, Feather)):
            walk(obj.content, depth + 1)
            return

        if isinstance(obj, PlayOnce):
            walk(obj.content, depth + 1)
            return
        
        if isinstance(obj, CommercialBreak):
            walk(obj.content, depth + 1)
            return
        
        if isinstance(obj, Fallback):
            walk(obj.primary, depth + 1)
            walk(obj.secondary, depth + 1)
            return

        if isinstance(obj, Block):
            walk(obj.items, depth + 1)
            if obj.intro: resolver.resolve(obj.intro)
            if obj.outro: resolver.resolve(obj.outro)
            if obj.bumpers: resolver.resolve(obj.bumpers)
            return
            
        if isinstance(obj, Program):
            walk(obj.content, depth + 1)
            walk(obj.filler, depth + 1)
            if obj.intro: resolver.resolve(obj.intro)
            if obj.outro: resolver.resolve(obj.outro)
            if obj.scheduling and "generated_queries" in obj.scheduling:
                for key, query in obj.scheduling["generated_queries"].items():
                    config.logger.debug(f"Pre-registering Program query: {key}")
                    resolver.register_dynamic_query(key, query, order="Chronological")
            return

        # Skip seasonal block references (strings in seasonal_blocks dict)
        if isinstance(obj, str) and obj in config.seasonal_blocks:
            # Don't try to register seasonal block names
            return

        # Handle Collections without triggering side effects (like advancing index)
        if hasattr(obj, "items") and hasattr(obj, "pick"):
            for item in obj.items:
                # Check if it's specifically a WeightedCollection tuple
                if isinstance(item, tuple) and len(item) == 2:
                    key, weight = item
                    # Only treat as weighted if weight is numeric
                    if isinstance(weight, (int, float)):
                        walk(key, depth + 1)
                    else:
                        # It's some other tuple, walk both elements
                        walk(key, depth + 1)
                        walk(weight, depth + 1)
                else:
                    walk(item, depth + 1)
            return

        if hasattr(obj, "pick"):
            resolver.resolve(obj, dummy_boss)
            return

        if isinstance(obj, (list, tuple, set)):
            for o in obj:
                walk(o, depth + 1)
            return

        if isinstance(obj, dict):
            # Special handling for inline content definitions (e.g. {"title": "Show"})
            # Resolve them directly to generate the key, instead of walking values
            if "title" in obj:
                resolver.resolve(obj, dummy_boss)
                return

            for v in obj.values():
                walk(v, depth + 1)
            return

        if isinstance(obj, str):
            # Only register if it's not a seasonal block reference
            if obj not in config.seasonal_blocks:
                resolver.resolve(obj, dummy_boss)

    walk(config.schedules)
    walk(config.seasonal_blocks)
    walk(config.fallback_content)
    walk(config.holiday_schedules)
    walk(config.commercial_content)

    for m in config.marathons:
        walk(m.collection)

def _resolve_day_schedule(config: ScheduleConfig, boss: DayDirector, holiday_ctx: HolidayContext) -> Dict[str, Any]:
    """
    Constructs the effective schedule for the day by applying:
    1. Day-of-week selection
    2. Global seasonal ramps
    3. Holiday schedule swaps/overrides
    """
    # 1. Determine base day schedule
    day_schedule = config.schedules.get("WEEKDAY", {})
    for key in config.schedules:
        if key != "WEEKDAY" and boss.has(key):
            day_schedule = config.schedules[key]
            break
    
    # Copy to avoid mutating master config
    day_schedule = day_schedule.copy()

    # 2. Apply global seasonal ramps
    if config.global_seasonal_ramps and ENABLE_SEASONAL_BLOCKS:
        active_ramp = False
        for holiday_name in config.global_seasonal_ramps:
            if holiday_ctx.envelope.get(holiday_name.lower(), 0.0) > 0 or \
               holiday_ctx.envelope.get(f"{holiday_name.lower()}_hangover", 0.0) > 0:
                active_ramp = True
                break
        
        if active_ramp:
            def wrap_values(d):
                return {k: wrap_values(v) if isinstance(v, dict) 
                        else SeasonalBlock(base=v, seasonal=config.global_seasonal_ramps, blend_ratio=1.0) 
                        for k, v in d.items()}
            day_schedule = wrap_values(day_schedule)

    # 3. Apply Holiday Schedule Swaps
    if config.holiday_schedules:
        for holiday_name, holiday_sched in config.holiday_schedules.items():
            holiday_label = holiday_name.upper()
            holiday_key = holiday_name.lower()
            is_holiday_day = boss.has(holiday_label)
            
            # Resolve Profile Set
            # Check if we have a HolidayProfile object or a raw dict
            profile_obj = config.block_profiles.get(holiday_label, config.block_profiles.get("default"))
            
            if isinstance(profile_obj, HolidayProfile):
                profile_set = profile_obj.blocks
            elif isinstance(profile_obj, dict):
                profile_set = profile_obj
            else:
                profile_set = {}

            for slot, content in holiday_sched.items():
                if slot not in day_schedule:
                    continue

                if is_holiday_day:
                    day_schedule[slot] = content
                    continue

                profile = profile_set.get(slot, BlockProfile())
                ramp_signal = holiday_ctx.envelope.get(holiday_key, 0.0)
                hangover_signal = holiday_ctx.envelope.get(f"{holiday_key}_hangover", 0.0)
                final_prob = profile.respond(ramp_signal, hangover_signal)
                
                if final_prob > 0 and boss.roll(final_prob, key=f"swap_{holiday_key}_{slot}"):
                    day_schedule[slot] = content
                    
    return day_schedule

def _play_schedule_slot(api: Any, build_id: str, context: Any, result: Any, current_slot_tuple: Tuple[int, int], day_schedule: Dict[Tuple[int, int], Any], config: ScheduleConfig, resolver: ContentResolver, boss: DayDirector, holiday_ctx: HolidayContext) -> Any:
    """
    Handles the playback logic for a single resolved schedule slot.
    Dispatches to the correct engine (Block, Program, etc.) or plays simple content.
    """
    # Check for Block (Resolved)
    if result.wrapper and isinstance(result.wrapper, Block):
        return play_block(
            api, build_id, context, result.wrapper, MASTER_SOURCES, config.logger,
            current_slot_tuple[0], current_slot_tuple[1],
            boss=boss,
            holiday_ctx=holiday_ctx,
            config=config
        )

    # Check for PlayOnce wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, PlayOnce):
        # Play once
        play_once = result.wrapper
        
        # Standard single item
        real_result = resolve_target(play_once.content, boss, holiday_ctx, config, resolver, config.logger)
        if real_result:
            context = play_with_fallback(api, build_id, real_result.resolved_content, config.logger, context=context, count=1)
        else:
            config.logger.warn(f"Skipping PlayOnce slot {current_slot_tuple} due to resolution failure.")
        
        # Fill rest with next block
        return handle_single_play_slot(
            api, build_id, context, current_slot_tuple,
            day_schedule, boss, holiday_ctx, config, resolver, config.logger
        )

    # Check for CommercialBreak wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, CommercialBreak):
        cb = result.wrapper
        # Resolve the content of the break (e.g. "commercials_spot")
        cb_res = resolve_target(cb.content, boss, holiday_ctx, config, resolver, config.logger)
        cb_key = cb_res.resolved_content
        
        if isinstance(cb_key, Fallback):
            cb_key = cb_key.primary

        target_dt = context.current_time + timedelta(seconds=cb.duration_seconds)
        target_time_str = target_dt.strftime("%H:%M")
        is_tomorrow = target_dt.day > context.current_time.day
        
        config.logger.info(f"☕ Commercial Break ({cb.duration_seconds}s) until {target_time_str}")
        
        return fill_until_time(
            api, build_id, context, config.logger, target_time_str, filler_key=cb_key, tomorrow=is_tomorrow
        )
    
    # Check for Program wrapper (Resolved)
    if result.wrapper and isinstance(result.wrapper, Program):
        return play_program(
            api, build_id, context, result.wrapper, resolver, config.logger, 
            boss, holiday_ctx, 
            current_slot_tuple[0], current_slot_tuple[1],
            config=config
        )

    # Handle Standard Content (Key or Fallback)
    final_content = result.resolved_content
    
    if final_content:
        config.logger.info(
            f"{context.current_time.strftime('%a %H:%M')} | {final_content} (Source: {result.source})"
        )

        context = play_with_fallback(api, build_id, final_content, config.logger, context=context, count=1)
        
        # --- AUTO COMMERCIALS (CHANNEL LEVEL) ---
        if config.commercial_duration > 0:
            # Resolve commercial content
            comm_res = resolve_target(config.commercial_content, boss, holiday_ctx, config, resolver, config.logger)
            comm_key = comm_res.resolved_content
            if isinstance(comm_key, Fallback):
                comm_key = comm_key.primary

            target_dt = context.current_time + timedelta(seconds=config.commercial_duration)
            target_time_str = target_dt.strftime("%H:%M")
            is_tomorrow = target_dt.day > context.current_time.day
            
            config.logger.info(f"☕ Auto Commercials ({config.commercial_duration}s)")
            
            context = fill_until_time(api, build_id, context, config.logger, target_time_str, filler_key=comm_key, tomorrow=is_tomorrow)
    else:
        config.logger.warn(f"Skipping slot {current_slot_tuple} due to resolution failure.")
        
    return context

def _find_active_marathon(config: ScheduleConfig, boss: DayDirector, holiday_ctx: HolidayContext) -> Tuple[Optional[Marathon], Any, Optional[Tuple[int, int]]]:
    """
    Checks triggers to see if a marathon should run today.
    Returns (marathon_obj, resolved_key, (start_hour, end_hour)).
    """
    # NOTE: Marathons are disabled during holiday ramp-up periods.
    if holiday_ctx.is_holiday_season:
        return None, None, None

    for m in sorted(config.marathons, key=lambda x: x.priority, reverse=True):
        if m.trigger(boss):
            marathon_to_run = m
            
            # Default to full day if not specified
            active_marathon_hours = marathon_to_run.hours or (8, 24)
            
            # Resolve key early to check for metadata overrides
            collection = marathon_to_run.collection
            if hasattr(collection, "pick"):
                marathon_key = collection.pick(boss) # Pass boss to collection.pick
            elif isinstance(collection, MarathonSequence):
                marathon_key = collection # Pass the sequence object directly
            elif isinstance(collection, list):
                marathon_key = boss.pick(f"marathon_{marathon_to_run.name}", collection)
            else:
                marathon_key = collection

            # Check for start_hour override in source definition
            if isinstance(marathon_key, str):
                source_data = MASTER_SOURCES.get(marathon_key)                    
                if isinstance(source_data, MarathonDefinition) and source_data.start_hour is not None:
                    active_marathon_hours = (source_data.start_hour, active_marathon_hours[1])

            config.logger.info(
                f"  {m.name} ACTIVE TODAY"
            )
            return marathon_to_run, marathon_key, active_marathon_hours
            
    return None, None, None

def _handle_end_of_slot_maintenance(api: Any, build_id: str, context: Any, last_time: Any, config: ScheduleConfig, boss: DayDirector, holiday_ctx: HolidayContext, resolver: ContentResolver) -> Any:
    """
    Handles fallback logic, circuit breaking, and filler at hour boundaries.
    """
    # Resolve fallback content only if stalled (to avoid side effects on collections)
    fallback_key = None
    if context.current_time <= last_time and config.fallback_content:
        try:
            fb_res = resolve_target(config.fallback_content, boss, holiday_ctx, config, resolver, config.logger)
            # resolve_target handles Fallback unwrapping if it returns a key, 
            # but if it returns a wrapper, we need to be careful.
            # For global fallback, we expect a simple content key.
            if isinstance(fb_res.resolved_content, str):
                fallback_key = fb_res.resolved_content
        except Exception as e:
            config.logger.warn(f"Failed to resolve fallback content: {e}")

    context = circuit_breaker(api, build_id, context, last_time, config.logger, fallback_content=fallback_key)

    if config.filler_content and is_approaching_hour_boundary(context):
        # Resolve filler content using full pipeline (holidays, etc)
        filler_result = resolve_target(config.filler_content, boss, holiday_ctx, config, resolver, config.logger)
        filler_content = filler_result.resolved_content
        
        # Handle Fallback (use primary/holiday version)
        if isinstance(filler_content, Fallback):
            filler_content = filler_content.primary

        context = fill_until_next_hour(api, build_id, context, config.logger, filler_content)
        
    return context

# 8. MAIN ORCHESTRATION

def run_daily_schedule(api: Any, context: Any, build_id: str, config: ScheduleConfig) -> Any:
    resolver = ContentResolver(api, build_id, MASTER_SOURCES, config.logger)

    # REQUIRED: register everything before playout begins
    try:
        pre_register_all_content(resolver, config)
    except Exception as e:
        config.logger.warn(f"Pre-registration failed: {e}")

    while not context.is_done:
        boss = DayDirector(context)
        holiday_ctx = HolidayContext(boss)
        start_day = context.current_time.day
        last_time = context.current_time

        day_schedule = _resolve_day_schedule(config, boss, holiday_ctx)

        config.logger.info(
            f"=== {boss.now.strftime('%A, %B %d, %Y')} ==="
        )
        config.logger.info(
            f"Season: {boss.season_vibe} | "
            f"Holidays: {', '.join(holiday_ctx.active_holidays) or 'None'}"
        )

        marathon_to_run, marathon_key, active_marathon_hours = _find_active_marathon(config, boss, holiday_ctx)

        while context.current_time.day == start_day and not context.is_done:
            hour = context.current_time.hour

            if marathon_to_run and hour_in_window(hour, active_marathon_hours[0], active_marathon_hours[1]):
                config.logger.info(
                    f"🚀 MARATHON START: {marathon_to_run.name}"
                )
                
                context = run_marathon(
                    api,
                    build_id,
                    context,
                    marathon_key,
                    MASTER_SOURCES,
                    config.logger, # Pass logger here
                    active_marathon_hours[0], # start_hour
                    active_marathon_hours[1], # end_hour
                    boss, # Pass boss to run_marathon
                    title=marathon_to_run.name,
                )

                last_time = context.current_time
                marathon_to_run = None
                continue

            current_slot_tuple = None
            target = None
            for (start, end), entry in sorted(day_schedule.items()):
                if hour_in_window(hour, start, end):
                    current_slot_tuple = (start, end)
                    target = entry
                    break

            # Resolve the target for the current slot
            result = resolve_target(target, boss, holiday_ctx, config, resolver, config.logger)
            
            # Delegate playback to the slot handler
            context = _play_schedule_slot(api, build_id, context, result, current_slot_tuple, day_schedule, config, resolver, boss, holiday_ctx)

            # Handle Single Play Slots (Play one item, then wait/fill until slot ends)
            if current_slot_tuple in config.single_play_tuples:
                context = handle_single_play_slot(
                    api, build_id, context, current_slot_tuple, day_schedule, boss, holiday_ctx, config, resolver, config.logger
                )
                last_time = context.current_time
                continue
            
            context = _handle_end_of_slot_maintenance(api, build_id, context, last_time, config, boss, holiday_ctx, resolver)
            last_time = context.current_time

    return context