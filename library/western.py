"""
High Noon Content - Westerns

Two libraries, and they do not mix.

The spine is five black-and-white network westerns, 1955-1963, 946 episodes:
Bonanza (431, complete), Gunsmoke (233, the half-hour Dennis Weaver years),
The Rifleman (166, complete), Wanted: Dead or Alive (94, complete) and Rawhide
(22, season one only). All episodic, all standalone, all tune-in. That is the
channel for fifteen hours a day.

The other library is six serialized modern westerns -- Justified, Longmire,
Deadwood, Dark Winds, Yellowstone, Lawmen: Bass Reeves -- 234 episodes that
fail the tune-in test outright. They are appointments, not strip content: one
show a night, one season a year, `modern_western_movie` on the bed between
seasons. Nobody drops into Deadwood season two, so the channel does not ask
them to.

Episode counts here are counted off disk, not read from the manifests --
`reference/library-tv.tsv` counts `extras/` folders as episodes and overstates
Justified by 39 and Deadwood by 15.

Not in this library, despite carrying a Western genre tag: Breaking Bad,
Westworld and Cowboy Bebop. See the `western_tv` note in `sources.py`.
"""

from scripts.logic.structures import (
    RandomCollection, OrderedCollection, DailyOrderedCollection, Block
)
from scripts.library.queries import show_by_title, movie_by_title
from scripts.logic.factories import annual_show

# ==============================================================================
# THE STRIP -- the black-and-white network western
# ==============================================================================
#
# Split by running time rather than by title, because a two-hour daypart holds
# four half-hours or two hour-longs and mixing them strands a slot's tail.
#
# Half-hours: Gunsmoke (30), The Rifleman (25), Wanted: Dead or Alive (25).
# Hour-longs: Bonanza (50), Rawhide (50).

HALF_HOUR_WEST = Block(
    name="Half-Hour West",
    items=RandomCollection([
        {"title": "Gunsmoke"},
        {"title": "The Rifleman"},
        {"title": "Wanted: Dead or Alive"},
    ])
)

# Each of the three morning strips is one show, so the hour reads as that show
# rather than as a genre wheel. This is the whole difference between "westerns
# are on" and "The Rifleman is on at eight".
WANTED_DEAD_OR_ALIVE = Block(
    name="Wanted: Dead or Alive",
    items=OrderedCollection([
        {"title": "Wanted: Dead or Alive",
         "query": show_by_title("Wanted: Dead or Alive"),
         "order": "Shuffle"},
    ])
)

THE_RIFLEMAN = Block(
    name="The Rifleman",
    items=OrderedCollection([
        {"title": "The Rifleman",
         "query": show_by_title("The Rifleman"),
         "order": "Shuffle"},
    ])
)

DODGE_CITY = Block(
    name="Dodge City",
    items=OrderedCollection([
        {"title": "Gunsmoke",
         "query": show_by_title("Gunsmoke"),
         "order": "Shuffle"},
    ])
)

# Bonanza is 431 episodes -- 46% of the spine on its own, and the only western
# here with a complete run. It carries the afternoon by itself.
THE_PONDEROSA = Block(
    name="The Ponderosa",
    items=OrderedCollection([
        {"title": "Bonanza",
         "query": show_by_title("Bonanza"),
         "order": "Shuffle"},
    ])
)

# Rawhide is 22 episodes and cannot strip -- a nightly hour would exhaust it in
# three weeks. It rides behind Bonanza in the evening instead, where the wheel
# means it surfaces roughly every other night and stays a treat.
THE_TRAIL_DRIVE = Block(
    name="The Trail Drive",
    items=RandomCollection([
        {"title": "Bonanza"},
        {"title": "Rawhide"},
    ])
)

# Brisco County is 1993, a comedy-western, and the one episodic show on the
# channel that is not black and white. It gets Saturday evening rather than a
# slot in the strip, where the tonal jump would read as a mistake.
BRISCO_COUNTY = Block(
    name="The Adventures of Brisco County, Jr.",
    items=OrderedCollection([
        {"title": "The Adventures of Brisco County, Jr.",
         "query": show_by_title("The Adventures of Brisco County, Jr."),
         "order": "Chronological"},
    ])
)

# The 02:00-06:00 dead zone. Everything, shuffled, no structure -- this is the
# hour where the channel is a jukebox and the strip identities do not matter.
THE_LONG_RIDE = Block(
    name="The Long Ride",
    items=RandomCollection([
        "classic_western_tv",
        {"title": "Bonanza"},
        {"title": "Gunsmoke"},
    ])
)

# ==============================================================================
# THE FILM -- all 46, handed over by Cabes Classic Cinema
# ==============================================================================

# The name block. 12:00-14:00, seven days, and the reason the channel is called
# what it is. Pre-1980 only: The Searchers, Shane, Giant, The Magnificent Seven,
# the Leone trilogy, Butch Cassidy, Blazing Saddles, Jeremiah Johnson.
HIGH_NOON_FEATURE = RandomCollection(["classic_western_movie"])

# 22:00-24:00 and 00:00-02:00. The modern half of the shelf -- Unforgiven,
# Tombstone, The Hateful Eight, Bone Tomahawk, The Assassination of Jesse James
# -- which is where the 160-minute running times live and where they fit.
LATE_FEATURE = RandomCollection(["modern_western_movie"])

# Saturday and Sunday afternoons draw the whole shelf. It is the one place the
# two eras run against each other on purpose: a matinee double bill that can
# put 3:10 to Yuma 1957 next to 3:10 to Yuma 2007.
WEEKEND_MATINEE = RandomCollection(["western_movie"])

# ==============================================================================
# THE APPOINTMENTS -- six serialized shows, six nights, one season a year
# ==============================================================================
#
# `frequency` paces an appointment; it does not gate it. `_find_active_episode`
# returns the current episode for any date inside the season window, so a show
# with frequency=["MONDAY"] in a block that runs seven nights airs the same
# episode all seven. Every one of these survives because PRIME_BLOCK in the
# channel is a weekday dict -- the slot does the gating. See KNOWN_ISSUES.md.
#
# Season lengths are counted off disk. Premieres are staggered across the four
# seasons so the channel always has one or two first-run nights and never six.
#
# `modern_western_movie` is the bed under all of them: 29 films, and a prime
# that falls through to a western feature is still the channel.

JUSTIFIED = annual_show(
    show_title="Justified",
    episodes_per_season=[13, 13, 13, 13, 13, 13],
    premiere_year=2026,
    premiere_season=("FALL", "MONDAY"),
    frequency=["MONDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

LONGMIRE = annual_show(
    show_title="Longmire",
    episodes_per_season=[10, 15, 10, 10, 10, 10],
    premiere_year=2026,
    premiere_season=("SUMMER", "TUESDAY"),
    frequency=["TUESDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

DEADWOOD = annual_show(
    show_title="Deadwood",
    episodes_per_season=[12, 12, 12],
    premiere_year=2026,
    premiere_season=("WINTER", "WEDNESDAY"),
    frequency=["WEDNESDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

DARK_WINDS = annual_show(
    show_title="Dark Winds",
    episodes_per_season=[6, 6, 8, 8],
    premiere_year=2026,
    premiere_season=("SPRING", "THURSDAY"),
    frequency=["THURSDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

# Two seasons on disk of five aired. The appointment is honest about what is
# there rather than declaring windows for episodes that would resolve to
# nothing and stall the block.
YELLOWSTONE = annual_show(
    show_title="Yellowstone",
    episodes_per_season=[9, 10],
    premiere_year=2026,
    premiere_season=("FALL", "FRIDAY"),
    frequency=["FRIDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

LAWMEN_BASS_REEVES = annual_show(
    show_title="Lawmen: Bass Reeves",
    episodes_per_season=[8],
    premiere_year=2026,
    premiere_season=("WINTER", "SUNDAY"),
    frequency=["SUNDAY"],
    reruns="modern_western_movie",
    episodes_per_slot=2,
    loop=True
)

# One appointment per night, wrapped so the slot has a name in the guide either
# way. DailyOrderedCollection rather than OrderedCollection: it resets to index
# 0 each day, so the appointment is always first in its two hours and premieres
# land at 20:00 every week. A date-anchored ordering walks the premiere around
# the block, which is the one thing an appointment cannot do.
def _appointment(name, program):
    return Block(
        name=name,
        items=DailyOrderedCollection([program, "modern_western_movie"]),
        fill_strategy="yield"
    )

MONDAY_NIGHT    = _appointment("Justified", JUSTIFIED)
TUESDAY_NIGHT   = _appointment("Longmire", LONGMIRE)
WEDNESDAY_NIGHT = _appointment("Deadwood", DEADWOOD)
THURSDAY_NIGHT  = _appointment("Dark Winds", DARK_WINDS)
FRIDAY_NIGHT    = _appointment("Yellowstone", YELLOWSTONE)
SUNDAY_NIGHT    = _appointment("Lawmen: Bass Reeves", LAWMEN_BASS_REEVES)

# Saturday has no appointment. It is the film night -- 20:00-24:00 straight
# through, which is where a 168-minute Hateful Eight can actually play.
SATURDAY_NIGHT_FEATURE = RandomCollection(["western_movie"])

# ==============================================================================
# EVENTS
# ==============================================================================

# Chronological on purpose: the Dollars films are a trilogy and the joke of the
# third one only lands after the first two. ~6.5 hours, so 18:00-24:00 fits it
# with the tail running into the late feature's slot.
DOLLARS_TRILOGY = OrderedCollection([
    {"title": "A Fistful of Dollars",
     "query": movie_by_title("Fistful of Dollars, A"), "order": "Chronological"},
    {"title": "For a Few Dollars More",
     "query": movie_by_title("For a Few Dollars More"), "order": "Chronological"},
    {"title": "The Good, the Bad and the Ugly",
     "query": movie_by_title("Good, the Bad and the Ugly, The"), "order": "Chronological"},
])

# The Fourth and Memorial Day both get the pre-1980 shelf rather than the whole
# one -- Django Unchained and The Hateful Eight are not holiday programming.
PATRIOTIC_WESTERNS = RandomCollection(["classic_western_movie"])
