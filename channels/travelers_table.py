"""
Travelers Table (240) -- the day of meals

*Somewhere else, and something to eat.* A kitchen that opens at six, serves
lunch, bakes through the afternoon, and hands the evening to the road.

Axis: **the clock, as a day of eating.** Not a genre and not a decade -- the
morning is instruction, the midday is the professional kitchen, the afternoon
is the bake, and from five the channel leaves the building. Saturday night it
goes outside altogether.

The roster, the counts (all taken off disk, and three of them wrong in the
manifest), the F6 budget and the two hours rules against Across the Pond are in
the docstring of `scripts/library/travel.py`.

Built 2026-09-07. The channel had been on the lineup with content, a name and
no designed grid, listed in channel-plan.md as
"240 | Travelers Table | cooking -- + nature docs | no".

**Two blocks read from `youtube/`**, a separate tree from `tv/`. It was not an
ErsatzTV library when this channel was designed and it is now (2026-09-07), so
09:00-12:00 and the Lunch Counter are live rather than falling to the bed. The
offline tooling was taught the tree at the same time -- see `SHOW_ROOTS` in
`scripts/testing/library_census.py`.
"""

from etv_client.models import ControlWaitUntil

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import travel

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Ten slots, none wrapping midnight (G1). `night` is 21-23 and `late` is 23-24;
# `after_hours` is 00-02 and sits on the far side of the boundary as its own
# slot, so the six-hour Overnight is two slots rather than one wrapping block.
#
# Slot names are the standard ones wherever the hours allow, because
# `HOLIDAY_PROFILES` is keyed by slot name and an unrecognised name falls back
# to a bare `BlockProfile()` -- full holiday ramp, no bias. Only `after_hours`
# and `late` are custom, and both are short slots at the ends of the night
# where that is harmless. This is the shape Across the Pond carries, and
# deliberately so: the two channels share two titles, and an hours rule is only
# readable if both grids agree on where the hours are.

TABLE_TIMESLOTS = {
    "after_hours": (0, 2),     # The Overnight, first half
    "overnight":   (2, 6),     # The Overnight, second half
    "early":       (6, 9),     # Breakfast            -- Good Eats
    "morning":     (9, 12),    # The Morning Kitchen  -- Japanese Food Noodles
    "noon":        (12, 14),   # The Lunch Counter    -- On the Line, Iron Chef
    "afternoon":   (14, 17),   # The Afternoon Bake   -- Bake Off
    "evening":     (17, 19),   # Prep                 -- No Reservations
    "prime":       (19, 21),   # Dinner Service       -- the named night
    "night":       (21, 23),   # Night Service        -- Parts Unknown
    "late":        (23, 24),   # Last Call            -- Cosmos, three nights
}

# ==============================================================================
# 2. THE NAMED NIGHTS
# ==============================================================================
#
# Two of them, because two is what the shelf holds: Alone (13 episodes), James
# May (6) and Conan (4) are the only runs on the channel too short to strip.
# Drawing five named nights out of this library would mean burning one of them
# in a fortnight (G6).
#
# The gate is this dict -- a weekday arm of the slot -- and not an appointment's
# `frequency`, which paces an episode index and does not stop a block airing on
# other days (G5). Nothing is stacked here: one block resolves per night, so
# there is no `DailyOrderedCollection` to wrap and replay.
#
# Saturday never reaches this dict. It has its own schedule arm below, where
# 19:00-24:00 is one block.

DINNER_SERVICE = {
    "MONDAY":  travel.ALONE_NIGHT,
    "TUESDAY": travel.THE_ROAD,
    "default": travel.DINNER_SERVICE,   # WED THU FRI SUN -- the marquee
}

# ==============================================================================
# 3. LAST CALL
# ==============================================================================
#
# Cosmos on Monday, Wednesday and Friday; the road on the other three. Thirteen
# hour-long episodes cannot carry a nightly hour -- that is a twelve-day cycle
# -- and three nights makes it thirty (F6). Saturday does not reach this either.

LAST_CALL = {
    "MONDAY":    travel.LAST_CALL_COSMOS,
    "WEDNESDAY": travel.LAST_CALL_COSMOS,
    "FRIDAY":    travel.LAST_CALL_COSMOS,
    "default":   travel.LAST_CALL_ROAD,
}

# ==============================================================================
# 4. SCHEDULE
# ==============================================================================
#
# The clock means the same thing six days a week, so there are two arms and the
# weekday differences live inside the two dicts above. Saturday is the one real
# variant: 19:00 to midnight goes outside.

WEEKDAY = {
    "after_hours": travel.THE_OVERNIGHT,
    "overnight":   travel.THE_OVERNIGHT,
    "early":       travel.BREAKFAST,
    "morning":     travel.THE_MORNING_KITCHEN,
    "noon":        travel.THE_LUNCH_COUNTER,
    "afternoon":   travel.THE_AFTERNOON_BAKE,
    "evening":     travel.PREP,
    "prime":       DINNER_SERVICE,
    "night":       travel.NIGHT_SERVICE,
    "late":        LAST_CALL,
}

SCHEDULES = {
    "WEEKDAY": WEEKDAY,

    # Saturday night is the nature night, and it is Saturday rather than Sunday
    # because Sunday at eight on BBC One is Across the Pond's natural-history
    # prime. Moving a day is cheaper than negotiating an hour (C2), and it puts
    # the whole 19:00-24:00 stretch under one block instead of three.
    "SATURDAY": {
        **WEEKDAY,
        "prime": travel.OUT_THERE,
        "night": travel.OUT_THERE,
        "late":  travel.OUT_THERE,
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
        timeslot_preset=TABLE_TIMESLOTS,
        logger=ChannelLogger(prefix="[TABLE]"),
        # No filler. `filler/bumpers/` holds exactly two trees and both are
        # Cartoon Network's; there is no food or travel branding on disk and
        # borrowing someone else's would put their identity on this channel,
        # which is the mistake G12 was written for. Ships silent, and the
        # shortfall is on the acquisitions list.
        filler_content=None,
        # Owned content only. A stall can fire in any slot, including 06:00 and
        # Sunday at eight, so a bed built from `bake_off_tv` or
        # `bbc_natural_history_tv` would be the one thing on this channel able
        # to reach Across the Pond's hours (C3). It is also what holds up
        # 09:00-14:00 until `youtube/` is indexed.
        fallback_content="travelers_table_vault_tv",
        # No marathons. Every date-anchored idea this channel had -- a
        # Thanksgiving cook, a Christmas bake -- wants content it does not own,
        # and `find_active_marathon` returns nothing while a holiday season is
        # live anyway (G9), which is exactly when a food channel would want one.
        enable_marathons=False,
        # Both injections off, and measured rather than assumed. Tag injection
        # rewrites a key as `(base) AND (tag:winter OR ...)`, so it is only
        # useful if the episodes carry the tags -- and they do not: **34 of
        # Good Eats' 251 episode NFOs carry any `<tag>` at all**, 21 of 141 for
        # No Reservations, 14 of 102 for Bake Off, and none of them are
        # seasonal. An injected key would resolve to nothing.
        #
        # That costs more here than on most channels because six of the ten
        # blocks hold a single show (G3): where Japanorama's injected pick can
        # yield to the next item on the wheel, Breakfast and The Morning
        # Kitchen have no next item and lean on the bed instead. G12's
        # principle, applied to a feature rather than to filler -- if the
        # assets are not there, ship without it.
        enable_holiday_injection=False,
        enable_seasonal_injection=False
    )
    return run_daily_schedule(api, context, build_id, config)
