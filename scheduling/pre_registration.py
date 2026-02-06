"""
Pre-registration logic for the scheduling system.
Walks the configuration tree and registers all content with ErsatzTV.
"""

from datetime import datetime
from typing import Any

from scripts.logic.resolution.resolver import ContentResolver
from scripts.scheduling.config import ScheduleConfig
from scripts.logic.structures import Block, Program
from scripts.logic.models import Fallback, Swap, Feather, CommercialBreak, ContentItem
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.core import DayDirector

class DummyContext:
    """Minimal context for pre-registration simulation."""
    def __init__(self):
        self.current_time = datetime.now()

class ContentRegistrar:
    """Helper class to traverse and register content configuration."""
    
    def __init__(self, resolver: ContentResolver, config: ScheduleConfig):
        self.resolver = resolver
        self.config = config
        self.visited = set()
        self.dummy_boss = DayDirector(DummyContext())

    def register(self, obj: Any, depth: int = 0) -> None:
        """Recursively register content objects."""
        if obj is None or depth > 10:
            return

        # Optimization: Avoid re-walking shared objects
        if id(obj) in self.visited:
            return
        self.visited.add(id(obj))

        # 1. Complex Logic Structures
        if isinstance(obj, SeasonalBlock) or (hasattr(obj, 'base') and hasattr(obj, 'seasonal')):
            self.register(obj.base, depth + 1)
            self.register(obj.seasonal, depth + 1)
            return

        if isinstance(obj, (Swap, Feather, CommercialBreak)):
            self.register(obj.content, depth + 1)
            return
        
        if isinstance(obj, Fallback):
            self.register(obj.primary, depth + 1)
            self.register(obj.secondary, depth + 1)
            return

        # 2. Containers (Block, Program)
        if isinstance(obj, Block):
            self._register_block(obj, depth)
            return
            
        if isinstance(obj, Program):
            self._register_program(obj, depth)
            return

        # 3. Leaf Content Objects
        if isinstance(obj, ContentItem):
            self.resolver.resolve(obj, self.dummy_boss)
            return

        # 4. Collections & Iterables
        # Skip seasonal block references (strings in seasonal_blocks dict)
        if isinstance(obj, str) and obj in self.config.seasonal_blocks:
            return

        # Handle Collections (must check not dict, as dicts also have 'items')
        if hasattr(obj, "items") and not isinstance(obj, dict):
            self.register(obj.items, depth + 1)
            return

        if hasattr(obj, "pick"):
            self.resolver.resolve(obj, self.dummy_boss)
            return

        if isinstance(obj, (list, tuple, set)):
            for o in obj:
                self.register(o, depth + 1)
            return

        if isinstance(obj, dict):
            self._register_dict(obj, depth)
            return

        if isinstance(obj, str):
            self._register_string(obj, depth)
            return

    def _register_block(self, block: Block, depth: int) -> None:
        self.register(block.items, depth + 1)
        self.register(block.filler, depth + 1)
        self._resolve_branding(block)

    def _register_program(self, program: Program, depth: int) -> None:
        self.register(program.content, depth + 1)
        self.register(program.filler, depth + 1)
        self._resolve_branding(program)
        if program.scheduling and "generated_queries" in program.scheduling:
            for key, query in program.scheduling["generated_queries"].items():
                self.config.logger.debug(f"Pre-registering Program query: {key}")
                self.resolver.register_dynamic_query(key, query, order="Chronological")

    def _resolve_branding(self, obj: Any) -> None:
        if obj.intro: self.resolver.resolve(obj.intro)
        if obj.outro: self.resolver.resolve(obj.outro)
        if obj.bumpers: self.resolver.resolve(obj.bumpers)
        if obj.commercials: self.resolver.resolve(obj.commercials)

    def _register_dict(self, d: dict, depth: int) -> None:
        if "title" in d:
            self.resolver.resolve(d, self.dummy_boss)
        else:
            for v in d.values():
                self.register(v, depth + 1)

    def _register_string(self, key: str, depth: int) -> None:
        # Optimization: If key points to a collection, walk its items
        if key in self.resolver.registry:
            data = self.resolver.registry[key]
            if hasattr(data, "items") and not callable(data.items):
                self.register(data.items, depth + 1)

        self.resolver.resolve(key, self.dummy_boss)

def pre_register_all_content(resolver: ContentResolver, config: ScheduleConfig) -> None:
    """Register all content before playout begins."""
    registrar = ContentRegistrar(resolver, config)
    
    # Walk roots
    registrar.register(config.schedules)
    registrar.register(config.seasonal_blocks)
    registrar.register(config.fallback_content)
    registrar.register(config.holiday_schedules)
    registrar.register(config.commercial_content)

    for m in config.marathons:
        registrar.register(m.collection)