"""
Totally 80s -- the decade as a broadcast day

Cartoons at breakfast, a genre wheel and a cult matinee through the daytime, the
after-school syndication strip at five, a named night at eight, sketch comedy at
eleven, and action and drama reruns overnight until the videos take the last two
hours before the cartoons.

The channel owns the 1980s as a *theme*, which is not the same as owning 1980s
film: `library/modern_movies.py` and this channel split the decade's film shelf
by hours, 06:00-22:00 here and 22:00-06:00 on Be Kind Rewind. That contract is
why the cult movie is at noon. See the docstring in `library/eighties.py`.

Redesigned 2026-09-01, and it was the last channel on the default timeslot
preset. What the pass found, beyond the six empty content keys that were the
known defect:

- **Four hours a day were not programmed at all.** The schedule named no
  `early` (06:00-08:00) and no `noon` (12:00-14:00) slot, so both fell through
  to `fallback_content`. With `night` and `overnight` already on music video,
  eleven of the channel's twenty-four hours were `eighties_music_videos`.
- **`evening` and `prime` were handed the same Block object**, so a two-item
  collection was stretched over 17:00-23:00 and a "night" was six hours long.
- **`night: (23, 2)` wrapped midnight**, the replay bug Cartoon Network, Nick,
  Disney and High Noon each carry their own map to avoid.
"""

from etv_client.models import ControlWaitUntil
from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import eighties

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# `late` is 23-24 and `night` is 00-02, each with its own slot, rather than the
# default's single `night: (23, 2)`. A wrapping slot is entered twice under two
# different day labels, so "Saturday night" resolves to two different nights and
# a collection replays its first items across the boundary.
#
# Film runs 10:00-22:00 and stops there: 22:00-06:00 is Be Kind Rewind's half of
# the 1980s film shelf.
#
# `night` and `overnight` were 00:00-02:00 and 02:00-06:00 and *both* held
# `eighties_music_videos`, which matched nothing on the server -- six hours of
# dead air a day, and the largest single defect the 2026-09-02 guide showed.
# The music video library is dated now, but honestly dated: 35 videos fall in
# 1975-1989, which is 152 minutes. So the video block is two hours, not six, and
# the four hours it gives up go to late-night television.

EIGHTIES_TIMESLOTS = {
    "night":     (0, 4),     # 80s late-night television
    "overnight": (4, 6),     # The Video Jukebox
    "early":     (6, 8),     # cartoons, every day of the year
    "morning":   (8, 10),    # cartoons, or sitcoms once school is back
    "midday":    (10, 12),   # the genre wheel
    "noon":      (12, 14),   # The Cult Matinee
    "afternoon": (14, 17),   # the genre wheel / the weekend film
    "evening":   (17, 20),   # the syndication strip
    "prime":     (20, 23),   # the named night
    "late":      (23, 24),   # The Sketch Hour
}

# ==============================================================================
# 2. SCHEDULE ASSEMBLY
# ==============================================================================

SCHEDULES = {
    "WEEKDAY": {
        "night":     eighties.LATE_NIGHT_TV_BLOCK,
        "overnight": eighties.VIDEO_JUKEBOX_BLOCK,
        "early":     eighties.MORNING_CARTOONS,
        "morning":   eighties.SEASONAL_MORNING_BLOCK,
        "midday":    eighties.SEASONAL_DAYTIME_BLOCK,
        "noon":      eighties.CULT_MATINEE_BLOCK,
        "afternoon": eighties.SEASONAL_DAYTIME_BLOCK,
        "evening":   eighties.EVENING_SYNDICATION,
        "prime":     eighties.PRIME_TIME_BLOCKS,
        "late":      eighties.SKETCH_HOUR_BLOCK,
    },
    "WEEKEND": {
        "night":     eighties.LATE_NIGHT_TV_BLOCK,
        "overnight": eighties.VIDEO_JUKEBOX_BLOCK,
        "early":     eighties.MORNING_CARTOONS,
        "morning":   eighties.SEASONAL_MORNING_BLOCK,
        "midday":    eighties.SEASONAL_DAYTIME_BLOCK,
        "noon":      eighties.CULT_MATINEE_BLOCK,
        # The one slot the weekend genuinely differs on: the afternoon film,
        # which is what the weekend afternoon was already for.
        "afternoon": "eighties_weekend_movie",
        "evening":   eighties.WEEKEND_EVENING,
        "prime":     eighties.PRIME_TIME_BLOCKS,
        "late":      eighties.SKETCH_HOUR_BLOCK,
    }
}


# ==============================================================================
# 3. ERSATZTV INTEGRATION
# ==============================================================================

def build_playout(api, context, build_id):
    """Build the daily playout schedule."""
    config = ScheduleConfig(
        schedules=SCHEDULES,
        timeslot_preset=EIGHTIES_TIMESLOTS,
        logger=ChannelLogger(prefix="[80s TV]"),
        # Still the fallback, but no longer the programming: the grid now covers
        # all twenty-four hours, so this is reached on a stall rather than for
        # eleven hours a day.
        fallback_content="eighties_music_videos",
        # `enable_filler=True` with no `filler_content` is an inert flag: the
        # "fill" strategy falls through to a bare wait when the filler will not
        # resolve, so the intent gets recorded and the effect is dead air. Music
        # videos are the right filler and are finally usable -- three to five
        # minutes each, so they fit the tails a film leaves, and filling the
        # seams with videos is what the channel is imitating.
        filler_content="eighties_music_videos",
        enable_commercials=True,
        enable_filler=True
    )
    return run_daily_schedule(api, context, build_id, config)

# Other required functions (can be left as-is)
def define_content(api, context, build_id): pass
def reset_playout(api, context, build_id):
    return api.wait_until(build_id, ControlWaitUntil(when="00:00", tomorrow=False, rewind_on_reset=True))
