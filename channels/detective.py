"""
Detective Channel - Crime, Mystery, and Procedurals

Features:
- "PlayOnce" Lunch Special (Specific daily episodes)
- British Crime Block (Evening)
- USA Network "Blue Sky" Block (Morning/Afternoon)
- Weekend Marathons (Columbo, Poirot)
"""

from etv_client.models import ControlWaitUntil
from scripts.schedule import run_daily_schedule, ScheduleConfig
from scripts.logic import triggers, Marathon, PlayOnce, Swap
from scripts.logic.seasonal import SeasonalBlock
from scripts.library import detective
from scripts.core.logger import ChannelLogger
from datetime import date

# ==============================================================================
# 1. MARATHONS - Special event programming
# ==============================================================================

MARATHONS = [
    Marathon(
        name="Monk: The Trudy Arc",
        trigger=triggers.chance(0.01, "monk_trudy_marathon"),
        collection="monk_trudy_arc_tv",
        hours=(10, 23)
    )
]

# ==============================================================================
# 2. SEASONAL BLOCKS
# ==============================================================================

SEASONAL_BLOCKS = {}

PRIME_SEASONAL = SeasonalBlock(
    base=detective.DETECTIVE_TUESDAY_BLUESKY, # Default base if needed
    seasonal={
        "FALL": Swap(detective.NOIR_NOVEMBER_COLLECTION) # Noir November takeover
    }
)

# ==============================================================================
# 3. BLOCK DEFINITIONS
# ==============================================================================

PRIME_BLOCK = {
    "MONDAY": detective.DETECTIVE_MONDAY_BRITISH,
    "TUESDAY": detective.DETECTIVE_TUESDAY_BLUESKY,
    "WEDNESDAY": detective.DETECTIVE_WEDNESDAY_HARDBOILED,
    "THURSDAY": detective.DETECTIVE_THURSDAY_WHODUNIT,
    "FRIDAY": detective.DETECTIVE_FRIDAY_RETRO,
    "default": PRIME_SEASONAL
}

# ==============================================================================
# 4. SCHEDULE DEFINITIONS
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": detective.DETECTIVE_LATE_NIGHT,
        "morning": detective.DETECTIVE_USA_BLOCK, # Monk/Psych
        "midday": detective.DETECTIVE_USA_BLOCK,
        "noon": PlayOnce({
            "WEEKDAY_A": "elsbeth_tv",     # Explicit
            "WEEKDAY_B": "moonlighting_tv",
            "default": "procedural_tv"     # True fallback
        }),
        "afternoon": detective.DETECTIVE_USA_BLOCK, # Monk/Psych
        "evening": SeasonalBlock(
            base=detective.DETECTIVE_BRITISH_BLOCK,
            seasonal={
                "SUMMER": Swap("monk_chronological_tv"),
                "FALL": Swap("monk_chronological_tv")
            }
        ),
        "prime": PRIME_BLOCK,
        "night": detective.DETECTIVE_LATE_NIGHT
    },
    "SATURDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": "procedural_tv",
        "morning": "procedural_tv",
        "midday": "poirot_tv",
        "noon": "poirot_tv",
        "afternoon": "miss_marple_tv",
        "evening": detective.MYSTERY_MOVIE_WHEEL,
        "prime": detective.MYSTERY_MOVIE_WHEEL,
        "night": "poirot_tv"
    },
    "SUNDAY": {
        "overnight": detective.DETECTIVE_LATE_NIGHT,
        "early": "procedural_tv",
        "morning": "procedural_tv",
        "midday": "poirot_tv",
        "noon": "poirot_tv",
        "afternoon": "miss_marple_tv",
        "evening": "columbo_tv",
        "prime": detective.SUNDAY_PRESTIGE_BLOCK, # Sequential Block
        "night": "poirot_tv"
    }
}

# ==============================================================================
# 5. ERSATZTV INTEGRATION
# ==============================================================================

def define_content(api, context, build_id):
    pass

def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(
        when="00:00", 
        tomorrow=False, 
        rewind_on_reset=True
    ))

def build_playout(api, context, build_id):
    config = ScheduleConfig(
        schedules=SCHEDULES,
        marathons=MARATHONS,
        logger=ChannelLogger(prefix="[DETECTIVE]"),
        fallback_content="procedural_tv"
    )
    return run_daily_schedule(api, context, build_id, config)
