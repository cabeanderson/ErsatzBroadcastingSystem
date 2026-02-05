# scripts/engines/marathon.py
"""
Marathon system with manual episode playback.
Compatible with older ErsatzTV API.
"""

from etv_client.models import ControlSkipToItem
from scripts.logic.resolver import ContentResolver, resolve_sequence
from scripts.logic.models import MarathonDefinition, ContentItem
from scripts.logic.queries import get_play_count, extract_episode_range, is_movie_query, extract_title_from_query
from scripts.core.logger import ChannelLogger
from scripts.playout import toggle_marathon_branding, play_item, play_smart_bumper
import random
from typing import Any, Dict, Optional, Callable

INFINITE = None


def run_marathon(api: Any, build_id: str, context: Any, marathon_key: str, sources_registry: Dict[str, Any], logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, title: Optional[str] = None) -> Any: # boss: DayDirector
    """
    Run marathon with manual episode loop (compatible with older API).
    """
    # 1. Resolve the marathon key to get the content definition
    resolver = ContentResolver(api, build_id, sources_registry, logger)
    
    # If it's a key (string), resolve it to register content.
    # If it's a sequence object, we'll handle items in the loop.
    if isinstance(marathon_key, str):
        resolver.resolve(marathon_key, boss)

    # 2. Determine the sequence of items to play
    # If the resolved content is a list (from a Collection), use it directly.
    # If it's a single key string, wrap it in a list.
    sequence = []
    
    # Check if the key points to a collection in the registry that returned a list
    # The resolver.resolve() call above might have returned a single key if it was a RandomCollection.
    # But for a MarathonSequence (OrderedCollection), we want the whole list.
    # We need to access the raw collection from the source registry if possible, 
    # OR rely on the fact that `marathon.collection` in the config might be the list/collection itself.
    
    # Let's look at how run_daily_schedule calls this. It passes `marathon_key`.
    # We need to look up the metadata for this key.
    if isinstance(marathon_key, str):
        data = resolver.get_query_data(marathon_key)
    else:
        data = None
    
    # Determine EPG Title/Description
    # Priority: 1. Specific Source Title, 2. Passed-in Title (Generic), 3. Key Name
    epg_title = title
    epg_desc = None
    start_mode = "beginning" # Default to beginning for curated marathons
    meta_season = None
    meta_episode = None
    meta_count = 0
    
    if isinstance(data, MarathonDefinition):
        epg_title = data.name
        epg_desc = data.description
        start_mode = data.start_mode
        meta_season = data.start_season
        meta_episode = data.start_episode
        meta_count = data.episode_count or 0
    elif isinstance(data, dict): # Legacy dictionary support
        epg_title = data.get("title", epg_title)
        epg_desc = data.get("description")
        start_mode = data.get("start_mode", "beginning")
        meta_season = data.get("start_season")
        meta_episode = data.get("start_episode")
        meta_count = data.get("episode_count", 0)
    
    logger.info(f"🎬 {epg_title or marathon_key} ({start_hour}:00-{end_hour}:00)")
    
    # Build the sequence
    # If the data represents a single item (MarathonDefinition, dict, str), treat as sequence of 1
    # If we want true multi-item sequences, we need to handle lists here.
    # Currently, `marathon_key` is a string key.
    # If the underlying source is a list (OrderedCollection), `resolver.resolve` usually picks ONE.
    # To support sequences, we might need to change how `run_marathon` is called or how it resolves.
    # For now, let's assume `marathon_key` points to a single "Block" of content (which might be a show).
    # We will treat it as a sequence of [marathon_key] for backward compatibility, 
    # but the logic below supports iterating if we expand this later.
    
    sequence = resolve_sequence(marathon_key)

    # Start EPG Grouping
    if epg_title:
        if logger.verbose:
            logger.debug(f"   📺 Grouping as: {epg_title}")
        toggle_marathon_branding(api, build_id, name=epg_title, description=epg_desc, start=True)
    
    start_day = context.current_time.day
    last_time = context.current_time
    items_played = 0
    
    # Iterate through the sequence
    for item_key in sequence:
        # Resolve the item to get its query/metadata
        # Note: We re-resolve here in case the sequence item is different from the main key
        if isinstance(item_key, ContentItem):
            item_data = item_key
        else:
            item_data = resolver.get_query_data(item_key)
        
        # If item_key is a ContentItem, resolve() handles registration
        # If item_key is a string, resolve() handles registration
        resolved_key = resolver.resolve(item_key, boss)
        
        # Determine Query
        query = None
        media_type = None
        is_movie = False
        if isinstance(item_data, MarathonDefinition):
            query = item_data.query
            media_type = item_data.media_type
            is_movie = item_data.is_movie()
        elif isinstance(item_data, dict):
            query = item_data.get("query")
            if not query and "content" in item_data:
                 # Handle nested content dict
                 c = item_data["content"]
                 if isinstance(c, dict): query = c.get("query")
        elif isinstance(item_data, ContentItem):
            query = item_data.query
            media_type = item_data.media_type
            is_movie = item_data.is_movie()
            # If query is missing in ContentItem, we might need to resolve it via title, but resolver.resolve usually handles registration.
        elif isinstance(item_data, str) or isinstance(item_key, str):
            query = item_data

        # Determine Play Count
        play_count = INFINITE # Default to infinite/fill
        if meta_count > 0:
            play_count = meta_count
        elif is_movie:
            play_count = 1
        elif query:
            detected = get_play_count(query)
            if detected:
                play_count = detected
        
        # Determine start parameters for explicit sequencing
        q_season, q_episode = None, None
        if query:
            q_season, q_episode = extract_episode_range(query)

        # Handle Random Start (Only for first item in sequence)
        if items_played == 0 and start_mode == "random" and play_count > 1:
             r_season = meta_season if meta_season is not None else q_season
             r_episode = 1
             if isinstance(meta_season, list):
                 r_season = random.randint(meta_season[0], meta_season[1])
             
             if r_season is not None:
                 logger.info(f"   🎲 Random start: S{r_season}E{r_episode} for {resolved_key}")
                 try:
                    api.skip_to_item(build_id, ControlSkipToItem(content=resolved_key, season=r_season, episode=r_episode))
                    # Disable explicit ordering for random mode to let it flow naturally
                    q_season, q_episode = None, None 
                 except Exception as e:
                    logger.warn(f"Random skip failed: {e}")

        # Play Loop for this item in the sequence
        played_this_item = 0
        while True:
            # Check if we've played enough items for this block
            if play_count is not INFINITE and played_this_item >= play_count:
                break

            # Global Time Check
            if context.current_time.day != start_day or context.is_done:
                break
            hour = context.current_time.hour
            if hour >= end_hour or hour < start_hour:
                logger.info(f"⏰ Time limit reached: {hour}:00 >= {end_hour}:00")
                break
            
            # EXPLICIT SEQUENCING: Force the exact episode if we know the range
            # This fixes issues where ErsatzTV skips episodes in a collection
            target_episode = None
            if q_season is not None and q_episode is not None and not is_movie:
                target_season = q_season
                target_episode = q_episode + played_this_item
                try:
                    # "Point" the collection to this specific episode before playing
                    api.skip_to_item(build_id, ControlSkipToItem(
                        content=resolved_key, 
                        season=target_season, 
                        episode=target_episode
                    ))
                except Exception:
                    pass # Fallback to standard "next item" behavior if skip fails
            
            context = play_item(api, build_id, resolved_key, logger)
            
            if context.current_time <= last_time:
                logger.warn(f"Marathon content exhausted or stalled")
                break
            
            last_time = context.current_time
            items_played += 1
            played_this_item += 1
            
            # --- MARATHON BUMPER LOGIC ---
            # Try to play a bumper tagged with "marathon", "bumper", and the show title
            if query:
                title = extract_title_from_query(query)
                context, played = play_smart_bumper(api, build_id, context, title, resolver, logger, required_tags=["marathon", "bumpers"])
                if played:
                    last_time = context.current_time
        
        # Check if we broke out of item loop due to time
        hour = context.current_time.hour
        if hour >= end_hour or hour < start_hour:
            break # Break sequence loop
    
    logger.info(f"🏁 {epg_title or marathon_key} - {items_played} items played")
    
    # End EPG Grouping
    if epg_title:
        toggle_marathon_branding(api, build_id, start=False)
    
    return context
