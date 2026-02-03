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
from scripts.logic.playback import (
    handle_single_play_slot, is_approaching_hour_boundary, fill_until_next_hour,
)
from scripts.library import ContentResolver
from scripts.playout import (ChannelLogger,
    circuit_breaker,
    fill_until_time,
    play_item, play_with_fallback,
)
from scripts.engines import run_marathon, play_branded_block, play_appointment_block, play_series_relay
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.timeslots import (
    DEFAULT_TIMESLOTS, ALT_TIMESLOTS, hour_in_window, 
    expand_timeslots, get_timeslot_map
)
from scripts.logic.models import (
    BrandedBlock, Marathon, BlockProfile, PlayOnce, Fallback, Swap, Feather, CommercialBreak
)
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.library.structures import AppointmentBlock, SeriesRelay

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
        self.commercials_between_items = commercials_between_items
        self.commercial_content = commercial_content


# 6. PRE-REGISTRATION (CRITICAL)

def pre_register_all_content(resolver: ContentResolver, config: ScheduleConfig) -> None:
    """Register all content before playout begins."""
    visited = set()
    
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

        if isinstance(obj, BrandedBlock):
            walk(obj.content, depth + 1)
            if obj.intro: resolver.resolve(obj.intro)
            if obj.outro: resolver.resolve(obj.outro)
            if obj.bumpers: resolver.resolve(obj.bumpers)
            if hasattr(obj, "specific_intros") and obj.specific_intros:
                walk(obj.specific_intros, depth + 1)
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
            resolver.resolve(obj)
            return

        if isinstance(obj, (list, tuple, set)):
            for o in obj:
                walk(o, depth + 1)
            return

        if isinstance(obj, dict):
            for v in obj.values():
                walk(v, depth + 1)
            return

        if isinstance(obj, str):
            # Only register if it's not a seasonal block reference
            if obj not in config.seasonal_blocks:
                resolver.resolve(obj)

    walk(config.schedules)
    walk(config.seasonal_blocks)
    walk(config.fallback_content)
    walk(config.holiday_schedules)
    walk(config.commercial_content)

    for m in config.marathons:
        walk(m.collection)


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

        # Determine day schedule based on Director labels
        # Priority: First matching key in config.schedules (excluding default)
        day_schedule = config.schedules.get("WEEKDAY", {})
        for key in config.schedules:
            if key != "WEEKDAY" and boss.has(key):
                day_schedule = config.schedules[key]
                break
        
        # Create a copy to allow for holiday swaps without mutating the master config
        day_schedule = day_schedule.copy()

        # Apply global seasonal ramps if configured
        if config.global_seasonal_ramps: # This feature seems experimental
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

        # Apply Holiday Schedule Swaps (Block Replacement)
        if config.holiday_schedules:
            for holiday_name, holiday_sched in config.holiday_schedules.items():
                # Normalize casing for consistency
                # Registry/Labels/Profiles use UPPERCASE
                # Signals/Envelope use lowercase
                holiday_label = holiday_name.upper()
                holiday_key = holiday_name.lower()

                # Check if today is the actual holiday (Day 0) - Force 100% takeover
                is_holiday_day = boss.has(holiday_label)
                
                # Resolve Profile Set for this holiday
                # The block_profiles can be a flat dict of profiles (e.g. STANDARD_PROFILES)
                # or a nested dict mapping holiday names to profile sets (e.g. HOLIDAY_PROFILES)
                first_val = next(iter(config.block_profiles.values()), None)
                if isinstance(first_val, dict): # Nested structure
                    profile_set = config.block_profiles.get(holiday_label, config.block_profiles.get("default", {}))
                else:
                    profile_set = config.block_profiles # Flat structure

                for slot, content in holiday_sched.items():
                    if slot not in day_schedule:
                        continue

                    if is_holiday_day:
                        day_schedule[slot] = content
                        continue

                    # Calculate Ramp based on Block Profile
                    profile = profile_set.get(slot, BlockProfile())
                    
                    ramp_signal = holiday_ctx.envelope.get(holiday_key, 0.0)
                    hangover_signal = holiday_ctx.envelope.get(f"{holiday_key}_hangover", 0.0)
                    
                    final_prob = profile.respond(ramp_signal, hangover_signal)
                    
                    if final_prob > 0 and boss.roll(final_prob, key=f"swap_{holiday_key}_{slot}"):
                        day_schedule[slot] = content

        config.logger.info(
            f"=== {boss.now.strftime('%A, %B %d, %Y')} ==="
        )
        config.logger.info(
            f"Season: {boss.season_vibe} | "
            f"Holidays: {', '.join(holiday_ctx.active_holidays) or 'None'}"
        )

        marathon_to_run = None
        marathon_key = None
        active_marathon_hours = None

        # NOTE: Marathons are disabled during holiday ramp-up periods.
        if not holiday_ctx.is_holiday_season:
            for m in sorted(config.marathons, key=lambda x: x.priority, reverse=True):
                if m.trigger(boss):
                    marathon_to_run = m
                    
                    # Default to full day if not specified
                    active_marathon_hours = marathon_to_run.hours or (8, 24)
                    
                    # Resolve key early to check for metadata overrides
                    collection = marathon_to_run.collection
                    if hasattr(collection, "pick"):
                        marathon_key = collection.pick(boss) # Pass boss to collection.pick
                    elif isinstance(collection, list):
                        marathon_key = boss.pick(f"marathon_{marathon_to_run.name}", collection)
                    else:
                        marathon_key = collection

                    # Check for start_hour override in source definition
                    source_data = MASTER_SOURCES.get(marathon_key)
                    if isinstance(source_data, dict) and "start_hour" in source_data:
                        st_hour = source_data["start_hour"]
                        if isinstance(st_hour, int):
                            active_marathon_hours = (st_hour, active_marathon_hours[1])

                    config.logger.info(
                        f"  {m.name} ACTIVE TODAY"
                    )
                    break

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

            result = resolve_target(target, boss, holiday_ctx, config, resolver, config.logger)

            # Check for BrandedBlock (Resolved)
            if result.wrapper and isinstance(result.wrapper, BrandedBlock):
                block = result.wrapper
                if block.has_branding(MASTER_SOURCES):
                    context = play_branded_block(
                        api, build_id, context, block, MASTER_SOURCES, config.logger,
                        current_slot_tuple[0], current_slot_tuple[1],
                        boss=boss,
                        holiday_ctx=holiday_ctx,
                    )
                    last_time = context.current_time
                    continue
                else:
                    # Fallback to just playing the content if branding missing
                    # Resolve the inner content to a key (recursively)
                    inner_result = resolve_target(block.content, boss, holiday_ctx, config, resolver, config.logger)
                    result = inner_result

            # Check for PlayOnce wrapper (Resolved)
            if result.wrapper and isinstance(result.wrapper, PlayOnce):
                # Play once
                play_once = result.wrapper
                real_result = resolve_target(play_once.content, boss, holiday_ctx, config, resolver, config.logger)
                if real_result:
                    real_key = real_result.resolved_content
                    context = play_with_fallback(api, build_id, real_key, config.logger, context=context, count=1)
                else:
                    config.logger.warn(f"Skipping PlayOnce slot {current_slot_tuple} due to resolution failure.")
                
                # Fill rest with next block
                context = handle_single_play_slot(
                    api, build_id, context, current_slot_tuple,
                    day_schedule, boss, holiday_ctx, config, resolver, config.logger
                )
                last_time = context.current_time
                continue

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
                
                context = fill_until_time(
                    api, build_id, context, config.logger, target_time_str, filler_key=cb_key, tomorrow=is_tomorrow
                )
                last_time = context.current_time
                continue
            
            # Check for AppointmentBlock wrapper (Resolved)
            if result.wrapper and isinstance(result.wrapper, AppointmentBlock):
                context = play_appointment_block(api, build_id, context, result.wrapper, resolver, config.logger, boss=boss)
                last_time = context.current_time
                continue
            
            # Check for SeriesRelay wrapper (Resolved)
            if result.wrapper and isinstance(result.wrapper, SeriesRelay):
                context = play_series_relay(api, build_id, context, result.wrapper, resolver, config.logger, boss=boss)
                last_time = context.current_time
                continue

            # Handle Standard Content (Key or Fallback)
            final_content = result.resolved_content
            
            if final_content:
                config.logger.info(
                    f"{context.current_time.strftime('%a %H:%M')} | {final_content} (Source: {result.source})"
                )

                context = play_with_fallback(api, build_id, final_content, config.logger, context=context, count=1)
                
                # --- AUTO COMMERCIALS (CHANNEL LEVEL) ---
                if config.commercials_between_items > 0:
                    # Resolve commercial content
                    comm_res = resolve_target(config.commercial_content, boss, holiday_ctx, config, resolver, config.logger)
                    comm_key = comm_res.resolved_content
                    if isinstance(comm_key, Fallback):
                        comm_key = comm_key.primary

                    target_dt = context.current_time + timedelta(seconds=config.commercials_between_items)
                    target_time_str = target_dt.strftime("%H:%M")
                    is_tomorrow = target_dt.day > context.current_time.day
                    
                    config.logger.info(f"☕ Auto Commercials ({config.commercials_between_items}s)")
                    
                    context = fill_until_time(api, build_id, context, config.logger, target_time_str, filler_key=comm_key, tomorrow=is_tomorrow)
                    last_time = context.current_time
            else:
                config.logger.warn(f"Skipping slot {current_slot_tuple} due to resolution failure.")

            # Handle Single Play Slots (Play one item, then wait/fill until slot ends)
            if current_slot_tuple in config.single_play_tuples:
                context = handle_single_play_slot(
                    api, build_id, context, current_slot_tuple, day_schedule, boss, holiday_ctx, config, resolver, config.logger
                )
                last_time = context.current_time
                continue
            
            # Resolve fallback content only if stalled (to avoid side effects on collections)
            fallback_key = None
            if context.current_time <= last_time and config.fallback_content:
                try:
                    fb_res = resolve_target(config.fallback_content, boss, holiday_ctx, config, resolver, config.logger)
                    content = fb_res.resolved_content
                    if isinstance(content, Fallback):
                        content = content.primary
                    if isinstance(content, str):
                        fallback_key = content
                except Exception as e:
                    config.logger.warn(f"Failed to resolve fallback content: {e}")

            context = circuit_breaker(api, build_id, context, last_time, config.logger, fallback_content=fallback_key)
            last_time = context.current_time

            if config.filler_content and is_approaching_hour_boundary(context):
                # Resolve filler content using full pipeline (holidays, etc)
                filler_result = resolve_target(config.filler_content, boss, holiday_ctx, config, resolver, config.logger)
                filler_content = filler_result.resolved_content
                
                # Handle Fallback (use primary/holiday version)
                if isinstance(filler_content, Fallback):
                    filler_content = filler_content.primary

                context = fill_until_next_hour(api, build_id, context, config.logger, filler_content
                )
                last_time = context.current_time

    return context