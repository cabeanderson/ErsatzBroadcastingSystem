"""
Makers Corner (241) -- the workshop day

*Somebody is building something, and you can see how.* A working day in a shop:
opened by a painter at six, handed to hand tools, then machines, then a
factory, then a house, and given at seven to the two people who blow things up.

Axis: **the clock, sized by the thing being made.** The day starts on a canvas
and ends on a workbench, and in between it climbs -- a dovetail at eight, a
cabinet at ten, a production line at noon, a whole house at three.

The roster, the counts (all taken off disk, and one of them wrong in the
manifest by 130 episodes), the F6 budget and the reason this channel has no
hours rule against anybody are in the docstring of `scripts/library/makers.py`.

Built 2026-09-07. The channel had been on the lineup with a name, content and
no designed grid, listed in channel-plan.md as
"241 | Makers Corner | DIY & craft | no".

**One block reads from `youtube/`**, a separate tree from `tv/`, and it is the
channel's only real F6 constraint: two maker shows, 79 videos, 16.7 hours
between them. That buys one hour a night, five nights a week, and the block is
weekday-only for exactly that reason.

**This is the only channel on the lineup with zero C1 exposure.** All eight
shows were unclaimed when it was built, so there is no hours rule, no era
split, no eviction and no shared bed. The one title it might have taken --
The Red Green Show -- was deliberately left with Corncob TV.
"""

from etv_client.models import ControlWaitUntil

from scripts.scheduling import run_daily_schedule, ScheduleConfig
from scripts.core.logger import ChannelLogger
from scripts.library import makers

# ==============================================================================
# 1. TIMESLOTS
# ==============================================================================
#
# Eleven slots, none wrapping midnight (G1). `late` is 23-24 and `after_hours`
# is 00-02, sitting on the far side of the boundary as its own slot, so the
# three-hour Lights Out is two slots rather than one wrapping block.
#
# Slot names are the standard ones wherever the hours allow, because
# `HOLIDAY_PROFILES` is keyed by slot name and an unrecognised name falls back
# to a bare `BlockProfile()` -- full holiday ramp, no bias. Only `after_hours`
# and `late` are custom, and both are short slots at the ends of the night
# where that is harmless. (It is harmless twice over here: holiday injection is
# off channel-wide, measured against the tags the episodes actually carry.)
#
# The slot *lengths* are not decoration. Every strip is two hours because every
# show but one has a 21-to-29-minute median; prime is three because MythBusters
# is 43.6 and four of those fit three hours where they would strand forty
# minutes in two (G2).

MAKERS_TIMESLOTS = {
    "after_hours": (0, 2),     # Lights Out, second half
    "overnight":   (2, 6),     # The Long Bench
    "early":       (6, 8),     # Sign-On           -- The Joy of Painting
    "morning":     (8, 10),    # The Hand Tool     -- The Woodwright's Shop
    "midday":      (10, 12),   # The Shop          -- The New Yankee Workshop
    "noon":        (12, 15),   # The Factory Floor -- How It's Made
    "afternoon":   (15, 17),   # The House         -- This Old House
    "evening":     (17, 19),   # The House, cont.
    "prime":       (19, 22),   # The Experiment    -- MythBusters
    "night":       (22, 23),   # The Small Shop    -- `youtube/`, Mon-Fri
    "late":        (23, 24),   # Lights Out, first half
}

# ==============================================================================
# 2. THE SMALL SHOP -- the one hour with a day gate
# ==============================================================================
#
# 22:00-23:00 belongs to the two `youtube/` shows Monday to Friday and to Bob
# Ross at the weekend. The gate is this dict -- a weekday arm of the slot --
# and not an appointment's `frequency`, which paces an episode index and does
# not stop a block airing on other days (G5). Nothing is stacked: one block
# resolves per night, so there is no `DailyOrderedCollection` to wrap and
# replay.
#
# It is five nights rather than seven because 16.7 hours of shelf is 5.6 hours
# a week at F6's floor. Seven would put both shows under three weeks.

NIGHT_HOUR = {
    "WEEKDAY": makers.THE_SMALL_SHOP,
    "default": makers.LIGHTS_OUT,   # SAT SUN -- the night starts an hour early
}

# ==============================================================================
# 3. SCHEDULE
# ==============================================================================
#
# The clock means the same thing six days a week and the one weekday variant
# lives in the dict above. Saturday is the real arm: 08:00-15:00 becomes the
# PBS Saturday-morning block and How It's Made moves to the afternoon.
#
# Sunday deliberately has no arm of its own. The shelf has eight shows and
# eleven slots and there is no seventh idea in it; inventing a Sunday would
# mean giving some pool hours it cannot afford, which is the arithmetic F6
# exists to stop.

WEEKDAY = {
    "after_hours": makers.LIGHTS_OUT,
    "overnight":   makers.THE_LONG_BENCH,
    "early":       makers.SIGN_ON,
    "morning":     makers.THE_HAND_TOOL,
    "midday":      makers.THE_SHOP,
    "noon":        makers.THE_FACTORY_FLOOR,
    "afternoon":   makers.THE_HOUSE,
    "evening":     makers.THE_HOUSE,
    "prime":       makers.THE_EXPERIMENT,
    "night":       NIGHT_HOUR,
    "late":        makers.LIGHTS_OUT,
}

SCHEDULES = {
    "WEEKDAY": WEEKDAY,

    # Saturday morning is when the block actually aired and when the audience
    # has a day to build something. Seven hours of the three PBS workshop
    # shows on one wheel -- the only place on this channel where a strip gives
    # way to variety, and the only argument good enough to break G3.
    #
    # It replaces those hours rather than adding to them: How It's Made trades
    # its noon for 15:00-19:00, so no show gains a second daypart and the whole
    # F6 table above still holds (G4).
    "SATURDAY": {
        **WEEKDAY,
        "morning":   makers.THE_WEEKEND_PROJECT,
        "midday":    makers.THE_WEEKEND_PROJECT,
        "noon":      makers.THE_WEEKEND_PROJECT,
        "afternoon": makers.THE_FACTORY_FLOOR,
        "evening":   makers.THE_FACTORY_FLOOR,
    },
}

# ==============================================================================
# 4. ERSATZTV INTEGRATION
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
        timeslot_preset=MAKERS_TIMESLOTS,
        logger=ChannelLogger(prefix="[MAKERS]"),
        # No filler. `filler/bumpers/` holds exactly one tree and it is
        # `cartoon network`; there is no PBS, workshop or maker branding on
        # disk, and putting Adult Swim bumps around Bob Ross is the mistake
        # G12 was written for. Ships silent, and the shortfall is on the
        # acquisitions list.
        filler_content=None,
        # The four half-hour workshop shows: what the channel is, in one key.
        # It excludes MythBusters, because a marquee that turns up when
        # something failed is not a marquee, and Joy of Painting, whose hours
        # are budgeted to the two blocks that bookend the night. Every title in
        # it is owned outright, so unlike Japanorama's overnight this bed
        # cannot reach another channel's hours (C3) -- and on this channel
        # there is no other channel's hours to reach.
        fallback_content="makers_corner_vault_tv",
        # No marathons. `find_active_marathon` returns nothing while a holiday
        # season is live (G9) and every date-anchored idea this channel has
        # lands inside one, but the real reason is simpler: marathons here
        # address film series by title and this channel has no film.
        enable_marathons=False,
        # Both injections off, and measured rather than assumed. Tag injection
        # rewrites a key as `(base) AND (tag:winter OR ...)`, so it is only
        # useful if the episodes carry the tags -- and they do not: **337 of
        # 2,164 episode NFOs on this channel carry any `<tag>` at all**, and
        # two-thirds of those are `season premiere` or `season finale`. The
        # word `christmas` appears three times in the whole 951-hour shelf.
        #
        # It costs more here than on most channels because six of the ten
        # blocks hold a single show (G3): where a wheel can yield an injected
        # pick to the next item, The Hand Tool and The Shop have no next item
        # and would fall to the bed. G12's principle applied to a feature
        # rather than to filler -- if the assets are not there, ship without
        # it.
        enable_holiday_injection=False,
        enable_seasonal_injection=False
    )
    return run_daily_schedule(api, context, build_id, config)
