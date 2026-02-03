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
from scripts.library import collections, structures
from scripts.playout import ChannelLogger
from datetime import date

MARATHONS = [
    Marathon(
        name="Monk: The Trudy Arc",
        trigger=triggers.chance(0.01, "monk_trudy_marathon"),
        collection="monk_trudy_arc_tv",
        hours=(10, 23)
    )
]

# SUNDAY CRIME NIGHT (Sequential)
# True Detective S1 (8 eps) -> Fargo S1 (10 eps) -> Mare of Easttown (7 eps)
# Start Date: Jan 4, 2026
# True Detective S1 (8 eps) -> Fargo S1 (10 eps)
SUNDAY_CRIME_BLOCK = structures.SeriesRelay(
    items=[("true_detective_s1", 8), ("fargo_s1", 10)],
    start_date="WINTER", # Start at the beginning of the Winter season
    frequency="weekly"
)

SEASONAL_BLOCKS = {}

SCHEDULES = {
    "WEEKDAY": {
        "overnight": collections.DETECTIVE_LATE_NIGHT,
        "early": collections.DETECTIVE_LATE_NIGHT,
        "morning": collections.DETECTIVE_USA_BLOCK, # Monk/Psych
        "midday": collections.DETECTIVE_USA_BLOCK,
        "noon": PlayOnce({
            "WEEKDAY_A": "elsbeth_tv",     # Explicit
            "WEEKDAY_B": "moonlighting_tv",
            "default": "procedural_tv"     # True fallback
        }),
        "afternoon": collections.DETECTIVE_USA_BLOCK, # Monk/Psych
        "evening": SeasonalBlock(
            base=collections.DETECTIVE_BRITISH_BLOCK,
            seasonal={
                "SUMMER": Swap("monk_chronological_tv"),
                "FALL": Swap("monk_chronological_tv")
            }
        ),
        "prime": collections.DETECTIVE_USA_BLOCK,
        "night": collections.DETECTIVE_LATE_NIGHT
    },
    "SATURDAY": {
        "overnight": collections.DETECTIVE_LATE_NIGHT,
        "early": "procedural_tv",
        "morning": "procedural_tv",
        "midday": "poirot_tv",
        "noon": "poirot_tv",
        "afternoon": "miss_marple_tv",
        "evening": "columbo_tv",
        "prime": "columbo_tv",
        "night": "poirot_tv"
    },
    "SUNDAY": {
        "overnight": collections.DETECTIVE_LATE_NIGHT,
        "early": "procedural_tv",
        "morning": "procedural_tv",
        "midday": "poirot_tv",
        "noon": "poirot_tv",
        "afternoon": "miss_marple_tv",
        "evening": "columbo_tv",
        "prime": SUNDAY_CRIME_BLOCK, # Sequential Block
        "night": "poirot_tv"
    }
}

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
