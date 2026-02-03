# scripts/engines/marathon.py
"""
Marathon system with manual episode playback.
Compatible with older ErsatzTV API.
"""

from etv_client.models import ControlSkipToItem
from scripts.library import ContentResolver, count_episodes_in_range, extract_episode_range
from scripts.playout import toggle_marathon_branding, play_item, ChannelLogger
import random
from typing import Any, Dict, Optional, Callable


def run_marathon(api: Any, build_id: str, context: Any, marathon_key: str, sources_registry: Dict[str, Any], logger: ChannelLogger, start_hour: int, end_hour: int, boss: Any, title: Optional[str] = None) -> Any: # boss: DayDirector
    """
    Run marathon with manual episode loop (compatible with older API).
    """
    resolver = ContentResolver(api, build_id, sources_registry, logger)
    
    # Get metadata
    data = sources_registry.get(marathon_key)
    
    # Determine EPG Title/Description
    # Priority: 1. Specific Source Title, 2. Passed-in Title (Generic), 3. Key Name
    epg_title = title
    epg_desc = None
    start_mode = "beginning" # Default to beginning for curated marathons
    meta_season = None
    meta_episode = None
    meta_count = 0
    
    if isinstance(data, dict):
        if "title" in data:
            epg_title = data["title"]
        if "description" in data:
            epg_desc = data["description"]
        if "start_mode" in data:
            start_mode = data["start_mode"]
        if "start_season" in data:
            meta_season = data["start_season"]
        if "start_episode" in data:
            meta_episode = data["start_episode"]
        if "episode_count" in data:
            meta_count = data["episode_count"]
    
    logger.info(f"🎬 {epg_title or marathon_key} ({start_hour}:00-{end_hour}:00)")
    
    # Register content
    resolver.resolve(marathon_key, boss) # Pass boss for deterministic collection picking
    
    # Get query for episode detection
    query = None
    if isinstance(data, dict):
        if "query" in data:
            query = data["query"]
        elif "content" in data:
            query_data = data["content"]
            query = query_data.get("query") if isinstance(query_data, dict) else query_data
    elif isinstance(data, str):
        query = data
    
    # Calculate episodes (for logging/stopping only)
    total_episodes = 0
    if query:
        total_episodes = count_episodes_in_range(query)
    if meta_count > 0:
        total_episodes = meta_count
    
    # Handle Start Logic (Beginning vs Random)
    if query:
        # 1. Try to get range from query
        q_season, q_episode = extract_episode_range(query)
        
        # 2. Override with explicit metadata if provided (Fixes tag-based queries)
        season = meta_season if meta_season is not None else q_season
        episode = meta_episode if meta_episode is not None else q_episode
        
        if start_mode == "random" and total_episodes > 1:
            # For "Simpsons Random Start":
            # If we have a season range in metadata, pick one
            if isinstance(meta_season, list):
                season = random.randint(meta_season[0], meta_season[1])
                episode = 1 # Start at ep 1 of that random season
                
            if season is not None and episode is not None:
                logger.info(f"   🎲 Random start: S{season}E{episode}")
                api.skip_to_item(build_id, ControlSkipToItem(
                    content=marathon_key,
                    season=season,
                    episode=episode
                ))
            
        elif start_mode == "beginning" and season is not None and episode is not None:
            logger.info(f"   ↳ Resetting to start: S{season}E{episode}")
            api.skip_to_item(build_id, ControlSkipToItem(
                content=marathon_key,
                season=season,
                episode=episode
            ))

    # Start EPG Grouping
    if epg_title:
        if logger.verbose:
            logger.debug(f"   📺 Grouping as: {epg_title}")
        toggle_marathon_branding(api, build_id, name=epg_title, description=epg_desc, start=True)
    
    # Manual episode loop
    start_day = context.current_time.day
    last_time = context.current_time
    episodes_played = 0
    
    while context.current_time.day == start_day and not context.is_done:
        hour = context.current_time.hour
        
        # Check time bounds
        if hour >= end_hour or hour < start_hour:
            logger.info(f"⏰ Time limit reached: {hour}:00 >= {end_hour}:00")
            break
        
        # Play episode
        context = play_item(api, build_id, marathon_key, logger)
        
        # Check progress
        if context.current_time <= last_time:
            logger.warn(f"Marathon content exhausted")
            break
        
        last_time = context.current_time
        episodes_played += 1
        
        # Check completion
        if total_episodes > 0 and episodes_played >= total_episodes:
            logger.info(f"✓ All {total_episodes} episodes complete (Played: {episodes_played})")
            break
    
    logger.info(f"🏁 {epg_title or marathon_key} - {episodes_played} episodes")
    
    # End EPG Grouping
    if epg_title:
        toggle_marathon_branding(api, build_id, start=False)
    
    return context
