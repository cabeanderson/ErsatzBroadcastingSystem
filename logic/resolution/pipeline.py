"""
The Resolution Pipeline.

Handles the transformation of schedule entries into playable content keys.
This includes:
1. Resolving nested structures (Dicts, Lists, Collections)
2. Applying overrides (Holidays, Seasonal Blocks)
3. Injecting dynamic tags (Holiday/Seasonal auto-tagging)
4. Extracting raw content for gap filling
"""

import traceback
from datetime import date, timedelta
from typing import Any, Union, Optional, Tuple, List, Dict

from scripts.core import registry, states
from scripts.core.identity import stable_hash
from scripts.core.logger import ChannelLogger
from scripts.logic.calendar.seasonal import SeasonalBlock, resolve_seasonal_block
from scripts.logic.models import Fallback, ResolutionResult, CommercialBreak
from scripts.logic.calendar.holidays import get_holiday_target
from scripts.logic.structures import Block, Program
from .config_utils import resolve_feature
from scripts.library.queries import inject_tag

# Keys that should be handled by the holiday system, not the generic label loop
# Dynamically derived from registry to ensure consistency
HOLIDAY_KEYS = set(registry.HOLIDAYS.values()) | {r["name"] for r in registry.FLOATING_RULES}

def _unwrap_nested_structure(target: Any, boss: Any, holiday_ctx: Any, config: Any, resolver: Any, logger: ChannelLogger, source: str) -> Tuple[Any, str]:
    """Iteratively resolves nested structures (Dicts, Lists, Collections, SeasonalBlocks)."""
    for _ in range(10):
        changed = False
        
        if isinstance(target, dict) and "title" not in target and "query" not in target:
            # Resolve inner dictionary using Director labels
            found_match = False
            for key, val in target.items():
                if key != "default" and key not in HOLIDAY_KEYS and boss.has(key):
                    target = val
                    found_match = True
                    changed = True
                    break
            if not found_match and "default" in target:
                target = target["default"]
                changed = True

        elif isinstance(target, list):
            target = boss.pick(f"resolve_list:{stable_hash(target)}", target)
            changed = True

        elif hasattr(target, 'pick'):
            target = target.pick(boss)
            changed = True

        elif isinstance(target, SeasonalBlock):
            target = resolve_seasonal_block(target, boss, holiday_ctx, resolver, logger) # Pass boss
            source = "seasonal"
            changed = True

        elif isinstance(target, str) and config.seasonal_blocks and target in config.seasonal_blocks:
            variants = config.seasonal_blocks[target]
            target = variants.get(boss.season_vibe, variants.get("default"))
            changed = True
            
        elif isinstance(target, (Fallback, Block, Program)):
            # Fallback objects are final; stop resolving
            break
            
        if not changed:
            break
    return target, source

def _finalize_content_resolution(target: Any, source: str, boss: Any, holiday_ctx: Any, resolver: Any, logger: ChannelLogger) -> ResolutionResult:
    """Handles final conversion of target to ResolutionResult, checking for wrappers."""
    # If target is a Fallback (from BroadcastSeries), return it directly
    # to avoid resolver errors (resolver expects string keys)
    if isinstance(target, Fallback):
        if isinstance(target.primary, str):
            resolver.resolve(target.primary)
        if isinstance(target.secondary, str): # Ensure secondary is registered if it's a string
            resolver.resolve(target.secondary)
        return ResolutionResult(wrapper=target, source=source)

    # Return wrappers directly so the dispatcher/engines can handle their logic
    if isinstance(target, (Block, Program, CommercialBreak)):
        return ResolutionResult(wrapper=target, source=source)

    # Safety check: If target is still a complex object (duck type check for SeasonalBlock)
    # This catches cases where isinstance might fail due to import aliasing or reload issues
    if not isinstance(target, str) and hasattr(target, 'base') and hasattr(target, 'seasonal'):
        target = resolve_seasonal_block(target, boss, holiday_ctx, resolver, logger) # Pass boss
        source = "seasonal"

    final_key = resolver.resolve(target)

    return ResolutionResult(key=final_key, source=source)

def resolve_content(target: Any, boss: Any, holiday_ctx: Any, config: Any, resolver: Any, logger: ChannelLogger, parent_item: Union[Block, Program, None] = None) -> ResolutionResult:
    """
    Full pipeline to resolve a raw schedule entry into a content key.
    Handles inner dicts, seasonal blocks, holidays, and fallback.
    Returns a ResolutionResult envelope.
    """
    source = "schedule"
    try:
        if target is None:  # Fallback to global fallback content if target is None
            target = config.fallback_content
            if isinstance(target, Block):
                logger.error(f"CONFIGURATION ERROR: fallback_content cannot be a Block ('{target.name}'). It must be a Collection or String Key.")

        # 1. Iterative Resolution (Unwrapping)
        target, source = _unwrap_nested_structure(target, boss, holiday_ctx, config, resolver, logger, source)

        # 2. Holiday Overrides
        holiday_target = get_holiday_target(holiday_ctx, target, config.global_holiday_overrides)
        if holiday_target is not target:
            target = holiday_target
            source = "holiday"

        # 3. Finalize (Wrappers vs Content Key)
        return _finalize_content_resolution(target, source, boss, holiday_ctx, resolver, logger)

    except Exception as e:
        logger.warn(f"resolve_content failed for {target}: {e}")
        traceback.print_exc()
        return ResolutionResult(key=None, source="error")

def _attempt_injection(base_key: str, tag_query: str, suffix: str, probability: float, roll_key: str, source_label: str, resolver: Any, boss: Any, logger: ChannelLogger) -> Optional[ResolutionResult]:
    """Helper to roll dice and apply injection if successful."""
    if boss.roll(probability, key=roll_key):
        tagged_key = inject_tag(
            base_key=base_key,
            tag_query=tag_query,
            suffix=suffix,
            resolver=resolver,
            logger=logger
        )
        if tagged_key:
            return ResolutionResult(wrapper=Fallback(primary=tagged_key, secondary=base_key), source=source_label)
    return None

def apply_seasonal_injection(final_key: Any, boss: Any, resolver: Any, logger: ChannelLogger, enabled: bool = True, source: str = "schedule") -> ResolutionResult:
    """
    Attempts to automatically inject seasonal tags into the base content query.
    """
    if not enabled or not isinstance(final_key, str) or not resolver:
        return ResolutionResult(key=final_key, source=source)

    from scripts.library.filters import SEASONAL_TAG_QUERIES

    season_tag_query = SEASONAL_TAG_QUERIES.get(boss.season_vibe)
    if not season_tag_query:
        return ResolutionResult(key=final_key, source=source)

    # Get the strength of the current season vibe
    strength = boss.get_season_strength(boss.season_vibe)
    # Cap auto-tag probability at 0.4 (40%)
    auto_ratio = 0.4
    
    # Roll for injection
    res = _attempt_injection(
        base_key=final_key,
        tag_query=season_tag_query,
        suffix=f"_auto_{boss.season_vibe.lower()}",
        probability=strength * auto_ratio,
        roll_key=f"seasonal_auto_tag_{boss.season_vibe}_{final_key}_{boss.now.hour}",
        source_label="seasonal_injection",
        resolver=resolver,
        boss=boss,
        logger=logger
    )
    if res:
        return res
            
    return ResolutionResult(key=final_key, source=source)

def apply_thematic_injection(final_key: Any, boss: Any, resolver: Any, logger: ChannelLogger, enabled: bool = True, source: str = "schedule") -> ResolutionResult:
    """
    Attempts to automatically inject thematic tags based on active calendar labels.
    """
    if not enabled or not isinstance(final_key, str) or not resolver:
        return ResolutionResult(key=final_key, source=source)

    from scripts.library.filters import INJECTION_RULES

    # Get base query data for context checks (veto/overrides)
    base_data = resolver.get_query_data(final_key)
    base_query = ""
    if isinstance(base_data, dict):
        base_query = base_data.get("query", "")
    elif isinstance(base_data, str):
        base_query = base_data
    
    # Normalize base query for checking
    base_query_lower = base_query.lower()

    for label, config in INJECTION_RULES.items():
        # 1. Determine Activation & Probability
        is_active = False
        probability = 0.0
        
        mode = config.get("mode", "static")
        
        if mode == "ramp":
            signal_name = config.get("signal")
            if signal_name:
                strength = boss.signal(signal_name)
                if strength > 0.01:
                    is_active = True
                    probability = strength * config.get("ratio", 1.0)
        elif mode == "static":
            check_label = config.get("label", label)
            if boss.has(check_label):
                is_active = True
                probability = config.get("ratio", 1.0)
        
        if not is_active:
            continue

        # 2. Veto Logic
        veto_list = config.get("veto", [])
        veto_keywords = config.get("veto_keywords", [])
        
        should_veto = False
        for v in veto_list:
            if f"genre:{v.lower()}" in base_query_lower or f"tag:{v.lower()}" in base_query_lower:
                should_veto = True
                break
        
        if not should_veto:
            for vk in veto_keywords:
                if vk.lower() in base_query_lower:
                    should_veto = True
                    break
        
        if should_veto:
            continue 

        # 3. Context Overrides
        tag_query = config.get("query")
        overrides = config.get("overrides", {})
        
        for context_key, override_query in overrides.items():
            if f"genre:{context_key.lower()}" in base_query_lower or f"tag:{context_key.lower()}" in base_query_lower:
                tag_query = override_query
                break

        # 4. Attempt Injection
        res = _attempt_injection(
            base_key=final_key,
            tag_query=tag_query,
            suffix=f"_auto_{label.lower()}",
            probability=probability,
            roll_key=f"thematic_auto_tag_{label}_{final_key}_{boss.now.hour}",
            source_label=f"injection_{label.lower()}",
            resolver=resolver,
            boss=boss,
            logger=logger
        )
        if res:
            return res
        break # Only apply the first matching theme
            
    return ResolutionResult(key=final_key, source=source)

def apply_injections(content_key: str, *, program: Optional[Program] = None, block: Optional[Block] = None, config: Any, resolver: Any, boss: Any, holiday_ctx: Any, logger: ChannelLogger, source: str) -> ResolutionResult:
    """
    Unified helper to apply all dynamic injections (Holiday, Seasonal, etc.).
    Respects cascading configuration flags (Program > Block > Channel).
    """
    # Ensure we have context for where this injection is happening
    assert program or block or source == "schedule_slot", "apply_injections called without context (program, block, or schedule_slot)"

    # Auto-disable injections for Appointment TV (scheduled programs) unless explicitly enabled
    is_appointment = bool(program and program.scheduling)

    def get_flag(attr, default_global):
        p_val = getattr(program, attr, None) if program else None
        if is_appointment and p_val is None: p_val = False
        b_val = getattr(block, attr, None) if block else None
        return resolve_feature(p_val, b_val, default_global)

    holiday_enabled = get_flag("enable_holiday_injection", config.enable_holiday_injection)
    seasonal_enabled = get_flag("enable_seasonal_injection", config.enable_seasonal_injection)
    thematic_enabled = get_flag("enable_thematic_injection", config.enable_thematic_injection)

    # Start with original key
    res = ResolutionResult(key=content_key, source=source)

    # 1. Seasonal Injection (Auto-Tagging)
    if res.key == content_key and not res.wrapper:
        res = apply_seasonal_injection(content_key, boss, resolver, logger, enabled=seasonal_enabled, source=res.source)

    # 2. Thematic Injection (Unified Holiday/Theme System)
    # Treat holiday_enabled as an alias for thematic_enabled for backward compatibility
    unified_enabled = thematic_enabled or holiday_enabled
    
    if unified_enabled and res.key == content_key and not res.wrapper:
        res = apply_thematic_injection(content_key, boss, resolver, logger, enabled=unified_enabled, source=res.source)

    return res

def _unwrap_container_for_gap_fill(content: Any, boss: Any) -> Any:
    """
    Helper to unwrap one layer of a container (Block, Program, etc.) 
    to find the underlying content for gap filling.
    """
    if isinstance(content, Program):
        return content.content
    elif isinstance(content, Block):
        items = content.items
        if hasattr(items, "pick"):
            return items.pick(boss)
        elif isinstance(items, list) and items:
            return items[0]
        return None # Empty block
    elif isinstance(content, CommercialBreak):
        return content.content
    elif isinstance(content, Fallback):
        return content.primary
    elif hasattr(content, 'pick'):
        return content.pick(boss)
    elif isinstance(content, list) and content:
        return content[0]
    return None

def extract_primary_content(obj: Any, boss: Any, holiday_ctx: Any, config: Any, resolver: Any, logger: ChannelLogger) -> Optional[str]:
    """
    Extracts a simple playable content key from a complex object (Block, Program, etc.).
    Used for gap filling where we just need 'something' from the next block.
    """
    target = obj
    
    # Iteratively resolve and unwrap until we find a string key
    for _ in range(10): # Safety limit
        # 1. Resolve high-level logic (Seasonal, Holiday, Dicts)
        res = resolve_content(target, boss, holiday_ctx, config, resolver, logger)
        content = res.resolved_content
        
        if content is None:
            return None
            
        if isinstance(content, str):
            return content
            
        # 2. Unwrap containers
        target = _unwrap_container_for_gap_fill(content, boss)
        if target is None:
            return None
            
    return None

def _build_season_windows(seasons: List[Tuple[str, int, Any]], episodes_per_slot: int, frequency: str, current_date: date) -> List[Tuple[date, date, str, int]]:
    """
    Constructs start/end windows for each season.
    This function is now more complex to handle contiguous, frequency-based scheduling.
    """
    season_windows: List[Tuple[date, date, str, int]] = []
    
    # For contiguous schedules, we need to track the end of the previous season
    last_season_end_date = None

    for key, count, start_raw in seasons:
        # For contiguous mode, the start date might need to be the end of the previous season
        if isinstance(start_raw, date) and last_season_end_date:
            start_dt = last_season_end_date
        else:
            start_dt: Optional[date] = states.resolve_season_date(start_raw, current_date)

        if not isinstance(start_dt, date):
            continue
            
        # Calculate duration based on slots, not just raw count
        slots_needed: int = (count + episodes_per_slot - 1) // episodes_per_slot
        
        # Calculate the actual end date based on the frequency
        end_dt = _calculate_end_date(start_dt, slots_needed, frequency)

        season_windows.append((start_dt, end_dt, key, count))
        last_season_end_date = end_dt
    
    season_windows.sort(key=lambda x: x[0])
    return season_windows

def _apply_schedule_looping(current_date: date, season_windows: List[Tuple[date, date, str, int]], loop: bool, loop_restart_season: Any) -> Optional[date]:
    """Adjusts current_date if looping is active and date is past end."""
    first_start_date: date = season_windows[0][0]
    last_end_date: date = season_windows[-1][1]

    if loop and current_date >= last_end_date:
        if loop_restart_season and isinstance(loop_restart_season, str):
            season_config: Optional[Dict[str, Any]] = registry.SEASONAL_RAMPS.get(loop_restart_season.upper())
            
            if season_config:
                restart_month, restart_day = season_config["peak_start"]
                next_restart_year: int = last_end_date.year
                first_restart_date: date = date(next_restart_year, restart_month, restart_day)
                
                if first_restart_date < last_end_date: first_restart_date = date(next_restart_year + 1, restart_month, restart_day)
                
                cycle_length: timedelta = first_restart_date - first_start_date
                if cycle_length.days <= 0: return None # Avoid division by zero

                total_elapsed: timedelta = current_date - first_start_date
                days_into_cycle: int = total_elapsed.days % cycle_length.days
                current_date = first_start_date + timedelta(days=days_into_cycle)
                if current_date >= last_end_date: return None
        else: # Immediate loop
            cycle_length_days: int = (last_end_date - first_start_date).days
            if cycle_length_days <= 0: return None # Avoid division by zero
            days_past_end: int = (current_date - last_end_date).days
            days_into_cycle: int = days_past_end % cycle_length_days
            current_date = first_start_date + timedelta(days=days_into_cycle)
            
    return current_date

def _find_active_episode(current_date: date, season_windows: List[Tuple[date, date, str, int]], episodes_per_slot: int, frequency: str) -> Optional[Tuple[str, int, int]]:
    """Locates the specific episode for the adjusted date, respecting frequency."""
    weekday_map = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]

    for start, end, key, count in season_windows:
        if start <= current_date < end:
            slot_idx = 0
            
            # Normalize frequency to a list of days for consistent calculation
            freq_list = []
            if isinstance(frequency, list):
                freq_list = frequency
            elif frequency == "daily":
                freq_list = weekday_map
            elif frequency == "weekly":
                # Assume it airs on the same day of the week as the premiere
                freq_list = [weekday_map[start.weekday()]]

            if freq_list:
                d = start
                slot_idx = 0
                while d < current_date:
                    if weekday_map[d.weekday()] in freq_list:
                        slot_idx += 1
                    d += timedelta(days=1)
            else: # Fallback for legacy or misconfigured string
                elapsed_days: int = (current_date - start).days
                slot_idx = (elapsed_days // 7) if frequency == "weekly" else elapsed_days

            episode: int = (slot_idx * episodes_per_slot) + 1
            return (key, count, episode)
    return None

def _calculate_end_date(start_date: date, slots_needed: int, frequency: Union[str, List[str]]) -> date:
    """Calculates the end date of a block of episodes based on airing frequency."""
    weekday_map = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
    
    # Normalize frequency to a list of days
    freq_list = []
    if isinstance(frequency, list):
        freq_list = frequency
    elif frequency == "daily":
        freq_list = weekday_map
    elif frequency == "weekly":
        freq_list = [weekday_map[start_date.weekday()]]

    if freq_list:
        d = start_date
        slots_aired = 0
        while slots_aired < slots_needed:
            if weekday_map[d.weekday()] in freq_list:
                slots_aired += 1
            d += timedelta(days=1)
        return d # The end date is the day *after* the last episode airs
    else: # Legacy "weekly" or "daily" string
        duration: timedelta = timedelta(days=(slots_needed * 7 if frequency == "weekly" else slots_needed))
        return start_date + duration


def resolve_scheduled_content(program: Program, current_date: date) -> Optional[Tuple[str, int, int]]:
    """
    Find which episode of a scheduled program is active on current_date.
    
    Returns:
        (content_key, episode_count, episode_number) or None
    """
    scheduling = program.scheduling
    if not scheduling:
        return None

    # Extract scheduling parameters with defaults
    seasons = scheduling.get("seasons", [])
    episodes_per_slot = scheduling.get("episodes_per_slot", 1)
    frequency = scheduling.get("frequency", "weekly")
    loop = scheduling.get("loop", False)
    loop_restart_season = scheduling.get("loop_restart_season")

    # 1. Build Season Windows
    season_windows = _build_season_windows(seasons, episodes_per_slot, frequency, current_date)
    
    if not season_windows:
        return None
        
    # 2. Handle Looping Logic
    current_date = _apply_schedule_looping(current_date, season_windows, loop, loop_restart_season)
    if current_date is None:
        return None

    # 3. Find Active Episode
    return _find_active_episode(current_date, season_windows, episodes_per_slot, frequency)