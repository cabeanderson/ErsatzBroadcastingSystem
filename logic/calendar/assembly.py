"""
Logic for determining the day's schedule structure.
Combines day-of-week selection, seasonal ramps, and holiday overrides.
"""

from typing import Dict, Any, TYPE_CHECKING, Tuple, Optional, List
from .seasonal import SeasonalBlock
from scripts.logic.models import BlockProfile, HolidayProfile, Marathon, MarathonDefinition, ContentItem
from scripts.logic.structures import Block, Program, MarathonSequence
from scripts.library.queries import get_play_count, extract_episode_range
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from scripts.scheduling.config import ScheduleConfig
    from scripts.core import DayDirector
    from .holidays import HolidayContext

# --- Marathon Conversion Logic (Moved from engines/marathon.py) ---

INFINITE = None

class MarathonItem(ABC):
    @abstractmethod
    def get_metadata(self, resolver: Any) -> Tuple[Optional[str], bool, int]: pass
    def get_playback_params(self, resolver: Any, forced_count: int) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        query, is_movie, internal_count = self.get_metadata(resolver)
        play_count = INFINITE
        if forced_count > 0: play_count = forced_count
        elif internal_count > 0: play_count = internal_count
        elif is_movie: play_count = 1
        elif query:
            detected = get_play_count(query)
            if detected: play_count = detected
        q_season, q_episode = (extract_episode_range(query) if query else (None, None))
        return play_count, q_season, q_episode

class RegistryItem(MarathonItem):
    def __init__(self, key: str): self.key = key
    def get_metadata(self, resolver):
        data = resolver.get_query_data(self.key)
        return _extract_metadata_from_data(data, default_query=self.key)

class DirectItem(MarathonItem):
    def __init__(self, data: Any): self.data = data
    def get_metadata(self, resolver): return _extract_metadata_from_data(self.data)

def _extract_metadata_from_data(data: Any, default_query: Optional[str] = None) -> Tuple[Optional[str], bool, int]:
    query, is_movie, count = default_query, False, 0
    if isinstance(data, MarathonDefinition): query, is_movie, count = data.query, data.is_movie(), data.episode_count or 0
    elif isinstance(data, dict):
        query = data.get("query", query)
        count = data.get("episode_count", 0)
        if not query and "content" in data and isinstance(data["content"], dict): query = data["content"].get("query", query)
    elif isinstance(data, ContentItem): query, is_movie = data.query, data.is_movie()
    elif isinstance(data, str): query = data
    return query, is_movie, count

def create_marathon_item(raw_item: Any) -> MarathonItem:
    return RegistryItem(raw_item) if isinstance(raw_item, str) else DirectItem(raw_item)

def _resolve_marathon_collection(marathon: Marathon, boss: "DayDirector") -> Any:
    """Pick the day's content out of whatever shape a Marathon declares.

    Four shapes, in precedence order: a collection picks for itself, a
    MarathonSequence is passed through whole because its order *is* the
    marathon, a plain list is picked from deterministically by date, and
    anything else is already the content.
    """
    if hasattr(marathon.collection, "pick"):
        return marathon.collection.pick(boss)
    if isinstance(marathon.collection, MarathonSequence):
        return marathon.collection
    if isinstance(marathon.collection, list):
        return boss.pick(f"marathon_{marathon.name}", marathon.collection)
    return marathon.collection


def find_active_marathon(config: "ScheduleConfig", boss: "DayDirector", holiday_ctx: "HolidayContext") -> Tuple[Optional[Marathon], Any, Optional[Tuple[int, int]]]:
    from scripts.library.sources import MASTER_SOURCES
    if not config.enable_marathons or holiday_ctx.is_holiday_season: return None, None, None
    for m in sorted(config.marathons, key=lambda x: x.priority, reverse=True):
        if m.trigger(boss):
            hours = m.hours or (8, 24)
            collection = _resolve_marathon_collection(m, boss)
            if isinstance(collection, str) and (source_data := MASTER_SOURCES.get(collection)) and isinstance(source_data, MarathonDefinition) and source_data.start_hour is not None:
                hours = (source_data.start_hour, hours[1])
            config.logger.info(f"  {m.name} ACTIVE TODAY")
            return m, collection, hours
    return None, None, None

def _convert_marathon_to_block(marathon: Marathon, marathon_key: Any, resolver: Any, boss: "DayDirector", logger: Any, filler: Any = None) -> Block:
    data = resolver.get_query_data(marathon_key) if isinstance(marathon_key, str) else None
    epg_title, forced_play_count, start_mode, meta_season = marathon.name, 0, "beginning", None
    if isinstance(data, MarathonDefinition):
        epg_title, forced_play_count, start_mode, meta_season = data.name, data.episode_count or 0, data.start_mode, data.start_season
    elif isinstance(data, dict):
        epg_title, forced_play_count, start_mode, meta_season = data.get("title", epg_title), data.get("episode_count", 0), data.get("start_mode", "beginning"), data.get("start_season")

    sequence = marathon_key.items if isinstance(marathon_key, MarathonSequence) else (marathon_key if isinstance(marathon_key, list) else [marathon_key])
    program_items = []
    for i, raw_item in enumerate(sequence):
        item = create_marathon_item(raw_item)
        play_count, q_season, q_episode = item.get_playback_params(resolver, forced_play_count)
        start_point = (q_season, q_episode) if q_season is not None and q_episode is not None else None

        # A random start needs somewhere to start from, which means more than one
        # item. play_count is None for unbounded content (a whole show) and a
        # positive int otherwise -- so the only case with no room is exactly 1.
        # Testing `play_count > 1` excluded None, which is precisely the
        # unbounded content that declares start_mode="random" in the first
        # place, so this never fired for any marathon in the library.
        if i == 0 and start_mode == "random" and play_count != 1:
            r_season = meta_season if meta_season is not None else q_season
            if isinstance(meta_season, list):
                # Must be deterministic: the same date has to produce the same
                # schedule across processes. random.randint() reseeds per
                # process and would break that promise for the whole day.
                seasons = list(range(meta_season[0], meta_season[1] + 1))
                r_season = boss.pick(f"marathon_season:{epg_title}", seasons)
            if r_season is not None:
                start_point = (r_season, 1)
                logger.info(f"   🎲 Marathon random start configured: S{r_season}E1")

        # Unbounded content (a whole show, no episode range) has no meaningful
        # count. Substituting a large one is not "continuous play": ErsatzTV's
        # add_count applies no time bound and commits every item in a single
        # call, so a 6-hour slot became days of playout. Flag it instead, and
        # let the engine ask for exactly the remaining window via add_duration.
        program_items.append(Program(
            name=f"{epg_title} - Part {i+1}",
            content=raw_item,
            play_count=play_count,
            fill_window=play_count is None,
            start_point=start_point,
            force_start=True
        ))

    # Strategy "yield" ensures that if content runs out, we return to the Runner to pick up the normal schedule
    return Block(name=epg_title, items=program_items, use_epg_group=True, strict_window=True, fill_strategy="yield", filler=filler)

def _get_marathon_override(config: "ScheduleConfig", boss: "DayDirector", holiday_ctx: "HolidayContext") -> Tuple[Optional[Block], Optional[Tuple[int, int]]]:
    """Checks for active marathons and returns the block and window."""
    from scripts.logic.resolution.resolver import ContentResolver # Local import
    from scripts.library.sources import MASTER_SOURCES
    
    marathon_to_run, marathon_key, active_marathon_hours = find_active_marathon(config, boss, holiday_ctx)

    if marathon_to_run:
        resolver = ContentResolver(None, None, MASTER_SOURCES, config.logger)
        config.logger.info(f"🚀 MARATHON OVERRIDE: {marathon_to_run.name} will run from {active_marathon_hours[0]}:00 to {active_marathon_hours[1]}:00.")
        marathon_block = _convert_marathon_to_block(marathon_to_run, marathon_key, resolver, boss, config.logger, filler=config.filler_content)
        return marathon_block, active_marathon_hours
    return None, None

# --- Schedule Assembly ---

def assemble_day_schedule(config: "ScheduleConfig", boss: "DayDirector", holiday_ctx: "HolidayContext") -> Tuple[Dict[str, Any], Optional[Block], Optional[Tuple[int, int]]]:
    """
    Constructs the effective schedule for the day by applying:
    1. Day-of-week selection
    2. Global seasonal ramps
    3. Holiday schedule swaps/overrides
    """
    day_schedule = config.schedules.get("WEEKDAY", {})
    for key in config.schedules:
        if key != "WEEKDAY" and boss.has(key):
            day_schedule = config.schedules[key]
            break
    day_schedule = day_schedule.copy()

    if config.global_seasonal_ramps:
        active_ramp = False
        for holiday_name in config.global_seasonal_ramps:
            if holiday_ctx.envelope.get(holiday_name.lower(), 0.0) > 0 or holiday_ctx.envelope.get(f"{holiday_name.lower()}_hangover", 0.0) > 0:
                active_ramp = True
                break
        if active_ramp:
            def wrap_values(d):
                return {k: wrap_values(v) if isinstance(v, dict) else SeasonalBlock(base=v, seasonal=config.global_seasonal_ramps, blend_ratio=1.0) for k, v in d.items()}
            day_schedule = wrap_values(day_schedule)

    if config.holiday_schedules:
        for holiday_name, holiday_sched in config.holiday_schedules.items():
            holiday_label = holiday_name.upper()
            holiday_key = holiday_name.lower()
            is_holiday_day = boss.has(holiday_label)
            profile_obj = config.block_profiles.get(holiday_label, config.block_profiles.get("default"))
            profile_set = profile_obj.blocks if isinstance(profile_obj, HolidayProfile) else (profile_obj if isinstance(profile_obj, dict) else {})

            for slot, content in holiday_sched.items():
                if slot not in day_schedule: continue
                if is_holiday_day:
                    day_schedule[slot] = content
                    continue
                profile = profile_set.get(slot, BlockProfile())
                ramp_signal = holiday_ctx.envelope.get(holiday_key, 0.0)
                hangover_signal = holiday_ctx.envelope.get(f"{holiday_key}_hangover", 0.0)
                final_prob = profile.respond(ramp_signal, hangover_signal)
                if final_prob > 0 and boss.roll(final_prob, key=f"swap_{holiday_key}_{slot}"):
                    day_schedule[slot] = content

    # --- Marathon Override Logic ---
    marathon_block, marathon_window = _get_marathon_override(config, boss, holiday_ctx)

    return day_schedule, marathon_block, marathon_window