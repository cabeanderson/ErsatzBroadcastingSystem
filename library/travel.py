"""
Travelers Table -- the day of meals
===================================

**Identity (F2).** *Somewhere else, and something to eat.* A day of meals, and
the world the food comes from. The channel is not "food shows shuffled": it is
a kitchen that opens at six, serves lunch, bakes through the afternoon, and
hands the evening to the road.

**Axis (F3): the clock, as a day of eating.** The morning is instruction, the
midday is the professional kitchen, the afternoon is the bake, and from five
the channel leaves the building. Nothing here is organised by genre or by
decade, because a food channel that runs Bourdain at nine in the morning has no
idea what it is.

    00-06  The Overnight        the day again -- announced, not smuggled
    06-09  Breakfast            Good Eats
    09-12  The Morning Kitchen  Japanese Food Noodles
    12-14  The Lunch Counter    On the Line, and Iron Chef behind it
    14-17  The Afternoon Bake   The Great British Bake Off
    17-19  Prep                 No Reservations
    19-21  Dinner Service       a different guest every night
    21-23  Night Service        Parts Unknown
    23-24  Last Call            Cosmos, three nights a week
    SAT 19-24  Out There        natural history, and only on Saturday

**TV-led, with no film shelf at all (F5).** 545 hours of television against a
documentary film shelf of seventeen titles -- Free Solo, Meru, the Qatsi
trilogy, My Octopus Teacher, The Silent World. Those seventeen were counted and
left off: fourteen of them sit inside Be Kind Rewind's 1980+ range and three
inside Cabes Classic Cinema's, both of which run film most of the day, so
taking them would have added seventeen titles of C1 exposure to a lineup that
already has a same-title backlog. A channel with 545 hours of television does
not need them. They are in acquisitions.md as a
deliberate omission rather than an oversight.

**Every count here was taken off disk, not from the manifest (V4)**, and three
of them moved a decision:

* **Good Eats is 195 episodes, not 305.** Seasons 12-14 are empty directories
  and 54 files are under `extras/`. 195 at a 20-minute median is 65 hours,
  which carries exactly the three hours before nine and nothing else.
* **Alone is 13 episodes, not 25.** Season 01 is an empty directory. That is
  the difference between a strip and a Monday night.
* Bake Off is 102 at a 58-minute median -- 98.6 hours, and the reason the
  evening works at all. See below.

--------------------------------------------------------------------------
THE ARITHMETIC, WHICH IS THIS CHANNEL'S REAL CONSTRAINT
--------------------------------------------------------------------------

F6 wants nothing cycling faster than about three weeks. **Travelers Table is
the thinnest channel on the lineup and does not clear that by much.** The whole
shelf is 545 hours; 24 hours a day for 21 days is 504. There is no clever grid
that fixes a number that close to the floor -- only content does.

Two structural decisions came out of it, and both are honest rather than
clever:

**The first is that 00:00-06:00 is a rebroadcast, and says so.** Six hours of
the day replayed. The first-run day is 06:00-24:00, eighteen hours, and that is
the number F6 is measured against here. This is what a food channel actually
does, and it is the same shape as Japanorama's `THE_REBROADCAST`.

**The second is that Bake Off had to come in.** Without it, the two Bourdains
were carrying 86 of 168 hours a week -- a 13-day cycle on the channel's
marquee, which is the failure F6 exists to catch. Bake Off's 98.6 hours took
Prep and Night Service down to 21 days and gave the afternoon a block of its
own. It is shared with Across the Pond under an hours rule, below.

The budget as built, at 168 hours a week:

    Good Eats           195 eps   65 h   21.0 h/wk   21.7 d
    Japanese Food N.    236 eps  106 h   39.9 h/wk   18.6 d   [youtube/]
    On the Line          80 eps   24 h    7.0 h/wk   24.0 d   [youtube/]
    Bake Off            102 eps   99 h   32.3 h/wk   21.4 d   [shared]
    No Reservations     134 eps   96 h   31.5 h/wk   21.4 d
    Parts Unknown        95 eps   67 h   24.1 h/wk   19.3 d
    Alone                13 eps    9 h    2.0 h/wk   31.1 d
    James May / Conan    10 eps    8 h    2.0 h/wk   26.6 d
    Cosmos               13 eps   13 h    3.0 h/wk   30.3 d
    BBC natural history  59 eps   51 h    4.6 h/wk   77.3 d   [shared]
    Crocodile Hunter      6 eps    4 h    0.4 h/wk   77.3 d
    Iron Chef            10 eps    4 h    0.3 h/wk  110.2 d

Two sit under 21 days and both are deliberate. Japanese Food Noodles at 18.6 is
236 *different noodle shops*, which is not the kind of repeat F6 is about.
Parts Unknown at 19.3 is inside the rounding on a 21-day target.

The four pools at the bottom are under-used on purpose: Iron Chef, Crocodile
Hunter and the natural history are all too short to strip, and the nature shelf
is capped at one night a week by choice, not by arithmetic -- it would carry
18 hours a week and it is given five.

--------------------------------------------------------------------------
THE HOURS RULES -- two channels, two shared keys
--------------------------------------------------------------------------

**Across the Pond holds both shared titles**, and the rule against it is
written at the resolution that channel's grid actually has (C2 rung 2), not as
one blanket window:

* **Bake Off is its Breakfast, 06:00-09:00, on all seven day-arms.** Travelers
  Table's 06:00-09:00 is Good Eats on every day-arm, so `bake_off_tv` is
  unreachable in that window -- it appears in one block, and that block is
  14:00-17:00.
* **The natural history is its Sunday prime, 20:00-23:00**, one night a week.
  Travelers Table's nature block is **Saturday**, which is the whole reason it
  is Saturday: Sunday at eight on BBC One belongs to the other channel, so this
  one moves a day rather than negotiating an hour.

Both are enforced by the grid's shape rather than by the grid remembering (C3).
There is no day-arm on this channel from which either key can resolve inside
Across the Pond's window, and the bed cannot reach them either --
`travelers_table_vault_tv` is Bourdain and Good Eats, all three owned outright,
which is the trap Japanorama's overnight fell into.

**Nothing was taken from Across the Pond.** Its grid is unchanged and its
`british.py` keys are untouched; both shared titles still run there exactly as
they did.

--------------------------------------------------------------------------
WHAT LEFT THE CHANNEL
--------------------------------------------------------------------------

The unscripted Travelers Table was airing six shows. Three of them belong
elsewhere and scripting it is where that gets settled:

* **Laid-Back Camp** and **both Midnight Diners** are Japanorama's -- the first
  is its 06:00-08:00 Morning Cast, the second its Deep Night, and Midnight
  Diner is the only live-action series on that channel and deliberately so.
  Eviction (C2 rung 4): the claim there is unambiguous.
* **Bake Off** stays, but as Across the Pond's title under an hours rule rather
  than as this channel's own.

Considered and left off: **Old Enough!** (20 episodes, 14-minute median) is
Japanese, charming, and neither food, travel nor nature -- it would have been
here on vibe. **How It's Made** (416 episodes) is unclaimed and is Makers
Corner's register, not this one. **Great British Menu**, **Rick Steves**,
**Julia Child** and **The Galloping Gourmet** are not on disk; they are what
would take this channel off the F6 floor, and they are already the top of
acquisitions.md.
"""

from scripts.logic.structures import Block, RandomCollection, WeightedCollection

# ==============================================================================
# 1. BREAKFAST -- 06:00-09:00
# ==============================================================================

# One show, so the hour reads as *Good Eats is on at seven* rather than
# *cooking is on* (G3). It is also the only half-hour show on the channel: at a
# 20-minute median it puts nine episodes into three hours, where every other
# pool here is 40 to 60 minutes and would strand the tail of the slot (G2).
#
# Good Eats appears in exactly one block. 65 hours of shelf carries 21 a week
# and no more, so it is held out of The Overnight as well -- the only pool that
# is. Adding it to the rebroadcast took it from 21.7 days to 15.3.
BREAKFAST = Block(
    name="Breakfast",
    items=RandomCollection(["good_eats_tv"]),
)

# ==============================================================================
# 2. THE MORNING KITCHEN -- 09:00-12:00
# ==============================================================================

# The largest pool on the channel and its most distinctive three hours: 236
# episodes of one man walking into Japanese noodle bars, ramen stalls and bento
# kitchens. One show per strip again (G3).
#
# This block reads from `youtube/`, which became an ErsatzTV library on
# 2026-09-07. It is the largest single pool on the channel and the whole of
# these three hours.
THE_MORNING_KITCHEN = Block(
    name="The Morning Kitchen",
    items=RandomCollection(["japanese_food_noodles_tv"]),
)

# ==============================================================================
# 3. THE LUNCH COUNTER -- 12:00-14:00
# ==============================================================================

# The professional kitchen at lunchtime: a day on the line at a Michelin
# restaurant, and Iron Chef behind it.
#
# Weighted rather than even, because the pools are 24 hours and 4. An even
# wheel would give Iron Chef an hour a week and cycle its ten episodes in a
# fortnight; at these weights it surfaces roughly once every three days and
# stays a treat -- the Rawhide arithmetic (G6), applied to a two-item block.
# On the Line also reads from `youtube/`; the manifests cover that tree as of
# 2026-09-07, and it resolves as `Bon Appetit: On the Line` -- the `tvshow.nfo`
# title rather than the bare `showtitle` the episodes carry, which is why the
# key names both.
THE_LUNCH_COUNTER = Block(
    name="The Lunch Counter",
    items=WeightedCollection([
        ("bon_appetit_on_the_line_tv", 0.85),
        ("iron_chef_tv", 0.15),
    ]),
)

# ==============================================================================
# 4. THE AFTERNOON BAKE -- 14:00-17:00
# ==============================================================================

# Shared with Across the Pond, which runs it as British breakfast television at
# 06:00-09:00. Here it is the afternoon bake, and the two never touch: this
# channel's 06:00-09:00 is Good Eats on every day-arm.
#
# The block that made the evening work. Without these 98.6 hours the two
# Bourdains were carrying 86 of the channel's 168 hours a week and cycling in
# thirteen days.
THE_AFTERNOON_BAKE = Block(
    name="The Afternoon Bake",
    items=RandomCollection(["bake_off_tv"]),
)

# ==============================================================================
# 5. PREP -- 17:00-19:00
# ==============================================================================

# The channel leaves the building at five. No Reservations is the earlier,
# scrappier show and it takes the earlier slot; Parts Unknown gets 21:00.
#
# Two blocks are only two blocks if they draw different keys (G4), which is why
# Prep and Night Service are one Bourdain each rather than a shared pool played
# twice. Only Dinner Service reaches for both, and only on the four nights that
# have no named guest.
PREP = Block(
    name="Prep",
    items=RandomCollection(["bourdain_no_reservations_tv"]),
)

# ==============================================================================
# 6. DINNER SERVICE -- 19:00-21:00
# ==============================================================================

# A different guest every night. The shelf supports exactly two named nights
# and it would be a lie to draw five: Alone (13), James May (6) and Conan (4)
# are the only runs on the channel too short to strip, and G6 says a run like
# that becomes an appointment rather than a rounding error.
#
# The day gate is the weekday arm of the slot, not a `frequency` argument --
# `frequency` paces an episode index and does not stop a block airing on other
# days (G5). Saturday never reaches this dict; it has its own schedule arm.

# Monday. Thirteen episodes, in order, looping. Two hours a week is a 4.5-week
# season, which is what a survival series should feel like.
ALONE_NIGHT = Block(
    name="Alone",
    items=RandomCollection(["alone_tv"]),
)

# Tuesday. Six episodes and four episodes; neither could hold a night by
# itself, and together they are ten and a 3.8-week cycle. Both are one
# presenter abroad being funny about it, which is why they share a night rather
# than sharing the Bourdain wheel.
THE_ROAD = Block(
    name="The Road",
    items=RandomCollection([
        "james_may_tv",
        "conan_must_go_tv",
    ]),
)

# Wednesday, Thursday, Friday and Sunday. The marquee, and the only block on
# the channel that draws both Bourdains.
DINNER_SERVICE = Block(
    name="Dinner Service",
    items=RandomCollection([
        "bourdain_no_reservations_tv",
        "bourdain_parts_unknown_tv",
    ]),
)

# ==============================================================================
# 7. NIGHT SERVICE -- 21:00-23:00
# ==============================================================================

# Parts Unknown alone, and it is the later, quieter, more political of the two
# shows -- the right one for nine o'clock (G3, G4).
NIGHT_SERVICE = Block(
    name="Night Service",
    items=RandomCollection(["bourdain_parts_unknown_tv"]),
)

# ==============================================================================
# 8. LAST CALL -- 23:00-24:00
# ==============================================================================

# Thirteen hour-long episodes of Cosmos, in order, three nights a week. Nightly
# would cycle them in twelve days; Monday, Wednesday and Friday makes it thirty
# (F6). The other three nights hand the last hour back to the road.
#
# Cosmos is the channel's own -- PBS 1980, not the 2014 remake, and Across the
# Pond's natural-history block does not carry it -- so unlike everything in
# Out There it is reachable on any night of the week.
LAST_CALL_COSMOS = Block(
    name="Last Call",
    items=RandomCollection(["cosmos_tv"]),
)

LAST_CALL_ROAD = Block(
    name="Last Call",
    items=RandomCollection([
        "bourdain_no_reservations_tv",
        "bourdain_parts_unknown_tv",
    ]),
)

# ==============================================================================
# 9. OUT THERE -- Saturday 19:00-24:00
# ==============================================================================

# Where the food comes from. Five hours, one night a week, and Saturday rather
# than Sunday for one reason: Sunday at eight on BBC One is Across the Pond's,
# and the cheapest way to keep C1 is to move a day rather than negotiate an
# hour.
#
# The seven BBC titles and the Crocodile Hunter's six episodes ride one wheel.
# Six episodes could not hold anything on their own and would burn out in a
# fortnight anywhere else; behind 59 they surface every few weeks and stay a
# treat, which is what High Noon does with Rawhide (G6).
#
# 55 hours against five a week is a 15-week cycle -- far slower than F6 asks
# for, and deliberately so. The nature shelf would carry 18 hours a week; it is
# an accent on this channel, not a daypart.
OUT_THERE = Block(
    name="Out There",
    items=WeightedCollection([
        ("bbc_natural_history_tv", 0.9),
        ("crocodile_hunter_tv", 0.1),
    ]),
)

# ==============================================================================
# 10. THE OVERNIGHT -- 00:00-06:00
# ==============================================================================

# The day again, and it says so in its name. Six hours across two slots -- 00-02
# and 02-06, split at midnight so neither wraps it (G1) -- both pointing at this
# one block, which means the no-repeat state carries across the boundary rather
# than restarting at two.
#
# It draws four of the five day pools and not the fifth: Good Eats is budgeted
# to the hour at Breakfast and adding it here took it from a 21.7-day cycle to
# 15.3. Weighted by shelf size so the six hours come off the pools that can
# afford them -- Bake Off and the two Bourdains are 98, 96 and 67 hours, and
# they carry the night.
#
# Nothing shared is in it that this channel cannot reach at 02:00 anyway: Across
# the Pond runs Bake Off at 06:00 and its natural history at 20:00, and the
# natural history is not here at all.
THE_OVERNIGHT = Block(
    name="The Overnight",
    items=WeightedCollection([
        ("bake_off_tv", 0.27),
        ("bourdain_no_reservations_tv", 0.26),
        ("japanese_food_noodles_tv", 0.29),
        ("bourdain_parts_unknown_tv", 0.18),
    ]),
)
