"""
Corncob TV -- comedy after the laugh track
==========================================

**Identity.** Single-camera, cable, streaming, sketch and alt. The line against
Good Times is the **studio audience**, not the year: Freaks and Geeks (1999),
The Larry Sanders Show (1992) and Mr. Show (1995) are single-camera with no
laugh track and belong here, while Frasier (1993) and Will & Grace (1998) are
multi-camera and stay there. Between them the two channels hold the whole
comedy shelf and neither is defined by what the other is not (F4).

**Axis (F3): the clock gets stranger.** Nightmare Theatre gets darker as the
night goes on; this is the same shape in a different register. Era is not the
axis here and does not need to be -- tone is.

    02-06  The Vault           the alt back catalogue
    06-08  Sign-On             the gentlest half-hours on the channel
    08-10  The Morning Bench   three network pools, a month at a time
    10-12  The Syndication Hour   the channel's own register, in daylight
    12-14  The Noon Hour       one show, one day
    14-17  The Workplace       the office comedies
    17-20  The Cable Hour      four cable pools, a month at a time
    20-23  the named night
    23-24  The Late Shift      sketch, and the Limited Series on Sunday
    00-02  The Deep End        the far end of the channel

**The named nights.** Seven comedy traditions, one a night. None is an
`annual_show`, so none can hit the G5 replay trap that took the old Must See
Thursday off Good Times -- these are plain ordered Blocks of content keys, which
advance an episode rather than pinning one.

    MON  The Gang               It's Always Sunny · Workaholics · Trailer Park Boys
    TUE  Single Camera          Malcolm · Scrubs · Arrested Development · My Name Is Earl
    WED  The Cringe             Curb · Nathan For You · The Rehearsal · Jury Duty
    THU  Must See Thursday      The Office · Parks and Rec · 30 Rock · Community
    FRI  Corncob After Dark     Tim and Eric · Detroiters · I Think You Should Leave
                                · The Chair Company
    SAT  Saturday Night Sketch  Mr. Show · The State · Key & Peele · Chappelle's Show
                                · Strangers with Candy
    SUN  HBO Sunday             Larry Sanders · Veep · Silicon Valley
                                · Flight of the Conchords · Eastbound & Down

Friday is the Tim Robinson lineage read as a night: Tim and Eric, then
Detroiters, I Think You Should Leave and The Chair Company. It is also the
channel's own name -- Corncob TV is a Tim and Eric segment.

**The Limited Series (Sunday, 23:00).** One short show a season, chronological,
roughly two episodes a Sunday. This is G6 used deliberately: the shelf is full
of 16-to-22-episode shows that cannot strip and are too serialized for a
tune-in slot, and a season of Sundays is exactly the right size for them.
Twenty episodes is about ten weeks of a thirteen-week season, so each one runs
out shortly before its season does and repeats its tail. Registered
`Chronological` (G8) because a limited series shuffled is not a limited series.

--------------------------------------------------------------------------
THE HOURS RULES
--------------------------------------------------------------------------

Only one channel overlaps this one, and only on two titles.

**Cartoon Network's Adult Swim** airs The Eric Andre Show and Check It Out!
with Dr. Steve Brule inside `AS_ORIGINALS_B`, which runs:

    20:00-23:00  Tuesday and Thursday   (prime, the WEEKDAY_B arm)
    23:00-24:00  Sunday                 (night)
    00:00-02:00  Monday                 (after_hours -- Sunday night's tail)

channel-coverage.md prescribes the C2 rung-1 split for exactly these shows:
Adult Swim runs them as **first-run** -- chronological, appointment, late --
and Corncob runs them as **syndication**, shuffled and in daylight. That is what
The Syndication Hour at 10:00-12:00 is. Adult Swim is never on air at that hour
on any day, so the split holds by the clock and not by anyone remembering it.

Everything else here is claimed by no other channel. The British comedies belong
to Across the Pond, the horror-comedies (What We Do in the Shadows, Santa
Clarita Diet, Ash vs Evil Dead, Garth Marenghi's Darkplace) to Nightmare
Theatre, and Monk, Psych, Bored to Death and Elsbeth to Mystery Theatre; none of
them is scheduled here.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.logic.factories import monthly_rotation

# ==============================================================================
# 1. THE OVERNIGHT AND THE SMALL HOURS
# ==============================================================================

# 00:00-02:00. The far end of the channel -- the newest and strangest of it,
# and the only slot where a six-episode show is an asset rather than a problem.
THE_DEEP_END = RandomCollection([
    "itysl_tv",
    "chair_company_tv",
    "the_studio_tv",
    "north_of_north_tv",
    "bad_thoughts_tv",
    "history_world_2_tv",
])

# 02:00-06:00. The back catalogue, and where the two long unscripted-adjacent
# shelves earn their keep: The Red Green Show is 301 episodes and Penn & Teller
# 89, which is most of a month of small hours between them.
THE_VAULT = RandomCollection([
    "mr_show_tv",
    "the_state_tv",
    "strangers_with_candy_tv",
    "insomniac_tv",
    "red_green_tv",
    "penn_teller_tv",
])

# ==============================================================================
# 2. SIGN-ON AND THE MORNING BENCH
# ==============================================================================

# 06:00-08:00. The gentlest half-hours the channel has. Red Green sits here
# rather than in a comedy strip because at six in the morning a Canadian man
# duct-taping a boat to a car is the correct programme.
SIGN_ON = RandomCollection([
    "schitts_creek_tv",
    "north_of_north_tv",
    "red_green_tv",
    "jim_gaffigan_tv",
])

# 08:00-10:00. Three pools on a monthly rotation, the bench pattern Nick uses
# for its cartoons. Nothing here is drawn by The Workplace at 14:00 (G4): these
# are the home-and-school single-cameras, that is the office ones.
NETWORK_SINGLE_CAM = Block(
    name="Single Camera",
    items=RandomCollection([
        "malcolm_tv",
        "my_name_is_earl_tv",
        "arrested_development_tv",
        "freaks_and_geeks_tv",
    ]),
)

THE_NEW_CLASS = Block(
    name="The New Class",
    items=RandomCollection([
        "abbott_elementary_tv",
        "good_place_tv",
        "kimmy_schmidt_tv",
        "schitts_creek_tv",
    ]),
)

# The shelf of shows that were cancelled early and are beloved anyway. Four of
# the five are under 40 episodes, which is why they ride a bench rather than
# hold a strip (G6).
THE_CULT_SHELF = Block(
    name="The Cult Shelf",
    items=RandomCollection([
        "community_tv",
        "ghosted_tv",
        "other_space_tv",
        "people_of_earth_tv",
        "future_man_tv",
    ]),
)

MORNING_BENCH = monthly_rotation([
    NETWORK_SINGLE_CAM,
    THE_NEW_CLASS,
    THE_CULT_SHELF,
])

# ==============================================================================
# 3. THE SYNDICATION HOUR (10:00-12:00)
# ==============================================================================
#
# The channel's own register, in daylight and shuffled. Two of these five are
# Cartoon Network's at night; see the hours rules in the module docstring. Adult
# Swim is not on air anywhere near 10:00-12:00, which is what makes the split
# hold by the clock rather than by convention (C3).

SYNDICATION_HOUR = Block(
    name="The Syndication Hour",
    items=RandomCollection([
        "tim_and_eric_tv",
        "eric_andre_tv",
        "steve_brule_tv",
        "food_party_tv",
        "the_guild_tv",
    ]),
    use_epg_group=False,
)

# ==============================================================================
# 4. THE NOON HOUR (12:00-14:00)
# ==============================================================================
#
# One show per day, no collection (G3), so the hour reads as "Scrubs is on at
# noon". Thursday deliberately takes Arrested Development rather than one of
# its own prime four -- G7, keep the marquee off the bench in front of it.

NOON_HOUR = {
    "MONDAY":    "scrubs_tv",
    "TUESDAY":   "malcolm_tv",
    "WEDNESDAY": "my_name_is_earl_tv",
    "THURSDAY":  "arrested_development_tv",
    "FRIDAY":    "community_tv",
    "SATURDAY":  "the_office_tv",
    "SUNDAY":    "parks_and_recreation_tv",
}

# ==============================================================================
# 5. THE WORKPLACE (14:00-17:00)
# ==============================================================================

THE_WORKPLACE = RandomCollection([
    "the_office_tv",
    "parks_and_recreation_tv",
    "30_rock_tv",
    "scrubs_tv",
    "superstore_tv",
    "better_off_ted_tv",
    "mythic_quest_tv",
])

# Thursday's afternoon drops the four that own Thursday night (G7). Without
# this, Must See Thursday's own shows run for three hours immediately before
# it and the 20:00 block stops meaning anything.
THE_WORKPLACE_THURSDAY = RandomCollection([
    "scrubs_tv",
    "superstore_tv",
    "better_off_ted_tv",
    "mythic_quest_tv",
    "jim_gaffigan_tv",
])

WORKPLACE_BLOCK = {
    "THURSDAY": THE_WORKPLACE_THURSDAY,
    "default": THE_WORKPLACE,
}

# ==============================================================================
# 6. THE CABLE HOUR (17:00-20:00)
# ==============================================================================
#
# Four pools, a month at a time, offset from the morning bench so the two are
# never showing the same shelf. Each pool is a different cable house style.

CABLE_BASIC = Block(
    name="The Cable Hour",
    items=RandomCollection([
        "always_sunny_tv",
        "workaholics_tv",
        "reno_911_tv",
        "portlandia_tv",
    ]),
)

CABLE_PREMIUM = Block(
    name="The Cable Hour",
    items=RandomCollection([
        "veep_tv",
        "silicon_valley_tv",
        "curb_tv",
        "larry_sanders_tv",
    ]),
)

CABLE_PRESTIGE = Block(
    name="The Cable Hour",
    items=RandomCollection([
        "atlanta_tv",
        "baskets_tv",
        "mr_inbetween_tv",
        "reservation_dogs_tv",
    ]),
)

CABLE_ODDITIES = Block(
    name="The Cable Hour",
    items=RandomCollection([
        "wilfred_tv",
        "man_seeking_woman_tv",
        "trailer_park_boys_tv",
        "detroiters_tv",
    ]),
)

CABLE_HOUR = monthly_rotation(
    [CABLE_BASIC, CABLE_PREMIUM, CABLE_PRESTIGE, CABLE_ODDITIES],
    start_month=2,
)

# ==============================================================================
# 7. THE NAMED NIGHTS (20:00-23:00)
# ==============================================================================
#
# Plain ordered Blocks of content keys, not `annual_show` appointments. That is
# the whole fix for the defect these four shows carried on Good Times: an
# `annual_show` Program pins a season and episode, so a collection that wraps
# inside the slot replays it, while a content key advances. Four items in a
# three-hour slot wrap twice here and simply play the next episode.

MON_PRIME = Block(
    name="The Gang",
    items=OrderedCollection([
        "always_sunny_tv",
        "workaholics_tv",
        "trailer_park_boys_tv",
    ]),
    use_epg_group=False,
)

TUE_PRIME = Block(
    name="Single Camera",
    items=OrderedCollection([
        "malcolm_tv",
        "scrubs_tv",
        "arrested_development_tv",
        "my_name_is_earl_tv",
    ]),
    use_epg_group=False,
)

# The discomfort tradition, in order of how much of it there is.
WED_PRIME = Block(
    name="The Cringe",
    items=OrderedCollection([
        "curb_tv",
        "nathan_for_you_tv",
        "the_rehearsal_tv",
        "jury_duty_tv",
    ]),
    use_epg_group=False,
)

# The night this channel was built to inherit. Four shows, 887 episodes, and no
# appointment machinery -- see the note above the blocks.
THU_PRIME = Block(
    name="Must See Thursday",
    items=OrderedCollection([
        "the_office_tv",
        "parks_and_recreation_tv",
        "30_rock_tv",
        "community_tv",
    ]),
    use_epg_group=False,
)

# The Tim Robinson lineage, in order: Tim and Eric, then the three shows that
# came out of it. Corncob TV is itself a Tim and Eric segment, so this is the
# channel's own night.
FRI_PRIME = Block(
    name="Corncob After Dark",
    items=OrderedCollection([
        "tim_and_eric_tv",
        "detroiters_tv",
        "itysl_tv",
        "chair_company_tv",
    ]),
    use_epg_group=False,
)

SAT_PRIME = Block(
    name="Saturday Night Sketch",
    items=OrderedCollection([
        "mr_show_tv",
        "the_state_tv",
        "key_and_peele_tv",
        "chappelles_show_tv",
        "strangers_with_candy_tv",
    ]),
    use_epg_group=False,
)

# HBO Sunday, which is a real thing and ran in this order for twenty years.
SUN_PRIME = Block(
    name="HBO Sunday",
    items=OrderedCollection([
        "larry_sanders_tv",
        "veep_tv",
        "silicon_valley_tv",
        "conchords_tv",
        "eastbound_tv",
    ]),
    use_epg_group=False,
)

# ==============================================================================
# 8. THE LATE SHIFT (23:00-24:00)
# ==============================================================================
#
# One hour. Each night takes a show that is *not* in that night's prime, so the
# late shift reads as a second helping rather than a repeat -- Nathan For You
# owns Wednesday at eight and Friday at eleven.

LIMITED_SERIES = {
    "WINTER": "party_down_tv",
    "SPRING": "enlightened_tv",
    "SUMMER": "wet_hot_tv",
    "FALL":   "vice_principals_tv",
}

LATE_SHIFT = {
    "MONDAY":    "key_and_peele_tv",
    "TUESDAY":   "chappelles_show_tv",
    "WEDNESDAY": "insomniac_tv",
    "THURSDAY":  "john_wilson_tv",
    "FRIDAY":    "nathan_for_you_tv",
    "SATURDAY":  "tim_and_eric_tv",
    "SUNDAY":    LIMITED_SERIES,
}

# ==============================================================================
# 9. FALLBACK AND HOLIDAYS
# ==============================================================================

# Safe at every hour of every day: nothing here is shared with Cartoon Network,
# so a stall cannot land the channel on Adult Swim's two titles at Adult Swim's
# hours. A fallback does not know what time it is, so "safe at some hours" is
# not safe.
CHANNEL_FALLBACK = RandomCollection([
    "scrubs_tv",
    "the_office_tv",
    "parks_and_recreation_tv",
    "30_rock_tv",
    "community_tv",
    "malcolm_tv",
    "superstore_tv",
    "always_sunny_tv",
    "curb_tv",
    "reno_911_tv",
    "red_green_tv",
    "portlandia_tv",
])

# Episode-level keys, so the holiday is the channel's own shows doing Halloween
# rather than a cartoon block borrowed from somewhere else.
HALLOWEEN_EVENT = RandomCollection([
    "halloween_sitcoms_tv",
])

THANKSGIVING_EVENT = RandomCollection([
    "thanksgiving_sitcoms_tv",
])

CHRISTMAS_EVENT = RandomCollection([
    "christmas_modern_sitcoms_tv",
    "christmas_90s_sitcoms_tv",
])
