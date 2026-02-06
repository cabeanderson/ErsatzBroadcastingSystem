"""
80s TV Channel - A Blast from the Past

Channel Philosophy:
A 24/7 celebration of the 1980s, mixing iconic TV shows, blockbuster movies,
and classic cartoons. The schedule is structured to provide a different feel
throughout the day, with a special focus on themed prime time blocks.

- Morning (6am-12pm): Light and fun content, cartoons or family sitcoms.
- Daytime (12pm-6pm): A rotation of dramas, action shows, and movie matinees.
- Prime Time (6pm-11pm): Curated, themed blocks for each night of the week.
- Late Night (11pm-6am): Music videos, cult movies, and late-night talk.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import eighties

# ==============================================================================
# 2. SCHEDULE ASSEMBLY
# ==============================================================================

# Combine the chosen blocks into a daily schedule structure.
# The `expand_timeslots` function will map these named slots to hour ranges.
SCHEDULES = {
    "WEEKDAY": {
        "morning": eighties.SEASONAL_MORNING_BLOCK,
        "midday": eighties.SEASONAL_DAYTIME_BLOCK,
        "afternoon": eighties.SEASONAL_DAYTIME_BLOCK,
        "evening": eighties.PRIME_TIME_BLOCKS, # Prime time starts in the evening slot
        "prime": eighties.PRIME_TIME_BLOCKS,
        "night": eighties.LATE_NIGHT_BLOCK,
        "overnight": eighties.LATE_NIGHT_BLOCK
    },
    "WEEKEND": {
        # Weekends could have a different structure, but we'll use the same for simplicity.
        "morning": eighties.SEASONAL_MORNING_BLOCK,
        "midday": eighties.SEASONAL_DAYTIME_BLOCK,
        "afternoon": "eighties_weekend_movie", # Weekend afternoon movie
        "evening": eighties.PRIME_TIME_BLOCKS,
        "prime": eighties.PRIME_TIME_BLOCKS,
        "night": eighties.LATE_NIGHT_BLOCK,
        "overnight": eighties.LATE_NIGHT_BLOCK
    }
}


# ==============================================================================
# 3. ERSATZTV INTEGRATION
# ==============================================================================

def build_playout(api, context, build_id):
    """Build the daily playout schedule."""
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset="default", # Uses standard broadcast dayparts
        logger=ChannelLogger(prefix="[80s TV]"),
        fallback_content="eighties_music_videos", # Fallback if all else fails
        enable_commercials=True,
        enable_filler=True
    )
    return run_daily_schedule(api, context, build_id, config)

# Other required functions (can be left as-is)
def define_content(api, context, build_id): pass
def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))
