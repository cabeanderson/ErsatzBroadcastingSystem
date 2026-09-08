"""
The Architect - Orchestrates daily channel flow.
Coordinates time, rules, and intent without touching physical execution.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from scripts.core.logger import ChannelLogger
from scripts.logic.calendar.timeslots import (
    expand_timeslots, get_timeslot_map
)
from scripts.logic.models import (
    Marathon
)
from scripts.logic.structures import Block
from scripts.logic.profiles import HOLIDAY_PROFILES
from scripts.settings import (
    ENABLE_HOLIDAY_INJECTION, ENABLE_COMMERCIALS,
    ENABLE_FILLER, ENABLE_BUMPERS, ENABLE_MARATHONS, ENABLE_SEASONAL_INJECTION,
    DEFAULT_COMMERCIAL_DURATION, DEFAULT_COMMERCIAL_CONTENT,
    DEFAULT_CIRCUIT_BREAKER_SKIP, SMART_BUMPERS
)

# 5. SCHEDULE CONFIGURATION

class ScheduleConfig:
    def __init__(
        self,
        schedules: Dict[str, Any],
        marathons: Optional[List[Marathon]] = None,
        seasonal_blocks: Optional[Dict[str, Dict[str, Any]]] = None,
        timeslot_preset: Union[str, Dict[str, Tuple[int, int]]] = "default",
        custom_timeslots: Optional[Dict[str, Tuple[int, int]]] = None,
        global_holiday_overrides: Optional[Dict[str, Any]] = None,
        global_seasonal_ramps: Optional[Dict[str, Dict[str, Any]]] = None,
        holiday_schedules: Optional[Dict[str, Dict[str, Any]]] = None,
        block_profiles: Optional[Dict[str, Any]] = None,
        filler_content: Optional[Any] = None,
        bumpers: Optional[str] = None,
        smart_bumpers: Optional[str] = None,
        logger: Optional[ChannelLogger] = None,
        fallback_content: Optional[Any] = None,
        commercial_content: Any = DEFAULT_COMMERCIAL_CONTENT,
        commercial_duration: int = DEFAULT_COMMERCIAL_DURATION,
        global_filter: Optional[str] = None,
        enable_holiday_injection: Optional[bool] = None,
        enable_seasonal_injection: Optional[bool] = None,
        enable_thematic_injection: Optional[bool] = None,
        enable_commercials: Optional[bool] = None,
        enable_filler: Optional[bool] = None,
        enable_bumpers: Optional[bool] = None,
        enable_marathons: Optional[bool] = None,
        timeslot_commercials: Optional[Dict[str, int]] = None,
        circuit_breaker_skip: int = DEFAULT_CIRCUIT_BREAKER_SKIP,
    ):
        # Resolve timeslots map locally
        timeslots = get_timeslot_map(timeslot_preset, custom_timeslots)

        self.schedules = {
            k: expand_timeslots(v, timeslot_preset, custom_timeslots)
            for k, v in schedules.items()
        }
        self.marathons = marathons or []
        self.seasonal_blocks = seasonal_blocks or {}

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
        self.bumpers = bumpers
        self.logger = logger or ChannelLogger() # Default to a basic logger
        # A Block cannot be a fallback. `dispatcher.resolve_fallback_key`
        # resolves a key or a Collection down to a content key, but a Block is
        # a container of slots with no single key to reach -- it resolves to
        # itself, the breaker skips ahead instead of playing it, and the
        # channel has a fallback that can never fire. Caught here so the error
        # lands at channel definition rather than at the moment the schedule is
        # already stalled.
        if isinstance(fallback_content, Block):
            raise ValueError(
                f"Configuration Error: fallback_content cannot be a Block "
                f"('{fallback_content.name}'). The circuit breaker plays a single "
                f"content key; pass a key or a Collection instead."
            )
        self.fallback_content = fallback_content
        # Support both old and new naming, prefer new
        self.commercial_duration = commercial_duration
        self.commercial_content = commercial_content
        self.timeslot_commercials = timeslot_commercials or {}
        self.circuit_breaker_skip = circuit_breaker_skip
        self.global_filter = global_filter
        
        # Set feature flags, falling back to global config
        self.enable_holiday_injection = enable_holiday_injection if enable_holiday_injection is not None else ENABLE_HOLIDAY_INJECTION
        self.enable_seasonal_injection = enable_seasonal_injection if enable_seasonal_injection is not None else ENABLE_SEASONAL_INJECTION
        self.enable_thematic_injection = enable_thematic_injection if enable_thematic_injection is not None else False # Default off for now
        self.enable_commercials = enable_commercials if enable_commercials is not None else ENABLE_COMMERCIALS
        self.enable_filler = enable_filler if enable_filler is not None else ENABLE_FILLER
        self.enable_bumpers = enable_bumpers if enable_bumpers is not None else ENABLE_BUMPERS
        self.enable_marathons = enable_marathons if enable_marathons is not None else ENABLE_MARATHONS
        self.smart_bumpers = smart_bumpers if smart_bumpers is not None else SMART_BUMPERS

        # Create reverse map for timeslot commercial lookups
        self.timeslot_reverse_map = {v: k for k, v in timeslots.items()}