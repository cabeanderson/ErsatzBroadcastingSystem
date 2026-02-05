"""
Logic for resolving schedule entries into content keys.
"""

import traceback
from scripts.core import registry
from scripts.core.logger import ChannelLogger
from scripts.logic.seasonal import SeasonalBlock, resolve_seasonal_block
from scripts.logic.models import Fallback, PlayOnce, ResolutionResult, CommercialBreak
from scripts.logic.holidays import get_holiday_target, apply_holiday_injection
from typing import Any, Union
from scripts.logic.structures import Block, Program

# Keys that should be handled by the holiday system, not the generic label loop
# Dynamically derived from registry to ensure consistency
HOLIDAY_KEYS = set(registry.HOLIDAYS.values()) | {r["name"] for r in registry.FLOATING_RULES}

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
                
            elif isinstance(target, (Fallback, Block, Program)):
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
        if isinstance(target, (PlayOnce, Block, Program, CommercialBreak)):
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