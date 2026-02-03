"""
Cartoon Network - 24/7 Animation Programming

Features:
- Saturday morning cartoons block
- DBZ and Simpsons marathons (probabilistic triggers)
- Seasonal superhero variants (Marvel in spring, DC otherwise)
- Holiday overrides (Halloween/Christmas special events)
- Adult Swim late-night programming
- Day-of-week variations (Tuesday/Thursday animation showcase)

Schedule Philosophy:
- Overnight (2-6am): Adult Swim after-dark content
- Morning (6-10am): Kid-friendly, energetic programming
- Midday (10-2pm): Classic cartoons and vault content
- Afternoon (2-7pm): Action/adventure, seasonal variants
- Prime (7-10pm): Premium animation, FOX primetime
- Late Night (10-2am): Anime and adult animation
"""

# ErsatzTV
from etv_client.models import ControlWaitUntil

# Framework - Orchestration
from scripts.schedule import run_daily_schedule, ScheduleConfig

# Framework - Logic
from scripts.logic.models import Marathon
from scripts.logic.seasonal import SeasonalBlock
from scripts.logic import triggers, Swap
from scripts.logic.profiles import STANDARD_PROFILES, CHRISTMAS_PROFILES

# Framework - Content
from scripts.library import collections, blocks
from scripts.playout import ChannelLogger

# MARATHONS - Special event programming

MARATHONS = [
    Marathon(
        name="Cowboy Bebop",
        trigger=triggers.chance(0.01, "bebop_marathon"),
        collection="cowboy_bebop_complete",
        hours=(10, 24),
        priority=2
    ),
    Marathon(
        name="DBZ Marathon",
        trigger=triggers.chance(0.02, "dbz_takeover"),
        collection=collections.DBZ_SAGAS,
        hours=(10, 24),  # 10am-midnight takeover
        priority=2
    ),
    Marathon(
        name="Simpsons Marathon",
        trigger=triggers.chance(0.01, "simpsons_takeover"),
        collection=collections.SIMPSONS_MARATHON,
        hours=(16, 22),  # 4pm-10pm takeover
        priority=1
    ),
    Marathon(
        name="Toonami Takeover",
        trigger=triggers.chance(0.01, "toonami_takeover"),
        collection=collections.TOONAMI_MAIN,
        hours=(12, 24),
        priority=2
    ),
    Marathon(
        name="Star Wars Animation Day",
        trigger=triggers.has_label("STAR_WARS_DAY"),
        collection=collections.STAR_WARS_ANIMATION,
        hours=(8, 22),
        priority=2
    )
]

# SEASONAL VARIANTS - Content that changes with seasons

SEASONAL_HEROES = SeasonalBlock(
    base=collections.SUPERHERO_HOUR,
    seasonal={
        "SPRING": Swap(collections.MARVEL_HOUR)
    }
)

SEASONAL_AFTERNOON = SeasonalBlock(
    base=collections.DISNEY_AFTERNOON,
    seasonal={
        "SPRING": Swap(collections.WB_AFTERNOON)
    }
)

# ==============================================================================
# 1. BLOCK DEFINITIONS (Chronological)
# ==============================================================================

# Early Block (06:00 - 08:00)
EARLY_BLOCK = {
    "WEEKDAY": collections.DISNEY_MORNING,
    "default": collections.CLASSIC_CARTOONS
}

# Morning Block (08:00 - 10:00)
MORNING_BLOCK = {
    "SATURDAY": collections.SATURDAY_MORNING,
    "SUNDAY": collections.CLASSIC_CARTOONS,
    "default": SEASONAL_HEROES
}

# Midday Block (10:00 - 12:00)
MIDDAY_BLOCK = {
    "SATURDAY": SEASONAL_HEROES,
    "SUNDAY": collections.CLASSIC_CARTOONS,
    "default": collections.CARTOON_NETWORK_CLASSICS
}

# Noon Block (12:00 - 14:00)
NOON_BLOCK = {
    "SUNDAY": collections.ANIMATION_SHOWCASE,
    "default": collections.NICKTOONS_VAULT
}

# Afternoon Block (14:00 - 18:00)
AFTERNOON_BLOCK = {
    "SUNDAY": collections.ANIMATION_SHOWCASE,
    "default": SEASONAL_AFTERNOON
}

# Evening Block (18:00 - 20:00)
EVENING_BLOCK = {
    "SATURDAY": collections.ANIME_BLOCK,
    "SUNDAY": collections.ANIMATION_SHOWCASE,
    "default": blocks.TOONAMI_BLOCK
}

# Prime Block (20:00 - 23:00)
PRIME_BLOCK = {
    "SATURDAY": collections.ANIMATION_SHOWCASE,
    "SUNDAY": collections.FOX_PRIMETIME,
    "default": blocks.ADULT_SWIM_BLOCK
}

# Night Block (23:00 - 02:00)
NIGHT_BLOCK = {
    "SATURDAY": collections.ANIME_BLOCK,
    "SUNDAY": blocks.ADULT_SWIM_BLOCK,
    "default": blocks.ADULT_SWIM_WEIRD
}

# HOLIDAY OVERRIDES - Applied globally

HALLOWEEN_SCHEDULE = {
    "overnight": collections.HALLOWEEN_ADULT_SCARES,
    "morning": collections.HALLOWEEN_KIDS_SPOOKFEST,
    "midday": collections.HALLOWEEN_TEEN_FRIGHTS,
    "afternoon": collections.HALLOWEEN_TEEN_FRIGHTS,
    "evening": collections.HALLOWEEN_TEEN_FRIGHTS,
    "prime": collections.HALLOWEEN_TV_EVENT,
    "night": collections.HALLOWEEN_ADULT_SCARES,
}

# For Christmas, take over all default timeslots with the Christmas event collection
CHRISTMAS_SCHEDULE = {
    "overnight": collections.CHRISTMAS_TV_EVENT,
    "morning": collections.CHRISTMAS_TV_EVENT,
    "midday": collections.CHRISTMAS_TV_EVENT,
    "afternoon": collections.CHRISTMAS_TV_EVENT,
    "evening": collections.CHRISTMAS_TV_EVENT,
    "prime": "christmas_animated_movie",
    "night": collections.CHRISTMAS_TV_EVENT,
}

HOLIDAY_SCHEDULES = {
    "HALLOWEEN": HALLOWEEN_SCHEDULE, "CHRISTMAS": CHRISTMAS_SCHEDULE
}

# ==============================================================================
# 2. SCHEDULE DEFINITIONS
# ==============================================================================

DAILY_SCHEDULE = {
    "overnight": collections.CLASSIC_CARTOONS,
    "early": EARLY_BLOCK,
    "morning": MORNING_BLOCK,
    "midday": MIDDAY_BLOCK,
    "noon": NOON_BLOCK,
    "afternoon": AFTERNOON_BLOCK,
    "evening": EVENING_BLOCK,
    "prime": PRIME_BLOCK,
    "night": NIGHT_BLOCK
}

SCHEDULES = {
    "WEEKDAY": DAILY_SCHEDULE,
    "WEEKEND": DAILY_SCHEDULE
}


# ERSATZTV INTEGRATION

def define_content(api, context, build_id):
    """ErsatzTV content definition hook (unused in scripted mode)."""
    pass

def reset_playout(api, context, build_id):
    """Reset playout to midnight with rewind."""
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00", 
        tomorrow=False, 
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    """Build the daily playout schedule."""
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        holiday_schedules=HOLIDAY_SCHEDULES,
        timeslot_preset="default",
        block_profiles={
            "HALLOWEEN": STANDARD_PROFILES, # TODO: Use a specific Halloween profile
            "CHRISTMAS": CHRISTMAS_PROFILES # TODO: Use a specific Christmas profile
        },
        filler_content=None,  # TODO: Add collections.BUMPERS when available
        logger=ChannelLogger(prefix="[CARTOONS]"),
        fallback_content=collections.CLASSIC_CARTOONS
    )
    
    return run_daily_schedule(api, context, build_id, config)