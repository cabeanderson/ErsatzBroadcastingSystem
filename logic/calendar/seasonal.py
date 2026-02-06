"""
Logic for blending seasonal content based on signal strength.
"""
from scripts.core.logger import ChannelLogger

import hashlib
from typing import Any, Dict, Tuple, Union, List, Optional
from scripts.logic.models import Swap, Feather

class SeasonalBlock:
    def __init__(self, base: Any, seasonal: Dict[str, Any], blend_ratio: float = 1.0, auto_tag: bool = False):
        self.base: Any = base
        self.seasonal: Dict[str, Any] = seasonal
        self.blend_ratio: float = blend_ratio
        self.auto_tag: bool = auto_tag

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

def _roll_for_substitution(boss: Any, content: Any, probability: float, key_suffix: str) -> bool:
    """Helper to roll the dice for substitution."""
    if not content:
        return False
    stable_content = _get_stable_content_key(content)
    return boss.roll(probability, key=f"seasonal_sub_{key_suffix}_{boss.now.hour}_{stable_content}")

def _check_holiday_ramps(block: SeasonalBlock, boss: Any, holiday_ctx: Any) -> Optional[Any]:
    """Checks for active holiday ramps defined in the block."""
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
            if _roll_for_substitution(boss, content, strength * ratio, key_suffix=key):
                return content
    return None

def _check_seasonal_vibe(block: SeasonalBlock, boss: Any) -> Optional[Any]:
    """Checks for the current meteorological season vibe."""
    raw_content = block.seasonal.get(boss.season_vibe)
    if not raw_content:
        return None

    # Resolve content and specific ratio (handles tuples/dicts)
    content, ratio = _resolve_variant(raw_content, block.blend_ratio, boss)

    # Get the strength of the current season vibe (0.0 to 1.0)
    strength = boss.get_season_strength(boss.season_vibe)
    
    if _roll_for_substitution(boss, content, strength * ratio, key_suffix=boss.season_vibe):
        return content
        
    return None

def resolve_seasonal_block(block: SeasonalBlock, boss: Any, holiday_ctx: Any, resolver: Any = None, logger: ChannelLogger = None) -> Any: # boss: DayDirector
    """
    Resolves a SeasonalBlock. If the current season has a variant defined,
    it will roll a deterministic die to decide whether to substitute it,
    scaled by the season's signal strength.
    """
    # 1. Check for Holiday ramp signals (e.g., Christmas, Halloween)
    holiday_content = _check_holiday_ramps(block, boss, holiday_ctx)
    if holiday_content:
        return holiday_content

    # 2. Check for meteorological season signals (WINTER, etc.)
    seasonal_content = _check_seasonal_vibe(block, boss)
    if seasonal_content:
        return seasonal_content

    # 3. Fallback to base
    return block.base