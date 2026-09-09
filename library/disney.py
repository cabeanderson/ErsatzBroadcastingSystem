"""
Disney Content
==============
Three eras of one studio, kept in their own hours: the 1990 syndication block
in the afternoon, the ABC morning cartoons at breakfast, and the modern Disney
Channel shows after school. Star Wars animation is the fourth thing, and it is
big enough to be its own strip rather than a guest in someone else's.

Unlike Nick, the bench here is not a rescue operation -- 902 episodes across
four pools is real depth. `monthly_rotation()` is used for the same reason
anyway: three strips cycling four pools a month at a time, offset so no two
strips show the same pool on the same day, is what stops a 24-hour channel
from feeling like a six-show playlist.

The pools are deliberately *not* the on-air blocks. THE_DISNEY_AFTERNOON
reassembles the 1990 lineup in broadcast order for its own two hours; the
bench splits the same shows into Duckburg and adventure halves, so the
afternoon marquee still means something when those shows turn up at 03:00.
Noon is the one daytime strip held off the bench entirely, so that the three
hours leading into the marquee are never the marquee's own shows.

Serialization rule: Gravity Falls, The Owl House, Amphibia and the three Star
Wars strips are the only serialized shows on the channel. They get the
chronological-weekday / shuffle-weekend split, which is first-run and reruns
out of one library, and they stay off the bench -- a serialized show dropped
into a random rotation is the thing the channel plan says not to do.

Sharing rule: none left. Gravity Falls and The Owl House came back from
Cartoon Network's CARTOON_NETWORK_CLASSICS when this channel was built, and the
CN restructure returned the rest -- DISNEY_MORNING, DISNEY_AFTERNOON, Gargoyles
and the Star Wars Day marathon. `star_wars_animation_tv` is also Other Worlds'
06:00 block, which is nowhere near this channel's Star Wars hours.
See reference/channel-plan.md.
"""

from scripts.logic.structures import (
    RandomCollection, OrderedCollection, DailyOrderedCollection, Block
)
from scripts.logic.factories import annual_show, monthly_rotation

# ==============================================================================
# 1. THE MARQUEE BLOCKS
# ==============================================================================

# 15:00-17:00. The 1990 syndication package in the order it actually ran, which
# is the one block on the channel that is an appointment rather than a pool.
THE_DISNEY_AFTERNOON = Block(
    name="The Disney Afternoon",
    items=OrderedCollection([
        {"title": "TaleSpin"},
        {"title": "Chip 'n' Dale Rescue Rangers"},
        {"title": "DuckTales"},
        {"title": "Darkwing Duck"},
        {"title": "Goof Troop"},
        {"title": "Gargoyles"},
    ]),
    use_epg_group=False
)

# 06:00-08:00. The ABC morning cartoons -- the studio's other syndication era,
# and the half of the library that is not Duckburg.
DISNEY_MORNING = Block(
    name="Disney Morning",
    items=OrderedCollection([
        {"title": "Aladdin"},
        # "Hercules" alone also matches Hercules: The Legendary Journeys, which
        # is live action and Other Worlds'. The key carries the genre filter.
        "hercules_animated_tv",
        {"title": "Pepper Ann"},
        {"title": "Mighty Ducks: The Animated Series"},
        {"title": "Buzz Lightyear of Star Command"},
    ]),
    use_epg_group=False
)

# ==============================================================================
# 2. THE MONTHLY BENCH
# ==============================================================================

# Duckburg and the shows that orbit it.
DUCKBURG = Block(
    name="Duckburg",
    items=RandomCollection([
        {"title": "DuckTales"},
        {"title": "Darkwing Duck"},
        {"title": "Chip 'n' Dale Rescue Rangers"},
    ])
)

# The other half of the Disney Afternoon: bigger world, longer episodes, and
# Gargoyles pulling the tone up a few years.
DISNEY_ADVENTURE = Block(
    name="Disney Adventure",
    items=RandomCollection([
        {"title": "TaleSpin"},
        {"title": "Gargoyles"},
        {"title": "Goof Troop"},
    ])
)

# The ABC morning shows, unordered -- the same five as DISNEY_MORNING minus the
# two that carry the action pool.
ONE_SATURDAY_MORNING = Block(
    name="One Saturday Morning",
    items=RandomCollection([
        {"title": "Aladdin"},
        "hercules_animated_tv",
        {"title": "Pepper Ann"},
    ])
)

# Episodic, action-shaped, and the only pool with a show from after 2000.
DISNEY_ACTION = Block(
    name="Disney Action",
    items=RandomCollection([
        {"title": "Kim Possible"},
        {"title": "Buzz Lightyear of Star Command"},
        {"title": "Mighty Ducks: The Animated Series"},
    ])
)

# Four pools cycling a month at a time across three strips, each starting the
# cycle a month apart: on any given day the overnight, morning and midday
# strips are showing three different pools, the fourth rests, and at the turn
# of the month they all move on one.
DAYTIME_POOLS = [
    DUCKBURG,
    ONE_SATURDAY_MORNING,
    DISNEY_ADVENTURE,
    DISNEY_ACTION,
]

MIDDAY_BENCH = monthly_rotation(DAYTIME_POOLS)
OVERNIGHT_BENCH = monthly_rotation(DAYTIME_POOLS, start_month=2)
MORNING_BENCH = monthly_rotation(DAYTIME_POOLS, start_month=3)

# 12:00-15:00 is the one strip that cannot be on the bench. DUCKBURG and
# DISNEY_ADVENTURE are the two halves of THE_DISNEY_AFTERNOON, so a bench turn
# here would put the marquee's own six shows in the three hours leading up to
# it -- four hours of the same rotation, and the 15:00 appointment stops
# meaning anything. Noon gets everything that is *not* the Disney Afternoon
# instead, which is the rest of the channel.
DISNEY_TOONS = Block(
    name="Disney Toons",
    items=RandomCollection([
        {"title": "Aladdin"},
        "hercules_animated_tv",
        {"title": "Pepper Ann"},
        {"title": "Kim Possible"},
        {"title": "Buzz Lightyear of Star Command"},
        {"title": "Mighty Ducks: The Animated Series"},
    ])
)

# ==============================================================================
# 3. THE DISNEY CHANNEL STRIP (17:00 - 19:00)
# ==============================================================================

# The three modern serialized shows. New episodes weekdays, reruns at the
# weekend -- and the shuffle half runs again after midnight, so the same two
# keys cover both the rerun windows without a third registration.
DISNEY_CHANNEL_FIRST_RUN = Block(
    name="The Disney Channel",
    items=OrderedCollection([
        "gravity_falls_chronological_tv",
        "owl_house_chronological_tv",
        "amphibia_chronological_tv",
    ]),
    use_epg_group=False
)

DISNEY_CHANNEL_RERUNS = Block(
    name="The Disney Channel",
    items=OrderedCollection([
        "gravity_falls_shuffle_tv",
        "owl_house_shuffle_tv",
        "amphibia_shuffle_tv",
    ]),
    use_epg_group=False
)

DISNEY_CHANNEL_STRIP = {
    "WEEKDAY": DISNEY_CHANNEL_FIRST_RUN,
    "default": DISNEY_CHANNEL_RERUNS,
}

# 00:00-02:00. The darkest end of the library, which is the modern shows plus
# Gargoyles, at the hour that suits them.
DISNEY_AFTER_DARK = Block(
    name="Disney After Dark",
    items=OrderedCollection([
        {"title": "Gargoyles"},
        "owl_house_shuffle_tv",
        "amphibia_shuffle_tv",
    ])
)

# ==============================================================================
# 4. STAR WARS (19:00 - 21:00, and the vault at 21:00 - 24:00)
# ==============================================================================

# 277 episodes across seven shows is too much to fold into anyone else's block
# and too serialized to shuffle, so it strips chronologically Monday to Friday.
#
# **It used to be a weekday/weekend pair and the weekend half never aired** --
# found by `testing/unaired_check.py` 2026-09-09. `STAR_WARS_STRIP` was
# `{"WEEKDAY": first-run, "default": reruns}`, but the only thing that reaches
# it is `PRIME_BLOCK`'s own `default`, and Saturday and Sunday are routed away
# from that to STAR_WARS_EVENT_NIGHT and WONDERFUL_WORLD_OF_DISNEY before it
# is ever consulted. Mon-Fri always carries the WEEKDAY label, so the reruns
# branch was unreachable on every day of the week.
#
# Nothing is lost by dropping it. The shuffled weekend it was meant to provide
# is what STAR_WARS_VAULT already does at 21:00-24:00 every day, and
# `star_wars_animation_tv` contains all three of the shows the reruns block
# named. Removing it changes no airing -- verified by diffing two years of
# this channel, 0 of 44,163 entries.
STAR_WARS_STRIP = Block(
    name="Star Wars",
    items=OrderedCollection([
        "clone_wars_chronological_tv",
        "rebels_chronological_tv",
        "bad_batch_chronological_tv",
    ]),
    use_epg_group=False
)

# 21:00-24:00. Everything with Star Wars on the front, shuffled -- the vault
# the strip draws down from, and where the four Saturday events go back to
# once their run is over.
STAR_WARS_VAULT = Block(
    name="The Star Wars Vault",
    items=RandomCollection([
        "star_wars_animation_tv",
    ])
)

# --- The Saturday events ---------------------------------------------------
#
# Four short series, 6/6/6/10 episodes, one per season of the year. None can
# strip -- six episodes shuffled into a rotation is a rounding error -- so each
# becomes an appointment instead: one episode a week, six or ten Saturdays,
# then back in the vault until next year. Between them they give 28 Saturdays
# a year a first-run Star Wars premiere and the vault covers the other 24.
#
# `premiere_season` is passed as a bare season string, not the ("SEASON","DAY")
# tuple used elsewhere in the library. The tuple form does not resolve to a
# date and silently yields no season windows -- see KNOWN_ISSUES.md.

TALES_OF_THE_JEDI = annual_show(
    show_title="Star Wars Tales of the Jedi",
    episodes_per_season=[6],
    premiere_year=2026,
    premiere_season="SPRING",
    frequency=["SATURDAY"],
    reruns="star_wars_animation_tv",
    loop=True
)

TALES_OF_THE_EMPIRE = annual_show(
    show_title="Star Wars Tales of the Empire",
    episodes_per_season=[6],
    premiere_year=2026,
    premiere_season="SUMMER",
    frequency=["SATURDAY"],
    reruns="star_wars_animation_tv",
    loop=True
)

TALES_OF_THE_UNDERWORLD = annual_show(
    show_title="Star Wars Tales of the Underworld",
    episodes_per_season=[6],
    premiere_year=2026,
    premiere_season="FALL",
    frequency=["SATURDAY"],
    reruns="star_wars_animation_tv",
    loop=True
)

MAUL_SHADOW_LORD = annual_show(
    show_title="Star Wars Maul - Shadow Lord",
    episodes_per_season=[10],
    premiere_year=2026,
    premiere_season="WINTER",
    frequency=["SATURDAY"],
    reruns="star_wars_animation_tv",
    loop=True
)

# DailyOrderedCollection, not OrderedCollection: it resets to index 0 each day,
# so each of the four holds the same position in the block every week and its
# premiere lands at the same time each Saturday. A date-anchored ordering
# walks the premiere around the two hours week to week, which is the one
# thing an appointment cannot do. Whichever is in season plays its episode;
# the other three are on their rerun bed, so the block reads as one Saturday
# night either way.
STAR_WARS_EVENT_NIGHT = Block(
    name="Star Wars: Tales",
    items=DailyOrderedCollection([
        TALES_OF_THE_JEDI,
        TALES_OF_THE_EMPIRE,
        TALES_OF_THE_UNDERWORLD,
        MAUL_SHADOW_LORD,
    ]),
    use_epg_group=False
)

# May 4th. The marathon collection, kept separate from the vault block so the
# marathon engine gets items rather than a Block.
STAR_WARS_MARATHON = RandomCollection([
    "clone_wars_chronological_tv",
    "rebels_chronological_tv",
    "bad_batch_chronological_tv",
])

# ==============================================================================
# 5. THE SUNDAY NIGHT MOVIE
# ==============================================================================

# 19:00-21:00 on Sunday, in place of the Star Wars strip. Two hours is one
# feature and the tail of another, which is what the slot is for.
WONDERFUL_WORLD_OF_DISNEY = Block(
    name="The Wonderful World of Disney",
    items=RandomCollection([
        "disney_movie",
        "pixar_movie",
    ]),
    use_epg_group=False
)

# ==============================================================================
# 6. HOLIDAY COLLECTIONS
# ==============================================================================

# Cartoon Network's HALLOWEEN_TEEN_FRIGHTS is Courage and Infinity Train, which
# are its own shows. Disney's teen-hours Halloween is built from Disney's.
DISNEY_HALLOWEEN = RandomCollection([
    "gravity_falls_shuffle_tv",
    "owl_house_shuffle_tv",
    "halloween_animated_tv",
])
