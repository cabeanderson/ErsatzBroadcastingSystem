"""
Logic for blending seasonal content based on signal strength.
"""
from scripts.core.logger import ChannelLogger

import hashlib
from typing import Any, Dict, Tuple, Union, List
from scripts.logic.models import Swap, Feather
from scripts.config import ENABLE_SEASONAL_BLOCKS

class SeasonalBlock:
    def __init__(self, base: Any, seasonal: Dict[str, Any], blend_ratio: float = 1.0):
        self.base: Any = base
        self.seasonal: Dict[str, Any] = seasonal
        self.blend_ratio: float = blend_ratio

def _get_stable_content_key(content: Any) -> str:
    """Generates a stable string representation for content."""
    # If it's a Collection object, use its items list which is stable
    if hasattr(content, "items"):
        # Optimization: Cache the hash on the object to avoid re-stringifying large lists
        if not hasattr(content, "_stable_key"):
            items_str = str(content.items).encode('utf-8')
            content._stable_key = hashlib.md5(items_str).hexdigest()
        return content._stable_key
    # Otherwise stringify (works for strings, lists, dicts)
    return str(content)

def _resolve_variant(variant: Any, default_ratio: float, boss: Any) -> Tuple[Any, float]:
    """
    Helper to resolve a variant value which might be:
    - A content key (string, collection)
    - A Swap or Feather object
    
    Returns: (content_key, ratio)
    """
    if isinstance(variant, dict):
        # Resolve nested dictionary based on day labels
        match = None
        for label, sub_variant in variant.items():
            if label != "default" and boss.has(label):
                match = sub_variant
                break
        return _resolve_variant(match or variant.get("default"), default_ratio, boss)

    if isinstance(variant, Feather):
        return variant.content, variant.ratio

    if isinstance(variant, Swap):
        return variant.content, 1.0

    return variant, default_ratio


def resolve_seasonal_block(block: SeasonalBlock, boss: Any, holiday_ctx: Any, resolver: Any = None, logger: ChannelLogger = None) -> Any: # boss: DayDirector
    """
    Resolves a SeasonalBlock. If the current season has a variant defined,
    it will roll a deterministic die to decide whether to substitute it,
    scaled by the season's signal strength.
    """
    
    if not ENABLE_SEASONAL_BLOCKS:
        return block.base

    # 1. Check for Holiday ramp signals (e.g., Christmas, Halloween)
    for key, raw_content in block.seasonal.items():
        if key in ["WINTER", "SPRING", "SUMMER", "FALL", "default"]:
            continue
        
        holiday_name = key.lower()
        hangover_name = f"{holiday_name}_hangover"

        # Get signal strength from HolidayContext for both ramp-up and cool-down
        ramp_strength = holiday_ctx.envelope.get(holiday_name, 0.0)
        hangover_strength = holiday_ctx.envelope.get(f"{holiday_name}_hangover", 0.0)
        
        strength = max(ramp_strength, hangover_strength)

        if strength > 0:
            content, ratio = _resolve_variant(raw_content, block.blend_ratio, boss)
            # Add hour to key to allow feathering throughout the day
            stable_content = _get_stable_content_key(content)
            if content and boss.roll(strength * ratio, key=f"seasonal_sub_{key}_{boss.now.hour}_{boss.now.minute}_{boss.now.second}_{stable_content}"):
                return content

    # 2. Check for meteorological season signals (WINTER, etc.)
    raw_content = block.seasonal.get(boss.season_vibe)
    if not raw_content:
        return block.base

    # Resolve content and specific ratio (handles tuples/dicts)
    content, ratio = _resolve_variant(raw_content, block.blend_ratio, boss)

    # Get the strength of the current season vibe (0.0 to 1.0)
    strength = boss.get_season_strength(boss.season_vibe)
    
    # Roll the dice with probability scaled by strength
    stable_content = _get_stable_content_key(content)
    if content and boss.roll(strength * ratio, key=f"seasonal_sub_{boss.season_vibe}_{boss.now.hour}_{boss.now.minute}_{boss.now.second}_{stable_content}"):
        return content
    else:
        return block.base