# scripts/logic/resolver.py
"""
Content Resolver - The Bridge to ErsatzTV.

Translates internal content keys and collections into actual
ErsatzTV search queries and registers them via the API.
"""

from typing import Any, Dict, Optional, Set, Union
import re
import hashlib
from scripts.library.queries import show_by_title
from scripts.core.identity import stable_hash
from etv_client.models import ContentSearch, ContentPlaylist
from scripts.core.logger import ChannelLogger
from scripts.logic.models import MarathonDefinition
from scripts.logic.models import ContentItem

class ContentResolver:
    def __init__(self, api: Any, build_id: str, registry: Dict[str, Any], logger: ChannelLogger, global_filter: Optional[str] = None):
        self.api: Any = api
        self.build_id: str = build_id
        self.registry: Dict[str, Any] = registry # This IS the MASTER_SOURCES from sources.py
        self.active_keys: Set[str] = set()
        self.dynamic_registry: Dict[str, Dict[str, Any]] = {}
        self.logger: ChannelLogger = logger
        self.global_filter: Optional[str] = global_filter

    def _get_key_from_target(self, target: Any, boss: Optional[Any] = None) -> Any: # boss: DayDirector
        """
        Unpacks the target from the calendar.
        If the calendar returns 'DBZ_TV', this finds it in sources.py.
        """
        # 1. If it's an object with a pick method (like OrderedCollection)
        if hasattr(target, 'pick'):
            return self._get_key_from_target(target.pick(boss), boss)

        # 2. If it's a raw list
        if isinstance(target, list):
            return self._get_key_from_target(boss.pick(f"resolver_list_pick:{stable_hash(target)}", target) if boss else target[0], boss) # Fallback to first item if no boss

        return target

    def _register_with_etv(self, key: str) -> None:
        """Uses the key to find the query/order and tells ErsatzTV."""
        # Safety check: Ignore non-string keys (e.g. CommercialBreak objects)
        if not isinstance(key, str):
            return

        if key in self.active_keys:
            return

        # Lookup in MASTER_SOURCES
        data = self.registry.get(key)
        if not data:
            self.logger.warn(f"Key '{key}' not found in MASTER_SOURCES!")
            return

        # Default values
        query = None
        order = "Shuffle"
        content_type = "search"
        playlist_name = None
        playlist_group = None

        # 1. Handle Dictionary Definitions
        if isinstance(data, dict):
            content_type = data.get("type", "search")
            
            if content_type == "playlist":
                playlist_name = data.get("playlist")
                playlist_group = data.get("group")
            
            # Structure from playback_order(): {"query": "...", "order": "..."}
            elif "query" in data:
                query = data["query"]
                order = data.get("order", "Shuffle")
            
            # Structure from legacy/marathon: {"content": ...}
            elif "content" in data:
                content = data["content"]
                if isinstance(content, dict):
                    query = content.get("query")
                    order = content.get("order", "Shuffle")
                else:
                    query = content
        
        # 2b. Handle MarathonDefinition
        elif isinstance(data, MarathonDefinition):
            query = data.query
            order = data.order
        
        # 2. Handle String Definitions
        elif isinstance(data, str):
            query = data

        # 3. Validation
        if content_type == "playlist":
            if playlist_name and playlist_group:
                self.api.add_playlist(self.build_id, ContentPlaylist(key=key, playlist=playlist_name, playlist_group=playlist_group))
                self.active_keys.add(key)
                return
            else:
                self.logger.warn(f"Invalid playlist definition for '{key}': {data}")
                return

        if not isinstance(query, str):
            self.logger.warn(f"Invalid query format for key '{key}'. Got: {type(data)}")
            return
            
        # Apply global filter if it exists
        if self.global_filter:
            query = f"({query}) AND ({self.global_filter})"

        if "test_bebop" in key:
            self.logger.info(f"Registering TEST key '{key}' with order: '{order}'")
        self.api.add_search(self.build_id, ContentSearch(key=key, query=query, order=order))
        self.active_keys.add(key)

    def resolve(self, target: Any, boss: Optional[Any] = None) -> str: # boss: DayDirector
        key = self._get_key_from_target(target, boss)
        
        # Check if key is a string that points to a Collection in the registry
        if isinstance(key, str) and key in self.registry:
            data = self.registry[key]
            if hasattr(data, 'pick'):
                # It's a collection! Pick from it.
                picked = data.pick(boss)
                # Recursively resolve the picked item
                return self.resolve(picked, boss)

        # Handle ContentItem objects
        if isinstance(key, ContentItem):
            # Optimization: Check if we've already generated a key for this object instance
            if hasattr(key, "_cached_generated_key"):
                 # Ensure we register it for this build (active_keys check is fast)
                 self.register_dynamic_query(key._cached_generated_key, key._cached_query, key.order)
                 return key._cached_generated_key

            title = key.title
            order = key.order
            query = key.query if key.query else show_by_title(title)
            
            # Generate unique key based on title AND query to prevent collisions
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()
            query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()[:6]
            generated_key = f"auto_gen_{safe_title}_{query_hash}"
            
            # Cache on the object itself
            key._cached_generated_key = generated_key
            key._cached_query = query
            
            self.register_dynamic_query(generated_key, query, order)
            return generated_key

        # Handle on-the-fly dictionary definitions (e.g. inside Collections)
        if isinstance(key, dict) and "title" in key:
            # Generate a key and query
            title = key["title"]
            order = key.get("order", "Shuffle")
            
            if "query" in key:
                query = key["query"]
            else:
                query = show_by_title(title)
            
            # Generate unique key based on title AND query
            safe_title = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()
            query_hash = hashlib.md5(query.encode('utf-8')).hexdigest()[:6]
            generated_key = f"auto_gen_{safe_title}_{query_hash}"
            
            self.register_dynamic_query(generated_key, query, order)
            return generated_key
            
        self._register_with_etv(key)
        return key

    def get_query_data(self, key: str) -> Optional[Union[str, Dict[str, Any]]]:
        """Retrieve raw query data for a key from the registry."""
        if key in self.dynamic_registry:
            return self.dynamic_registry[key]
        return self.registry.get(key)

    def register_dynamic_query(self, key: str, query: str, order: str = "Shuffle") -> None:
        """Register a dynamically generated query with ErsatzTV."""
        if key in self.active_keys:
            return
            
        # Apply global filter if it exists
        if self.global_filter:
            query = f"({query}) AND ({self.global_filter})"
            
        self.api.add_search(self.build_id, ContentSearch(key=key, query=query, order=order))
        self.active_keys.add(key)
        # Store locally so we can inspect it later (e.g. for multi-part detection)
        self.dynamic_registry[key] = {"query": query, "order": order}