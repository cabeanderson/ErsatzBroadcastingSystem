"""
Example Channel Configuration
-----------------------------
This file demonstrates every major feature of the ErsatzTV Scheduling Framework.
It serves as a reference for creating your own channels.

To run this channel:
1. Ensure you have content keys defined in library/sources.py
2. Run from project root: python3 -m channels.example_channel
"""

import os
import sys
from datetime import datetime

# Add project root to path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.scheduling.pre_registration import pre_register_all_content
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic.resolution.resolver import ContentResolver
from scripts.library.sources import MASTER_SOURCES
from scripts.logic.structures import Block, OrderedCollection
from scripts.logic.calendar.holidays import with_holidays
from scripts.logic.triggers import chance, has_label, on_date
from scripts.logic.models import Marathon, BlockProfile, Feather, Swap
from scripts.core.logger import ChannelLogger
# In a real channel, you would import your collections:
# from scripts.library import collections

# ==============================================================================
# 1. CUSTOM TIMESLOTS
# ==============================================================================
# Define named time ranges for your schedule.
# You can use "default", "kids", "movies" presets, or define your own.
# Format: "name": (start_hour, end_hour)
# Note: (22, 6) wraps around midnight.
MY_TIMESLOTS = {
    "morning": (6, 10),
    "midday": (10, 14),
    "afternoon": (14, 18),
    "prime": (18, 22),
    "late_night": (22, 2),
    "graveyard": (2, 6)
}

# ==============================================================================
# 2. COMPLEX BLOCKS & PROGRAMMING
# ==============================================================================

# --- Branded Block ---
# A block with intro, outro, and bumpers between items.
# Content keys must exist in library/sources.py
SATURDAY_MORNING_BLOCK = Block(
    name="Saturday Morning Cartoons",
    # Must be a collection (anything with .pick) or a list -- a bare key string
    # plays nothing and stalls the slot. See KNOWN_ISSUES.md.
    items=OrderedCollection(["collection_80s_cartoons"]),
    intro="intro_saturday_morning",     # Key for intro video
    outro="outro_saturday_morning",     # Key for outro video
    bumpers="bumpers_cartoons",         # Key for bumpers
    use_epg_group=True
)

# --- Seasonal Block ---
# Content that changes based on the season (Winter, Spring, Summer, Fall).
# 'base' plays normally. 'seasonal' blends in based on season strength.
EVENING_MOVIES = SeasonalBlock(
    base="collection_general_movies",
    seasonal={
        "WINTER": Feather("collection_christmas_movies", ratio=0.4), # 40% chance in Winter
        "SUMMER": Swap("collection_blockbuster_movies"),             # 100% swap in Summer
        "OCTOBER": Swap("collection_horror_movies")                  # Custom season/month
    },
    blend_ratio=1.0
)

# --- Block Profiles ---
# Define how aggressive holiday takeovers are for specific slots.
# "bias": Increases/decreases probability of holiday content.
MY_PROFILES = {
    "prime": BlockProfile(max_ratio=1.0, bias=0.2), # Aggressive holiday takeover
    "late_night": BlockProfile(max_ratio=0.5, bias=-0.1) # Subtle holiday takeover
}

# ==============================================================================
# 3. MARATHONS
# ==============================================================================
# Special events that take over the schedule when triggered.
# Checked daily.
MARATHONS = [
    Marathon(
        name="Sci-Fi Saturday",
        # Trigger: 20% chance, but ONLY on Saturdays
        trigger=lambda boss: boss.has("SATURDAY") and boss.roll(0.20, "scifi_marathon"),
        collection="collection_scifi_series",
        hours=(12, 24),  # Runs from noon to midnight
        priority=10      # Higher priority overrides other marathons
    ),
    Marathon(
        name="Star Wars May 4th",
        # Trigger: Specific date range
        trigger=on_date(5, 4),
        collection="collection_star_wars",
        hours=(8, 24),
        priority=50
    )
]

# ==============================================================================
# 4. WEEKLY SCHEDULE
# ==============================================================================
# Define what plays during which timeslots for different day types.
# Keys can be: "WEEKDAY", "WEEKEND", "MONDAY", "TUESDAY", etc.
# Specific days override general groups.

SCHEDULE = {
    "WEEKDAY": {
        "morning": "collection_news_and_weather",
        "midday": "collection_sitcoms",
        # Single play slot: Plays one item, then fills rest of slot with next block
        "afternoon": Block(
            name="Daily Talkshow",
            items=["show_daily_talkshow"],
            fill_strategy="bridge",
            strict_window=False
        ),
        "prime": with_holidays(
            "collection_drama_series",
            # Overrides for specific holidays
            halloween="collection_horror_movies",
            christmas="collection_holiday_specials"
        ),
        "late_night": "collection_adult_swim",
        "graveyard": "collection_infomercials"
    },
    "FRIDAY": {
        # Friday specific overrides
        "prime": EVENING_MOVIES, # Uses the SeasonalBlock defined above
        "late_night": "collection_horror_movies"
    },
    "SATURDAY": {
        "morning": SATURDAY_MORNING_BLOCK, # Uses BrandedBlock
        "midday": "collection_sports",
        "prime": "collection_action_movies"
    },
    "SUNDAY": {
        "morning": "collection_classic_cartoons",
        "midday": "collection_documentaries",
        "prime": "collection_prestige_drama"
    }
}

# ==============================================================================
# 5. HOLIDAY SCHEDULES (FULL DAY TAKEOVERS)
# ==============================================================================
# Completely replace the schedule on specific holidays.

HOLIDAY_SCHEDULES = {
    "CHRISTMAS": {
        "morning": "collection_yule_log",
        "midday": "collection_christmas_parade",
        "afternoon": "collection_christmas_movies",
        "prime": "collection_classic_christmas_movies",
        "late_night": "collection_yule_log"
    }
}

# ==============================================================================
# 6. CONFIGURATION & EXECUTION
# ==============================================================================

def get_config(verbose=True):
    """Creates and returns the ScheduleConfig object."""
    logger = ChannelLogger(prefix="[EXAMPLE-TV]", verbose=verbose)

    return ScheduleConfig(
        # The main schedule
        schedules=SCHEDULE,
        
        # Marathons list
        marathons=MARATHONS,
        
        # Timeslot definitions
        timeslot_preset="custom", # Use 'custom' when providing custom_timeslots
        custom_timeslots=MY_TIMESLOTS,
        
        # Full day holiday schedules
        holiday_schedules=HOLIDAY_SCHEDULES,
        
        # Global overrides (applies to ALL slots if holiday is active)
        # Use sparingly, usually better to use with_holidays() in schedule
        global_holiday_overrides={
            "new_years_eve": "collection_party_music"
        },
        
        # Global seasonal ramps (experimental)
        # Defines content that slowly blends in globally based on season
        global_seasonal_ramps={
            "WINTER": "collection_winter_bumpers"
        },
        
        # Block profiles (controls holiday blend aggression)
        block_profiles=MY_PROFILES,
        
        # Filler content to pad time at hour boundaries
        filler_content="collection_music_videos",
        
        # Fallback if something goes wrong or content is missing
        fallback_content="collection_fallback_loops",
        
        # Commercial settings
        commercial_duration=0, # Seconds (0 to disable global commercials)
        commercial_content="commercials_spot",
        
        logger=logger
    )

# ==============================================================================
# 7. ENTRYPOINT FUNCTIONS (Required by ErsatzTV)
# ==============================================================================

def define_content(api, context, build_id):
    """Called by ErsatzTV to register content before playout."""
    config = get_config(verbose=True)
    resolver = ContentResolver(api, build_id, MASTER_SOURCES, config.logger)
    pre_register_all_content(resolver, config)

def reset_playout(api, context, build_id):
    """Called by ErsatzTV if mode is 'reset'."""
    return context

def build_playout(api, context, build_id):
    """Called by ErsatzTV to generate the schedule."""
    config = get_config(verbose=True)
    return run_daily_schedule(api, context, build_id, config)

if __name__ == "__main__":
    # Simulator Mode
    print("Running simulator for Example Channel...")
    # The simulator expects the module to have a build_playout function, which we now have.
    from scripts.testing.simulator import test_channel
    test_channel(sys.modules[__name__])