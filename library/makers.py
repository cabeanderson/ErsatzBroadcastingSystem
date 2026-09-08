"""
Makers Corner -- the workshop day
=================================

**Identity (F2).** *Somebody is building something, and you can see how.* Not
"DIY shows shuffled": a working day in a shop, opened by a painter at six,
handed to hand tools, then machines, then a factory, then a house, and given
at seven to the two people who blow things up.

**Axis (F3): the clock, sized by the thing being made.** The day starts on a
canvas and ends on a workbench, and in between it climbs -- a dovetail at
eight, a cabinet at ten, a production line at noon, a whole house at three.
Nothing here is organised by decade or by network, because a maker channel
that runs a factory tour at six in the morning has no idea what it is.

    00-02  Lights Out         The Joy of Painting
    02-06  The Long Bench     the four workshop shows, weighted
    06-08  Sign-On            The Joy of Painting
    08-10  The Hand Tool      The Woodwright's Shop
    10-12  The Shop           The New Yankee Workshop
    12-15  The Factory Floor  How It's Made
    15-19  The House          This Old House
    19-22  The Experiment     MythBusters
    22-23  The Small Shop     Pedulla Studio and Timothy Wilmots  (Mon-Fri)
    23-24  Lights Out         The Joy of Painting
    SAT 08-15  The Weekend Project   the PBS Saturday morning block, reassembled
    SAT 15-19  The Factory Floor     How It's Made takes the afternoon instead

**Television-led, with no film shelf at all (F5).** Eight shows, 2,084
episodes, **951 hours**, and the film library has nothing to add: there is no
DIY or craft shelf in `library-movies.tsv` to draw on, so this is a television
channel with no film keys, in the way High Noon is a television channel with a
film shelf and Nightmare Theatre is the inverse.

**Nothing here is shared with another channel.** All eight shows were unclaimed
at build time -- checked against every `library/*.py` and every channel module.
That makes Makers Corner the only channel on the lineup with **zero C1
exposure**: no hours rule, no era split, no eviction, and a bed that cannot
reach anyone else's shelf. The nearest thing to a claim is *The Red Green Show*
(301 episodes), which is a DIY-parody sitcom and is Corncob TV's -- its
02:00-06:00 vault and its 06:00-08:00 sign-on. It was considered and left
alone; see WHAT WAS LEFT OFF.

**Every count here was taken off disk, not from the manifest (V4)**, and one
of them moved a decision -- see New Yankee Workshop below.

--------------------------------------------------------------------------
THE SHELF, MEASURED
--------------------------------------------------------------------------

Episode counts are video files outside `extras/`; medians are
`<durationinseconds>` out of the episode NFOs.

    The Woodwright's Shop   1984  479 eps  26.8m  218.3 h  PBS
    MythBusters             2003  272 eps  43.6m  210.5 h  Science Channel
    The Joy of Painting     1983  403 eps  27.2m  180.6 h  PBS
    How It's Made           2001  416 eps  21.5m  148.4 h  Science Channel
    This Old House          1979  234 eps  28.7m  112.3 h  PBS
    The New Yankee Workshop 1989  151 eps  25.1m   63.9 h  PBS
    Pedulla Studio                 28 eps  19.6m   10.6 h  [youtube/]
    Timothy Wilmots                51 eps   6.8m    6.1 h  [youtube/]
                                 -----            -------
                                2,084             950.7 h

**951 hours is 39.6 days at 24 hours a day, against F6's 21-day floor.** That
is worth saying plainly because it is the opposite of the channel built the
day before: Travelers Table has 545 hours and sits on the floor, which is why
six of its twenty-four hours are an announced rebroadcast. Makers Corner needs
no rebroadcast. Every hour of this grid is first-run and the whole channel is
running at about 53% of what F6 would permit.

**The New Yankee Workshop is 151 episodes, not 281.** Ten of its twenty-one
seasons -- 1-4, 10, 12-14, 18-19 -- are `.divx` files. They are AVI containers
(`ffprobe` says `format_name=avi`) with an extension that is in nobody's
allowlist: not `library_census.VIDEO_EXTENSIONS`, and, on the evidence that the
manifest and the folder agree at exactly 151, not ErsatzTV's either. **130
episodes and 49.8 hours of the show's entire early run are invisible to the
whole stack.** The budget below is written against the 151 that index. The fix
is a rename and it is on acquisitions.md; until
it happens, Norm Abram is the smallest shelf on the channel and sets its
ceiling.

--------------------------------------------------------------------------
THE ARITHMETIC (F6)
--------------------------------------------------------------------------

At 168 hours a week, and with the Saturday arm counted:

    Joy of Painting        180.6 h   37.0 h/wk   34.2 d
    Woodwright's Shop      218.3 h   26.4 h/wk   58.0 d
    New Yankee Workshop     63.9 h   17.6 h/wk   25.4 d
    How It's Made          148.4 h   31.8 h/wk   32.7 d
    This Old House         112.3 h   29.3 h/wk   26.9 d
    MythBusters            210.5 h   21.0 h/wk   70.2 d
    Pedulla Studio          10.6 h    3.2 h/wk   23.3 d
    Timothy Wilmots          6.1 h    1.8 h/wk   23.3 d
                                    ---------
                                     168.0 h/wk

**All eight clear 21 days**, and the two tightest are the two YouTube shows at
23.3 -- which is the point of the ratio in THE_SMALL_SHOP and the reason that
block is weekdays only. MythBusters at 70 days is deliberately slack: 272
episodes surfacing once a fortnight each is what keeps prime feeling like the
marquee, and it is the show with the most headroom if the grid ever needs it.

**The real constraint on this channel is not the television, it is the 16.7
hours of `youtube/`.** Two shows, 79 videos. At F6's floor that shelf supports
5.6 hours a week and no more, which buys exactly one hour a night, five nights.
Everything else on the channel has slack; this has none, and it is the top of
the acquisitions list.

--------------------------------------------------------------------------
WHAT WAS LEFT OFF
--------------------------------------------------------------------------

* **The Red Green Show** (301 episodes) is the obvious eighth-and-a-half show
  and it stays where it is. It is a scripted sketch sitcom wearing a DIY show's
  clothes, Corncob TV built two blocks on it in the 2026-09-01 rebuild, and
  Handyman Corner is a joke about this channel rather than an episode of it.
  Taking it would have converted a channel with **zero** C1 exposure into one
  with an hours rule, to gain hours it does not need. Left alone (C2: the
  cheapest fix is the one you do not have to make).
* **Top Gear, The Grand Tour and Clarkson's Farm** are Across the Pond's, and
  a shed full of men welding a caravan to a Reliant Robin is a motoring show,
  not a maker show. Not asked for.
* **Penn & Teller: Bull!** was filed against this channel in
  channel-coverage.md and went to Corncob TV on
  2026-09-01 instead. Correct: it is an argument show, not a workshop.
* **No film shelf.** Checked and there is none to have -- the film library has
  no DIY, craft or process titles, so unlike every other television-led channel
  on the lineup this one has nothing to put on a weekend afternoon. That is a
  gap in the collection, not in the grid.

--------------------------------------------------------------------------
NO FILLER, NO MARATHONS, NO APPOINTMENTS
--------------------------------------------------------------------------

**No filler (G12).** `filler/bumpers/` holds exactly one tree and it is
`cartoon network`. There is no PBS, workshop or maker branding on disk, and
borrowing Adult Swim's bumps for Bob Ross is the mistake G12 was written for.
Ships silent; the shortfall is on the acquisitions list.

**No marathons.** `find_active_marathon` returns nothing while a holiday season
is live (G9), and every date-anchored idea this channel has -- a Christmas
build, a Thanksgiving table -- lands inside one. There is also nothing to point
a `MarathonSequence` at: marathons here address film series by title, and this
channel has no film.

**No appointments (F7/G6).** Every show on the shelf can strip -- the smallest
television pool is 151 episodes -- so nothing is too short to be anything but a
strip, and there is no run to turn into a Thursday night. A channel with no
appointment is a channel with no G5 gating bug, which is the one failure mode
this grid cannot have.

**Both injections off, measured rather than assumed.** Tag injection rewrites a
key as `(base) AND (tag:winter OR ...)`, so it is only useful if the episodes
carry the tags. They do not: **337 of 2,164 episode NFOs on this channel carry
any `<tag>` at all**, and the tag is `season premiere` or `season finale` in
two-thirds of those. The word `christmas` appears **three times in the whole
shelf** -- once in Joy of Painting, twice in MythBusters. An injected key would
resolve to nothing, and with six of the ten blocks holding a single show (G3)
there would be no next item to yield to.
"""

from scripts.logic.structures import Block, RandomCollection, WeightedCollection

# ==============================================================================
# 1. LIGHTS OUT -- 23:00-24:00 and 00:00-02:00
# ==============================================================================

# The frame around the working day. Bob Ross opens the channel and closes it,
# and appears nowhere in between -- 403 episodes could carry sixty hours a week
# and are given thirty-seven, because a third Ross block is exactly the mistake
# Cabes Classic Cinema made when First Reel and The Golden Age drew the same
# keys in a different order (G4).
#
# One block, reached from two slots -- 23-24 and 00-02 -- split at midnight so
# neither wraps it (G1). Pointing both at the same block is what carries the
# no-repeat state across the boundary rather than restarting it at midnight.
LIGHTS_OUT = Block(
    name="Lights Out",
    items=RandomCollection(["joy_of_painting_tv"]),
)

# ==============================================================================
# 2. THE LONG BENCH -- 02:00-06:00
# ==============================================================================

# Four hours of the four half-hour workshop shows. Not a rebroadcast and not a
# vault: this channel has 951 hours and does not need to replay the day, so the
# small hours are first-run like everything else.
#
# Weighted to spend the overnight out of the shelves that can afford it. The
# weights are **pick** probabilities, not airtime -- a `WeightedCollection`
# chooses an item, and these four have different running times, so each weight
# is the target airtime share divided by the show's median and renormalised.
# Aimed at 40/35/15/10 of the four hours; at 26.8, 21.5, 25.1 and 28.7 minutes
# that lands as the numbers below.
#
# Two shows are deliberately absent. MythBusters, because the marquee playing
# at three in the morning is not a marquee. Joy of Painting, because it holds
# the hours either side of this block already and adding it here would make the
# stretch from 23:00 to 08:00 one show with a gap in it.
THE_LONG_BENCH = Block(
    name="The Long Bench",
    items=WeightedCollection([
        ("woodwrights_shop_tv", 0.37),
        ("how_its_made_tv", 0.40),
        ("new_yankee_workshop_tv", 0.15),
        ("this_old_house_tv", 0.08),
    ]),
)

# ==============================================================================
# 3. SIGN-ON -- 06:00-08:00
# ==============================================================================

# Two hours of Bob Ross to open the day. It is the gentlest thing on the shelf
# and the only one that is not instruction you could follow with tools in your
# hands, which is why it is here and not at ten.
SIGN_ON = Block(
    name="Sign-On",
    items=RandomCollection(["joy_of_painting_tv"]),
)

# ==============================================================================
# 4. THE HAND TOOL -- 08:00-10:00
# ==============================================================================

# Roy Underhill, no electricity, 479 episodes -- the largest shelf on the
# channel and the bottom of the day's scale. One show per strip, so eight
# o'clock reads as *The Woodwright's Shop is on* rather than *woodworking is
# on* (G3). At a 26.8-minute median it puts four episodes into two hours and
# leaves nothing stranded (G2).
THE_HAND_TOOL = Block(
    name="The Hand Tool",
    items=RandomCollection(["woodwrights_shop_tv"]),
)

# ==============================================================================
# 5. THE SHOP -- 10:00-12:00
# ==============================================================================

# Norm Abram and a room full of machines: the same craft as eight o'clock with
# the power turned on, which is why it follows it. One strip and no more --
# 63.9 hours is the smallest television shelf here, and a second daypart would
# take it under three weeks (F6).
THE_SHOP = Block(
    name="The Shop",
    items=RandomCollection(["new_yankee_workshop_tv"]),
)

# ==============================================================================
# 6. THE FACTORY FLOOR -- 12:00-15:00  (Saturday 15:00-19:00)
# ==============================================================================

# The scale jumps from one bench to a production line, and the presenter
# disappears. 416 episodes at 21.5 minutes -- the shortest show on the channel
# and the only one with no host, no project and no continuity, which is what
# makes it the right three hours to walk in and out of at lunchtime.
#
# One block reached from two arms of the week rather than two blocks drawing
# one key: on Saturday it moves to 15:00-19:00 and the morning goes to
# THE_WEEKEND_PROJECT (G4).
THE_FACTORY_FLOOR = Block(
    name="The Factory Floor",
    items=RandomCollection(["how_its_made_tv"]),
)

# ==============================================================================
# 7. THE HOUSE -- 15:00-19:00
# ==============================================================================

# The top of the scale: the largest thing anyone on this channel makes. Four
# hours across the afternoon and evening slots, and one block rather than two
# so the no-repeat state runs the whole stretch.
#
# Four hours is also where the audience is -- people come home at five, and a
# home-improvement show at five is the one piece of this grid that needs no
# argument. It costs This Old House a 26.9-day cycle, the second tightest on
# the channel, and that is the right pool to spend it on.
THE_HOUSE = Block(
    name="The House",
    items=RandomCollection(["this_old_house_tv"]),
)

# ==============================================================================
# 8. THE EXPERIMENT -- 19:00-22:00
# ==============================================================================

# Prime, and the only hour-long show on the channel: a 43.6-minute median
# against 21 to 29 for everything else. **That is the reason prime is three
# hours and every other strip is two** -- an hour-long show in a two-hour
# daypart strands forty minutes, and four of them fit three hours almost
# exactly (G2).
#
# It appears in exactly one block. 210 hours against 21 a week is a ten-week
# cycle, far slacker than F6 asks for and deliberately so: the marquee is the
# one thing on the channel that should never feel like a rerun, and it is also
# the reserve if any other pool ever has to give hours back.
THE_EXPERIMENT = Block(
    name="The Experiment",
    items=RandomCollection(["mythbusters_tv"]),
)

# ==============================================================================
# 9. THE SMALL SHOP -- 22:00-23:00, Monday to Friday
# ==============================================================================

# The day ends where it started, on one bench, with the network taken away:
# two people filming themselves in a garage. It is the same programme as the
# morning strips fifty years later, which is why it sits at the far end of the
# day from them rather than next to them.
#
# **The whole `youtube/` maker shelf is 16.7 hours**, so this hour is the
# channel's only real F6 constraint. Five nights a week is 5 hours; a nightly
# hour would be seven and take both shows under three weeks. Saturday and
# Sunday hand the hour to Lights Out instead.
#
# The weights are picks, not airtime, and they look inverted on purpose. Aiming
# at 63.5% of the hour for Pedulla and 36.5% for Wilmots, against medians of
# 19.6 and 6.8 minutes, means **picking the short one more often**: 62 picks of
# Wilmots at 6.8 minutes is 424 minutes against 38 picks of Pedulla at 19.6 for
# 737. Both land at 23.3 days.
#
# This is the one block on the channel that deliberately mixes running times,
# which G2 exists to prevent. G2's reason is that mixing strands the tail of
# the slot -- and here the mixing is what fills it. Fifteen of Wilmots' 51
# videos are under five minutes and five are under two, so there is always
# something short enough to close the hour after a 40-minute Pedulla build.
# The pool that would be a G2 problem anywhere else is the reason this hour
# never has a hole in it.
THE_SMALL_SHOP = Block(
    name="The Small Shop",
    items=WeightedCollection([
        ("pedulla_studio_tv", 0.38),
        ("timothy_wilmots_tv", 0.62),
    ]),
)

# ==============================================================================
# 10. THE WEEKEND PROJECT -- Saturday 08:00-15:00
# ==============================================================================

# Seven hours, and the one place on the channel where the strips give way to a
# wheel. This is the PBS Saturday morning how-to block put back together: This
# Old House, The New Yankee Workshop and The Woodwright's Shop are what
# actually aired in that order on that morning, and reassembling it is the only
# argument for breaking G3 anywhere on this grid.
#
# It replaces the weekday 08:00-15:00 rather than adding to it, so no show gains
# a second daypart -- Woodwright's and New Yankee each trade two strip hours for
# a share of seven, and How It's Made trades its noon for Saturday 15:00-19:00.
# Weights are picks against medians of 26.8, 28.7 and 25.1, aimed at 45/35/20
# of the seven hours.
#
# Saturday is Saturday because that is when the block aired and when the
# audience has a day to build something. It is not a collision fix: nothing on
# this channel collides with anything.
THE_WEEKEND_PROJECT = Block(
    name="The Weekend Project",
    items=WeightedCollection([
        ("woodwrights_shop_tv", 0.45),
        ("this_old_house_tv", 0.33),
        ("new_yankee_workshop_tv", 0.22),
    ]),
)
