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
from scripts.scheduling import run_daily_schedule, ScheduleConfig

# Framework - Logic
from scripts.logic.models import Marathon
from scripts.logic.calendar.seasonal import SeasonalBlock
from scripts.logic import triggers, Swap, profiles

# Framework - Content
from scripts.library import animation, common
from scripts.core.logger import ChannelLogger

# ==============================================================================
# 1. MARATHONS - Special event programming
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Cowboy Bebop",
        trigger=triggers.chance(0.01, "bebop_marathon"),
        collection=animation.COWBOY_BEBOP_COMPLETE,
        hours=(10, 24),
        priority=2
    ),
    Marathon(
        name="DBZ Marathon",
        trigger=triggers.chance(0.02, "dbz_takeover"),
        collection=animation.DBZ_SAGAS,
        hours=(10, 24),  # 10am-midnight takeover
        priority=2
    ),
    Marathon(
        name="Simpsons Marathon",
        trigger=triggers.chance(0.01, "simpsons_takeover"),
        collection=animation.SIMPSONS_MARATHON,
        hours=(16, 22),  # 4pm-10pm takeover
        priority=1
    ),
    Marathon(
        name="Toonami Takeover",
        trigger=triggers.chance(0.01, "toonami_takeover"),
        collection=animation.TOONAMI_BLOCK.items,
        hours=(12, 24),
        priority=2
    ),
    Marathon(
        name="Star Wars Animation Day",
        trigger=triggers.has_label("STAR_WARS_DAY"),
        collection=animation.STAR_WARS_ANIMATION,
        hours=(8, 22),
        priority=2
    )
]

# ==============================================================================
# 2. SEASONAL VARIANTS - Content that changes with seasons
# ==============================================================================

# Use pre-defined seasonal blocks from animation library
SEASONAL_HEROES = animation.CN_MORNING_HERO
SEASONAL_AFTERNOON = animation.CN_AFTERNOON_BLOCK

# ==============================================================================
# 3. BLOCK DEFINITIONS (Chronological)
# ==============================================================================

# Early Block (06:00 - 08:00)
EARLY_BLOCK = {
    "WEEKDAY": animation.DISNEY_MORNING,
    "default": animation.CLASSIC_CARTOONS
}

# Morning Block (08:00 - 10:00)
MORNING_BLOCK = {
    "SATURDAY": animation.SATURDAY_MORNING,
    "SUNDAY": animation.CLASSIC_CARTOONS,
    "default": SEASONAL_HEROES
}

# Midday Block (10:00 - 12:00)
MIDDAY_BLOCK = {
    "SATURDAY": SEASONAL_HEROES,
    "SUNDAY": animation.CLASSIC_CARTOONS,
    "default": animation.CARTOON_NETWORK_CLASSICS
}

# Noon Block (12:00 - 14:00)
NOON_BLOCK = {
    "SUNDAY": animation.ANIMATION_SHOWCASE,
    "default": animation.NICKTOONS_VAULT
}

# Afternoon Block (14:00 - 18:00)
AFTERNOON_BLOCK = {
    "SUNDAY": animation.ANIMATION_SHOWCASE,
    "default": SEASONAL_AFTERNOON
}

# Evening Block (18:00 - 20:00)
EVENING_BLOCK = {
    "SATURDAY": animation.ANIME_BLOCK,
    "SUNDAY": animation.ANIMATION_SHOWCASE,
    "default": animation.TOONAMI_BLOCK
}

# Prime Block (20:00 - 23:00)
PRIME_BLOCK = {
    "SATURDAY": animation.ANIMATION_SHOWCASE,
    "SUNDAY": animation.FOX_PRIMETIME,
    "WEEKDAY_A": animation.AS_PRIME_A, # Mon/Wed/Fri
    "WEEKDAY_B": animation.AS_PRIME_B, # Tue/Thu
    "default": animation.AS_PRIME_B
}

# Night Block (23:00 - 02:00)
NIGHT_BLOCK = {
    "SATURDAY": animation.ANIME_BLOCK,
    "WEEKDAY_A": animation.AS_NIGHT_A, # Mon/Wed/Fri
    "default": animation.AS_NIGHT_B    # Tue/Thu/Sun
}

# ==============================================================================
# 4. HOLIDAY OVERRIDES - Applied globally
# ==============================================================================

HALLOWEEN_SCHEDULE = {
    "overnight": common.HALLOWEEN_ADULT_SCARES,
    "morning": common.HALLOWEEN_KIDS_SPOOKFEST,
    "midday": common.HALLOWEEN_TEEN_FRIGHTS,
    "afternoon": common.HALLOWEEN_TEEN_FRIGHTS,
    "evening": common.HALLOWEEN_TEEN_FRIGHTS,
    "prime": common.HALLOWEEN_TV_EVENT,
    "night": common.HALLOWEEN_ADULT_SCARES,
}

# For Christmas, take over all default timeslots with the Christmas event collection
CHRISTMAS_SCHEDULE = {
    "overnight": common.CHRISTMAS_TV_EVENT,
    "morning": common.CHRISTMAS_TV_EVENT,
    "midday": common.CHRISTMAS_TV_EVENT,
    "afternoon": common.CHRISTMAS_TV_EVENT,
    "evening": common.CHRISTMAS_TV_EVENT,
    "prime": "christmas_animated_movie",
    "night": common.CHRISTMAS_TV_EVENT,
}

HOLIDAY_SCHEDULES = {
    "HALLOWEEN": HALLOWEEN_SCHEDULE, "CHRISTMAS": CHRISTMAS_SCHEDULE
}

# ==============================================================================
# 5. SCHEDULE DEFINITIONS
# ==============================================================================

DAILY_SCHEDULE = {
    "overnight": animation.CLASSIC_CARTOONS,
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


# ==============================================================================
# 6. ERSATZTV INTEGRATION
# ==============================================================================

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
        block_profiles={}, # Use defaults from HOLIDAY_PROFILES
        filler_content="adult_swim_bumpers",
        logger=ChannelLogger(prefix="[CARTOONS]"),
        fallback_content=animation.CLASSIC_CARTOONS,
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True,
        enable_bumpers=True
    )
    
    return run_daily_schedule(api, context, build_id, config)