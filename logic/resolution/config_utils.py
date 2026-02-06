"""
Configuration utilities for resolving cascading feature flags and settings.

Hierarchy: Item (Program) > Block > Channel (ScheduleConfig) > Global (config.py)

Example:
    # Global default (config.py)
    ENABLE_COMMERCIALS = False
    
    # Channel override
    config = ScheduleConfig(enable_commercials=True)  # All programs get commercials
    
    # Block override
    block = Block(enable_commercials=False)  # This block is commercial-free
    
    # Program override
    program = Program(enable_commercials=True)  # This specific program has commercials
    
    # Resolution
    enabled = resolve_feature(
        program.enable_commercials,  # ← Wins (True)
        block.enable_commercials,    # Ignored
        config.enable_commercials    # Ignored
    )
"""

from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.logic.structures import Block, Program
    from scripts.scheduling.config import ScheduleConfig

def _is_set(val: Any) -> bool:
    return val is not None

def resolve_feature(item_val: Optional[bool], block_val: Optional[bool], channel_val: bool) -> bool:
    """
    Resolves a feature flag based on the hierarchy: Item > Block > Channel.
    Channel value is assumed to already include Global default.
    """
    if item_val is not None:
        return item_val
    if block_val is not None:
        return block_val
    return channel_val

def resolve_commercial_duration(program: Optional["Program"], block: Optional["Block"], config: "ScheduleConfig", slot_name: Optional[str] = None) -> int:
    """
    Resolves commercial duration.
    Hierarchy: Program > Block > Timeslot > Channel.
    """
    if program and program.commercial_duration > 0:
        return program.commercial_duration
    
    if block and block.commercial_duration > 0:
        return block.commercial_duration
        
    if slot_name and slot_name in config.timeslot_commercials:
        return config.timeslot_commercials[slot_name]
        
    return config.commercial_duration

def resolve_filler_content(program: Optional["Program"], block: Optional["Block"], config: "ScheduleConfig") -> Any:
    """
    Resolves filler content key.
    Hierarchy: Program > Block > Channel.
    """
    if program and _is_set(program.filler):
        return program.filler
    if block and _is_set(block.filler):
        return block.filler
    return config.filler_content

def resolve_bumper_collection(program: Optional["Program"], block: Optional["Block"], config: "ScheduleConfig") -> Optional[str]:
    """
    Resolves bumper collection key.
    Hierarchy: Program > Block > Channel.
    """
    if program and _is_set(program.bumpers):
        return program.bumpers
    if block and _is_set(block.bumpers):
        return block.bumpers
    return config.bumpers