"""
Logic for resolving schedule entries into content keys.
"""

import random
import traceback
from scripts.core import registry
from scripts.playout import ChannelLogger
from scripts.logic.seasonal import SeasonalBlock, resolve_seasonal_block
from scripts.logic.models import Fallback, PlayOnce, BrandedBlock, ResolutionResult, CommercialBreak
from scripts.logic.holidays import get_holiday_target
from typing import Any
from scripts.library.structures import AppointmentBlock, SeriesRelay

# Keys that should be handled by the holiday system, not the generic label loop
HOLIDAY_KEYS = {
    "CHRISTMAS", "HALLOWEEN", "THANKSGIVING", "VALENTINES_DAY", 
    "JULY_4", "NEW_YEARS_DAY", "NEW_YEARS_EVE", "ST_PATRICKS_DAY", "STAR_WARS_DAY"
}

def resolve_target(target: Any, boss: Any, holiday_ctx: Any, config: Any, resolver: Any, logger: ChannelLogger) -> ResolutionResult:
    """
    Full pipeline to resolve a raw schedule entry into a content key.
    Handles inner dicts, seasonal blocks, holidays, and fallback.
    Returns a ResolutionResult envelope.
    """
    source = "schedule"
    try:
        if target is None:  # Fallback to global fallback content if target is None
            target = config.fallback_content

        # Iterative resolution loop to handle nested structures
        # (e.g. Dict -> SeasonalBlock -> BroadcastSeries -> Fallback)
        for _ in range(10):
            changed = False
            
            if isinstance(target, dict):
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
                target = boss.pick(f"resolve_list:{id(target)}", target)
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
                
            elif isinstance(target, (Fallback, BrandedBlock)):
                # Fallback objects are final; stop resolving
                break
                
            if not changed:
                break

        # Check for holiday overrides
        holiday_target = get_holiday_target(holiday_ctx, target, config.global_holiday_overrides)
        if holiday_target is not target:
            target = holiday_target
            source = "holiday"

        # If target is a Fallback (from BroadcastSeries), return it directly
        # to avoid resolver errors (resolver expects string keys)
        if isinstance(target, Fallback):
            if isinstance(target.primary, str):
                resolver.resolve(target.primary)
            if isinstance(target.secondary, str): # Ensure secondary is registered if it's a string
                resolver.resolve(target.secondary)
            return ResolutionResult(wrapper=target, source=source)

        # Return wrappers directly so schedule.py can handle their logic
        if isinstance(target, (PlayOnce, BrandedBlock, CommercialBreak, AppointmentBlock, SeriesRelay)):
            return ResolutionResult(wrapper=target, source=source)

        # Safety check: If target is still a complex object (duck type check for SeasonalBlock)
        # This catches cases where isinstance might fail due to import aliasing or reload issues
        if not isinstance(target, str) and hasattr(target, 'base') and hasattr(target, 'seasonal'):
            target = resolve_seasonal_block(target, boss, holiday_ctx, resolver, logger) # Pass boss
            source = "seasonal"

        final_key = resolver.resolve(target)

        return apply_holiday_injection(final_key, resolver, holiday_ctx, boss, logger, source)
    except Exception as e:
        logger.warn(f"resolve_target failed for {target}: {e}")
        traceback.print_exc()
        return ResolutionResult(key=None, source="error")


def apply_holiday_injection(final_key: Any, resolver: Any, holiday_ctx: Any, boss: Any, logger: ChannelLogger, source: str = "schedule") -> ResolutionResult:
    """Check if any major holiday is active and try to inject a tagged variant."""
    if isinstance(final_key, str):
        active_tag = None
        
        for holiday in registry.HOLIDAY_PRIORITY:
            strength = holiday_ctx.envelope.get(holiday, 0.0)
            # Roll based on signal strength (e.g. 0.1 signal = 10% chance)
            if strength > 0.01 and boss.roll(strength, key=f"inject_{holiday}_{final_key}"):
                active_tag = holiday
                break
            
        if active_tag:
            # Get original query to see if we can modify it
            data = resolver.get_query_data(final_key)
            
            base_query = None
            order = "Shuffle"
            if isinstance(data, dict):
                base_query = data.get("query")
                order = data.get("order", "Shuffle")
            elif isinstance(data, str):
                base_query = data
                
            # Only inject if it's a valid query and not already tagged
            if base_query and f"tag:{active_tag}" not in base_query:
                holiday_key = f"{final_key}_auto_{active_tag}"
                holiday_query = f"({base_query}) AND tag:{active_tag}"
                resolver.register_dynamic_query(holiday_key, holiday_query, order)
                return ResolutionResult(wrapper=Fallback(primary=holiday_key, secondary=final_key), source="injection")

    return ResolutionResult(key=final_key, source=source)