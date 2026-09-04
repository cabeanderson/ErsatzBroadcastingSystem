"""
Japanorama (164) -- the Japanese broadcast day

Anime as a whole schedule rather than an after-school block. Cartoon Network
already runs the best three hours of it on this lineup, and Toonami is a
*block*: it has no morning, no feature, and no small hours. This channel signs
on at six and reaches 深夜アニメ by 23:00.

Axis: **the clock, as a broadcast day.** The morning is gentle, the day is
syndication, the evening is the feature, and after 23:00 the channel becomes
the half of the medium American television never imported.

The roster, the block budgets and the one hours rule that matters -- Cartoon
Network's Toonami holds the entire shonen canon, about 2,450 episodes -- are in
the docstring of `scripts/library/anime.py`.

Built 2026-09-03. The channel had been on the lineup since the beginning with
no configuration and no stated identity, listed in channel-plan.md as
"164 | Japanorama | anime | no".
"""

from etv_client.models import ControlWaitUntil

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.logic import triggers, Marathon
from scripts.library import anime

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Ten slots, none wrapping midnight (G1). `late` is 23-24 and `deep_night` is
# 00-02, each with its own block: a wrapping slot is entered twice under two
# different day labels, so a collection spanning the boundary replays its first
# items on the far side.
#
# The boundaries are Cartoon Network's, deliberately. The hours rule against
# Toonami is only readable if the two grids agree on where the hours are --
# "Toonami is dark 06:00-17:00" should be a fact you can hold both files up
# against, not a claim that needs a simulation to believe. Same reason Corncob
# TV took Cartoon Network's map when its one rule was against Adult Swim.

JAPANORAMA_TIMESLOTS = {
    "deep_night": (0, 2),     # Deep Night, the film half
    "overnight":  (2, 6),     # The Rebroadcast
    "morning":    (6, 8),     # Morning Cast
    "kids":       (8, 12),    # The Kids' Hours
    "midday":     (12, 15),   # The Syndication Hour
    "afternoon":  (15, 17),   # The Dragon Ball Hour
    "teatime":    (17, 19),   # Teatime
    "feature":    (19, 21),   # Japanorama Theatre
    "prime":      (21, 23),   # the named night
    "late":       (23, 24),   # Deep Night begins
}

# ==============================================================================
# 2. MARATHONS
# ==============================================================================

MARATHONS = [
    # 29 April to 3 May. Golden Week really ends on the 5th, but 4 May is Star
    # Wars Day in `core/registry.py` and `find_active_marathon` returns nothing
    # while a holiday season is live -- a marathon spanning the 4th would go
    # dark in the middle of itself (G9).
    Marathon(
        name="Golden Week",
        trigger=triggers.in_range(4, 29, 5, 3),
        collection=anime.GOLDEN_WEEK,
        hours=(12, 24),
        priority=2,
    ),
    # Obon, 13-16 August. Grave of the Fireflies is what Japan actually screens
    # in this week.
    Marathon(
        name="Obon",
        trigger=triggers.in_range(8, 13, 8, 16),
        collection=anime.OBON,
        hours=(19, 24),
        priority=2,
    ),
]

# ==============================================================================
# 3. THE NAMED NIGHTS
# ==============================================================================
#
# One strip a night, day-gated by the weekday arm rather than by an
# appointment's `frequency` -- which paces an episode index and does not stop a
# show airing on other days (G5). Saturday and Sunday have their own schedule
# arms below and never reach this dict.

PRIME_BLOCK = {
    "MONDAY":    anime.FRIEREN_NIGHT,
    "TUESDAY":   anime.VINLAND_NIGHT,
    "WEDNESDAY": anime.MUSIC_NIGHT,
    "THURSDAY":  anime.QUIET_NIGHT,
    "FRIDAY":    anime.SHONEN_NIGHT,
    "default":   anime.SUNDAY_REPLAY,
}

# ==============================================================================
# 4. SCHEDULE
# ==============================================================================
#
# The clock means the same thing every day here, so the weekend arms change
# three slots and no more: Saturday takes the canon at the feature and the
# limited series in prime, Sunday gives the whole evening to Ghibli.

SCHEDULES = {
    "WEEKDAY": {
        "deep_night": anime.DEEP_NIGHT_LATE,
        "overnight":  anime.THE_REBROADCAST,
        "morning":    anime.MORNING_CAST,
        "kids":       anime.THE_KIDS_HOURS,
        "midday":     anime.THE_SYNDICATION_HOUR,
        "afternoon":  anime.THE_DRAGON_BALL_HOUR,
        "teatime":    anime.TEATIME,
        "feature":    anime.JAPANORAMA_THEATRE,
        "prime":      PRIME_BLOCK,
        "late":       anime.DEEP_NIGHT,
    },
    "SATURDAY": {
        "deep_night": anime.DEEP_NIGHT_LATE,
        "overnight":  anime.THE_REBROADCAST,
        "morning":    anime.MORNING_CAST,
        "kids":       anime.THE_KIDS_HOURS,
        "midday":     anime.THE_SYNDICATION_HOUR,
        "afternoon":  anime.THE_DRAGON_BALL_HOUR,
        "teatime":    anime.TEATIME,
        "feature":    anime.SATURDAY_THEATRE,
        "prime":      anime.SATURDAY_LIMITED_SERIES,
        "late":       anime.DEEP_NIGHT,
    },
    "SUNDAY": {
        "deep_night": anime.DEEP_NIGHT_LATE,
        "overnight":  anime.THE_REBROADCAST,
        "morning":    anime.MORNING_CAST,
        "kids":       anime.THE_KIDS_HOURS,
        "midday":     anime.THE_SYNDICATION_HOUR,
        "afternoon":  anime.THE_DRAGON_BALL_HOUR,
        "teatime":    anime.TEATIME,
        "feature":    anime.GHIBLI_SUNDAY,
        "prime":      anime.SUNDAY_REPLAY,
        "late":       anime.DEEP_NIGHT,
    },
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
        holiday_schedules={"NEW_YEARS_EVE": anime.OMISOKA_SCHEDULE},
        timeslot_preset=JAPANORAMA_TIMESLOTS,
        logger=ChannelLogger(prefix="[JAPANORAMA]"),
        # The 24 three-minute shorts -- Room Camp and Encouragement of Climb's
        # first season. Cartoon Network ships with no daytime filler because its
        # bumper trees are empty and silence beats the wrong branding (G12);
        # this channel has real programming the right length for the hole.
        filler_content="japanorama_shorts_tv",
        # Owned content only. A stall can fire in any slot, so a bed built from
        # the syndication keys would be the one thing on the channel able to
        # reach Toonami's window.
        fallback_content="japanorama_vault_tv",
        enable_marathons=True,
        enable_holiday_injection=True,
        enable_seasonal_injection=True
    )
    return run_daily_schedule(api, context, build_id, config)
