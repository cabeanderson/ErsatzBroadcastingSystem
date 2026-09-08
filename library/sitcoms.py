"""
Good Times -- the studio audience
=================================

**Identity.** Multi-camera network sitcom, 1951-1999. If it has a laugh track
and it aired on CBS, NBC, ABC or FOX, it is here. That is a *form*, not a date
range (F4): the multi-camera studio-audience sitcom really does end around
2000, when Malcolm in the Middle and The Office replaced it with single-camera.
Everything on the far side of that break -- the single-camera network sitcom,
cable, streaming, sketch and alt comedy -- belongs to Corncob TV.

**Axis (F3): the week is the networks; the day is that network's history.**

Each day of the week belongs to one network and walks its roster across the
clock. The placement is by *fit*, not by date -- CBS Monday opens with The Nanny
(1993) at eight in the morning and closes with Murphy Brown, while its 06:00
sign-on is Dick Van Dyke (1961). Era floats freely, which it can precisely
because the laugh-track line was drawn: every show left on this channel works at
any hour, so nothing has to be fenced into a daypart.

    MONDAY     CBS      the vault day      -- CBS Monday, 1993
    TUESDAY    NBC                         -- NBC Tuesday, 1997
    WEDNESDAY  ABC                         -- ABC Wednesday, 1995
    THURSDAY   NBC                         -- Must See TV
    FRIDAY     ABC                         -- TGIF
    SATURDAY   CBS                         -- The Greatest Night (1973)
    SUNDAY     FOX + the fourth networks   -- Fox Sunday

Roster by network: ABC 18 shows, NBC 15, CBS 11, FOX/UPN/WB 5. Two days each
for the big three and one for FOX, which puts every network on a 16-20 week
cycle -- comfortably past the three-week floor in F6.

**The books.** Three daytime strips a day -- morning, midday, afternoon -- carry
a season-keyed book, so the channel reshuffles its daytime four times a year the
way a real station does while prime, evening and the overnight stay the spine.
Winter leans cosy (Andy Griffith, Bob Newhart, Northern Exposure, Golden Girls),
spring leans bright (Bewitched, Jeannie, Sabrina, Mork), summer leans young
(Saved by the Bell, Sister Sister, Fresh Prince, Full House), fall is the
marquee. Sunday carries no book: five shows would give four names to the same
five titles. See reference/acquisitions.md.

--------------------------------------------------------------------------
THE HOURS RULES (C1/C2 -- every one of these is a title another channel is
airing at that hour, not a matter of taste)
--------------------------------------------------------------------------

Nick at Nite, split at midnight. The documented rule reads "nothing shared
between 21:00 and 02:00", which is stricter than Nick's own grid: `nite` is
21:00-24:00 and holds the pre-1970 seven, `after_hours` is 00:00-02:00 and holds
the 70s shift. Blocking each title only for the hours Nick actually airs it is
what C1 literally asks, and it is what frees Saturday prime below.

  21:00-24:00 (so: prime 20-23 and late 23-24)
      Dick Van Dyke · Andy Griffith · Bewitched · I Dream of Jeannie
      The Addams Family · Gilligan's Island
  00:00-02:00 (so: after_hours)
      Mary Tyler Moore · Bob Newhart · Taxi · M*A*S*H · Sanford and Son
      Good Times · Soap · Mork & Mindy · Smothers Brothers

Totally 80s. Its evening splits Mon-Fri from Sat-Sun and the two arms hold
different titles, so the rule is not "these six, every day" -- Married... with
Children is free at the weekend and Murphy Brown and Roseanne are free on a
weekday. Sunday's 17:00 strip and Monday's prime both depend on that.

  Mon-Fri 17:00-20:00       Family Matters · Married... with Children
                            The Wonder Years · Full House
  Sat-Sun 17:00-20:00       Family Matters · Full House · Murphy Brown
                            · Roseanne
  08:00-10:00, FALL/WINTER  Saved by the Bell · Perfect Strangers · Coach
  Tuesday 20:00-23:00       Roseanne · Murphy Brown · The Golden Girls
  Thursday 20:00-23:00      Cheers · Night Court
  23:00-24:00               In Living Color

**Lucy TV is out of scope, settled by the operator 2026-09-08.** It runs
I Love Lucy and nothing else, as background television, and it **claims
nothing**. Every other channel schedules as though it did not exist. This
replaces the old framing, which treated it as a claimant and therefore needed
C5 to license a "three-channel exemption" for I Love Lucy -- an exemption that
existed only because a non-claimant had been counted as one.

What is left is an ordinary hours rule, not an exception. I Love Lucy is on
this channel and on Nick at Nite, and the only constraint that binds is Nick's,
above: out of 21:00-24:00, which prime and late respect. It signs the channel
on at 06:00 on both CBS days, and 06:00 is nowhere near Nick.

**All three Lucille Ball series are here as of 2026-09-08**, where the old
policy reserved two of them for a channel that was never going to air them:

* **I Love Lucy** (180 eps, 26.3m) -- the sign-on, both CBS days. This is the
  multi-camera studio-audience channel and this is the show that invented the
  form.
* **The Lucy Show** (156 eps, 25.6m) -- CBS 1962, so it joins the CBS bench on
  Monday and Saturday like any other half-hour on the roster.
* **The Lucy-Desi Comedy Hour** (13 eps, **50.7m**) -- the only hour-long show
  on the channel. Too short to strip (G6) and the wrong shape for a half-hour
  slot (G2), so it takes Saturday's two-hour noon exactly: two episodes, one
  day a week, a 45-day cycle.

Thursday is the one to notice. Totally 80s runs Cheers and Night Court as *its*
Must See Thursday; Good Times runs the 1990s Must See Thursday on the same
night. Same night's identity, two eras, no shared title.
"""

from scripts.logic.structures import RandomCollection, OrderedCollection, Block
from scripts.library.queries import show_by_title
from . import branding

# ==============================================================================
# 1. THE ROSTER, BY NETWORK
# ==============================================================================
#
# Documentation first and content second: these are what each network-day draws
# from, and having them written down is what makes the hours rules above
# checkable by eye. Nothing schedules them, which is why they are underscored:
# collision_report's `library_collections()` treats every public uppercase list
# in the library as a schedulable collection, and a roster read that way makes
# every pair of shows on one network report as SAME COLLECTION.

_CBS_ROSTER = [
    "i_love_lucy_tv", "lucy_show_tv", "lucy_desi_tv",
    "andy_griffith_tv", "dick_van_dyke_tv", "gilligans_island_tv",
    "smothers_brothers_tv", "mary_tyler_moore_tv", "mash_tv", "bob_newhart_tv",
    "good_times_tv", "murphy_brown_tv", "northern_exposure_tv", "nanny_tv",
]

_NBC_ROSTER = [
    "jeannie_tv", "sanford_and_son_tv", "cheers_tv", "night_court_tv",
    "golden_girls_tv", "saved_by_the_bell_tv", "seinfeld_tv", "fresh_prince_tv",
    "wings_tv", "mad_about_you_tv", "frasier_tv", "newsradio_tv", "3rd_rock_tv",
    "just_shoot_me_tv", "will_and_grace_tv",
]

_ABC_ROSTER = [
    "bewitched_tv", "addams_family_tv", "soap_tv", "mork_mindy_tv", "taxi_tv",
    "perfect_strangers_tv", "full_house_tv", "roseanne_tv", "wonder_years_tv",
    "coach_tv", "family_matters_tv", "dinosaurs_tv", "home_improvement_tv",
    "mr_cooper_tv", "sister_sister_tv", "drew_carey_tv", "sabrina_tv",
    "spin_city_tv",
]

# FOX proper is three shows. Sunday is "FOX and the fourth networks" so that the
# day has five: Moesha was UPN and Sister, Sister spent its back half on The WB,
# which is the same upstart-network story the day is about.
_FOURTH_NETWORK_ROSTER = [
    "married_children_tv", "in_living_color_tv", "martin_tv", "moesha_tv",
    "sister_sister_tv",
]

# The channel fallback. Every title here is clear of Nick at Nite and Totally
# 80s at *every* hour of the day, which is the only safe property for content
# that fires on a stall and cannot know what time it is. Lucy TV used to be in
# that sentence and is not a claimant (see the docstring), so it no longer
# constrains anything here.
CHANNEL_FALLBACK = RandomCollection([
    "seinfeld_tv", "frasier_tv", "wings_tv", "mad_about_you_tv", "newsradio_tv",
    "3rd_rock_tv", "just_shoot_me_tv", "will_and_grace_tv", "nanny_tv",
    "drew_carey_tv", "home_improvement_tv", "spin_city_tv", "sabrina_tv",
    "mr_cooper_tv", "sister_sister_tv", "northern_exposure_tv",
])


# ==============================================================================
# 2. MONDAY -- CBS, the vault day
# ==============================================================================

MON_AFTER_HOURS = OrderedCollection(["nanny_tv", "murphy_brown_tv"])
MON_OVERNIGHT = RandomCollection([
    "i_love_lucy_tv", "lucy_show_tv", "gilligans_island_tv", "andy_griffith_tv",
    "dick_van_dyke_tv",
])
# The channel signs on with the show that invented it. 06:00 is nowhere near
# Nick at Nite's 21:00-24:00, so this is an hours rule and not an exception --
# see the docstring.
MON_EARLY = OrderedCollection(["i_love_lucy_tv", "dick_van_dyke_tv", "andy_griffith_tv"])

MON_MORNING = {
    "FALL":   OrderedCollection(["nanny_tv", "murphy_brown_tv"]),
    "WINTER": OrderedCollection(["northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": OrderedCollection(["gilligans_island_tv", "nanny_tv"]),
    "SUMMER": OrderedCollection(["good_times_tv", "gilligans_island_tv"]),
}
MON_MIDDAY = {
    "FALL":   OrderedCollection(["good_times_tv", "bob_newhart_tv"]),
    "WINTER": OrderedCollection(["bob_newhart_tv", "mary_tyler_moore_tv"]),
    # The Lucy Show rather than I Love Lucy, deliberately: the two Ball series
    # are never in the same arm, so the channel reads as having a Lucy on
    # somewhere rather than as running Lucy twice (G4, inside one day).
    "SPRING": OrderedCollection(["lucy_show_tv", "murphy_brown_tv"]),
    "SUMMER": OrderedCollection(["gilligans_island_tv", "good_times_tv"]),
}
MON_AFTERNOON = {
    "FALL":   RandomCollection(["andy_griffith_tv", "good_times_tv", "nanny_tv"]),
    "WINTER": RandomCollection(["andy_griffith_tv", "bob_newhart_tv", "northern_exposure_tv"]),
    "SPRING": RandomCollection(["gilligans_island_tv", "dick_van_dyke_tv", "nanny_tv"]),
    "SUMMER": RandomCollection(["gilligans_island_tv", "good_times_tv", "nanny_tv"]),
}

MON_EVENING = OrderedCollection(["mary_tyler_moore_tv", "bob_newhart_tv"])

# CBS Monday, 1993 -- the night Murphy Brown actually held down.
MON_PRIME = Block(
    name="CBS Monday",
    items=OrderedCollection([
        "murphy_brown_tv",
        "northern_exposure_tv",
        "nanny_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 3. TUESDAY -- NBC
# ==============================================================================

TUE_AFTER_HOURS = OrderedCollection(["just_shoot_me_tv", "newsradio_tv"])
TUE_OVERNIGHT = OrderedCollection(["jeannie_tv", "sanford_and_son_tv"])
TUE_EARLY = OrderedCollection(["wings_tv", "mad_about_you_tv"])

# Saved by the Bell is Totally 80s' 08:00-10:00 in fall and winter, so it takes
# the summer arm of this book and the midday strip the rest of the year.
TUE_MORNING = {
    "FALL":   OrderedCollection(["3rd_rock_tv", "just_shoot_me_tv"]),
    "WINTER": OrderedCollection(["frasier_tv", "wings_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "mad_about_you_tv"]),
    "SUMMER": OrderedCollection(["saved_by_the_bell_tv", "fresh_prince_tv"]),
}
TUE_MIDDAY = {
    "FALL":   OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
    "WINTER": OrderedCollection(["golden_girls_tv", "night_court_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "wings_tv"]),
    "SUMMER": OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
}
TUE_AFTERNOON = {
    "FALL":   RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "mad_about_you_tv"]),
    "WINTER": RandomCollection(["night_court_tv", "golden_girls_tv", "wings_tv"]),
    "SPRING": RandomCollection(["jeannie_tv", "fresh_prince_tv", "newsradio_tv"]),
    "SUMMER": RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "jeannie_tv"]),
}

TUE_EVENING = OrderedCollection(["seinfeld_tv", "frasier_tv"])

# The literal NBC Tuesday lineup of 1997, all four of them on disk:
# Mad About You, NewsRadio, Frasier, Just Shoot Me!
TUE_PRIME = Block(
    name="NBC Tuesday",
    items=OrderedCollection([
        "mad_about_you_tv",
        "newsradio_tv",
        "frasier_tv",
        "just_shoot_me_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 4. WEDNESDAY -- ABC
# ==============================================================================

WED_AFTER_HOURS = OrderedCollection(["drew_carey_tv", "spin_city_tv"])
WED_OVERNIGHT = OrderedCollection(["bewitched_tv", "addams_family_tv"])
WED_EARLY = OrderedCollection(["sabrina_tv", "sister_sister_tv"])

WED_MORNING = {
    "FALL":   OrderedCollection(["spin_city_tv", "drew_carey_tv"]),
    "WINTER": OrderedCollection(["home_improvement_tv", "drew_carey_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "sabrina_tv"]),
    "SUMMER": OrderedCollection(["perfect_strangers_tv", "sister_sister_tv"]),
}
WED_MIDDAY = {
    "FALL":   OrderedCollection(["mr_cooper_tv", "dinosaurs_tv"]),
    "WINTER": OrderedCollection(["dinosaurs_tv", "coach_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "mork_mindy_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "sabrina_tv"]),
}
# Full House and Family Matters are Totally 80s' 17:00-20:00 strip and nothing
# else; the afternoon is open and it is where TGIF's own shows belong anyway.
WED_AFTERNOON = {
    "FALL":   RandomCollection(["full_house_tv", "family_matters_tv", "sister_sister_tv"]),
    "WINTER": RandomCollection(["full_house_tv", "perfect_strangers_tv", "dinosaurs_tv"]),
    "SPRING": RandomCollection(["bewitched_tv", "sabrina_tv", "mork_mindy_tv"]),
    "SUMMER": RandomCollection(["sister_sister_tv", "full_house_tv", "wonder_years_tv"]),
}

WED_EVENING = RandomCollection(["home_improvement_tv", "coach_tv", "mr_cooper_tv"])

WED_PRIME = Block(
    name="ABC Wednesday",
    items=OrderedCollection([
        "drew_carey_tv",
        "roseanne_tv",
        "coach_tv",
    ]),
    use_epg_group=False,
)

WED_LATE = OrderedCollection(["soap_tv", "mork_mindy_tv"])


# ==============================================================================
# 5. THURSDAY -- NBC, Must See TV
# ==============================================================================

THU_AFTER_HOURS = OrderedCollection(["frasier_tv", "mad_about_you_tv"])
THU_OVERNIGHT = OrderedCollection(["jeannie_tv", "night_court_tv"])
THU_EARLY = OrderedCollection(["newsradio_tv", "wings_tv"])

THU_MORNING = {
    "FALL":   OrderedCollection(["will_and_grace_tv", "frasier_tv"]),
    "WINTER": OrderedCollection(["golden_girls_tv", "frasier_tv"]),
    "SPRING": OrderedCollection(["jeannie_tv", "3rd_rock_tv"]),
    "SUMMER": OrderedCollection(["saved_by_the_bell_tv", "will_and_grace_tv"]),
}
THU_MIDDAY = {
    "FALL":   OrderedCollection(["golden_girls_tv", "night_court_tv"]),
    "WINTER": OrderedCollection(["cheers_tv", "golden_girls_tv"]),
    "SPRING": OrderedCollection(["wings_tv", "mad_about_you_tv"]),
    "SUMMER": OrderedCollection(["fresh_prince_tv", "saved_by_the_bell_tv"]),
}
THU_AFTERNOON = {
    "FALL":   RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "will_and_grace_tv"]),
    "WINTER": RandomCollection(["golden_girls_tv", "night_court_tv", "frasier_tv"]),
    "SPRING": RandomCollection(["jeannie_tv", "wings_tv", "3rd_rock_tv"]),
    "SUMMER": RandomCollection(["saved_by_the_bell_tv", "fresh_prince_tv", "seinfeld_tv"]),
}

THU_EVENING = OrderedCollection(["seinfeld_tv", "wings_tv"])

# NBC Thursday, 1995. Friends is not on disk; the other three of the four are,
# and Will & Grace inherits the 21:00 half-hour it went on to hold.
# Cheers and Night Court are deliberately absent: they are Totally 80s' Thursday
# prime, and this is the same night one era later.
THU_PRIME = Block(
    name="Must See TV",
    items=OrderedCollection([
        "seinfeld_tv",
        "mad_about_you_tv",
        "frasier_tv",
        "will_and_grace_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 6. FRIDAY -- ABC, TGIF
# ==============================================================================

FRI_AFTER_HOURS = OrderedCollection(["spin_city_tv", "sabrina_tv"])
FRI_OVERNIGHT = OrderedCollection(["bewitched_tv", "addams_family_tv"])
FRI_EARLY = OrderedCollection(["dinosaurs_tv", "sabrina_tv"])

FRI_MORNING = {
    "FALL":   OrderedCollection(["drew_carey_tv", "spin_city_tv"]),
    "WINTER": OrderedCollection(["home_improvement_tv", "spin_city_tv"]),
    "SPRING": OrderedCollection(["bewitched_tv", "dinosaurs_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "perfect_strangers_tv"]),
}
FRI_MIDDAY = {
    "FALL":   OrderedCollection(["sister_sister_tv", "mr_cooper_tv"]),
    "WINTER": OrderedCollection(["mr_cooper_tv", "dinosaurs_tv"]),
    "SPRING": OrderedCollection(["sabrina_tv", "mork_mindy_tv"]),
    "SUMMER": OrderedCollection(["sister_sister_tv", "full_house_tv"]),
}
FRI_AFTERNOON = {
    "FALL":   RandomCollection(["full_house_tv", "family_matters_tv", "mr_cooper_tv"]),
    "WINTER": RandomCollection(["perfect_strangers_tv", "coach_tv", "dinosaurs_tv"]),
    "SPRING": RandomCollection(["sabrina_tv", "bewitched_tv", "sister_sister_tv"]),
    "SUMMER": RandomCollection(["full_house_tv", "sister_sister_tv", "wonder_years_tv"]),
}

FRI_EVENING = RandomCollection(["drew_carey_tv", "home_improvement_tv", "sabrina_tv"])

# The one block on the channel that keeps its own branding. Queried by title
# rather than by key because the block wants a shuffled order of its own, and a
# content key carries its playback order (G8).
FRI_PRIME = Block(
    name="TGIF",
    items=OrderedCollection([
        {"title": "Full House", "query": show_by_title("Full House"), "order": "Shuffle"},
        {"title": "Family Matters", "query": show_by_title("Family Matters"), "order": "Shuffle"},
        {"title": "Perfect Strangers", "query": show_by_title("Perfect Strangers"), "order": "Shuffle"},
        {"title": "Hangin' with Mr. Cooper", "query": show_by_title("Hangin' with Mr. Cooper"), "order": "Shuffle"},
        {"title": "Sister, Sister", "query": show_by_title("Sister, Sister"), "order": "Shuffle"},
        {"title": "Dinosaurs", "query": show_by_title("Dinosaurs"), "order": "Shuffle"},
    ]),
    bumpers=branding.BRANDING_TGIF.bumpers,
    use_epg_group=False,
)

FRI_LATE = OrderedCollection(["soap_tv", "taxi_tv"])


# ==============================================================================
# 7. SATURDAY -- CBS, The Greatest Night
# ==============================================================================

SAT_AFTER_HOURS = OrderedCollection(["nanny_tv", "northern_exposure_tv"])
SAT_OVERNIGHT = OrderedCollection([
    "gilligans_island_tv", "lucy_show_tv", "andy_griffith_tv",
])
SAT_EARLY = OrderedCollection(["i_love_lucy_tv", "dick_van_dyke_tv", "gilligans_island_tv"])

SAT_MORNING = {
    "FALL":   OrderedCollection(["nanny_tv", "northern_exposure_tv"]),
    "WINTER": OrderedCollection(["northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": OrderedCollection(["dick_van_dyke_tv", "gilligans_island_tv"]),
    "SUMMER": OrderedCollection(["gilligans_island_tv", "good_times_tv"]),
}
SAT_MIDDAY = {
    "FALL":   OrderedCollection(["good_times_tv", "murphy_brown_tv"]),
    "WINTER": OrderedCollection(["bob_newhart_tv", "mary_tyler_moore_tv"]),
    "SPRING": OrderedCollection(["i_love_lucy_tv", "andy_griffith_tv"]),
    "SUMMER": OrderedCollection(["good_times_tv", "nanny_tv"]),
}
SAT_AFTERNOON = {
    "FALL":   RandomCollection(["andy_griffith_tv", "lucy_show_tv", "good_times_tv"]),
    "WINTER": RandomCollection(["andy_griffith_tv", "northern_exposure_tv", "bob_newhart_tv"]),
    "SPRING": RandomCollection(["dick_van_dyke_tv", "gilligans_island_tv", "nanny_tv"]),
    "SUMMER": RandomCollection(["gilligans_island_tv", "lucy_show_tv", "nanny_tv"]),
}

SAT_EVENING = OrderedCollection(["dick_van_dyke_tv", "good_times_tv"])

# CBS Saturday, 1973 -- All in the Family, M*A*S*H, Mary Tyler Moore, Bob
# Newhart, Carol Burnett. Three of the five are on disk and they are the three
# in the middle. Reachable at 20:00-23:00 only because Nick at Nite runs the 70s
# shift at 00:00-02:00 and not at 21:00; see the hours rules in the docstring.
# The two missing names are the top of reference/acquisitions.md.
SAT_PRIME = Block(
    name="The Greatest Night",
    items=OrderedCollection([
        "mash_tv",
        "mary_tyler_moore_tv",
        "bob_newhart_tv",
    ]),
    use_epg_group=False,
)


# ==============================================================================
# 8. SUNDAY -- FOX and the fourth networks
# ==============================================================================
#
# Five shows and no seasonal book: four arms would be four names for the same
# five titles. It is a deliberately small, loud day -- which is what FOX Sunday
# was -- and the shelf it wants is in reference/acquisitions.md.

SUN_AFTER_HOURS = OrderedCollection(["martin_tv", "in_living_color_tv"])
SUN_OVERNIGHT = OrderedCollection(["married_children_tv", "martin_tv"])
SUN_EARLY = OrderedCollection(["sister_sister_tv", "moesha_tv"])
SUN_MORNING = OrderedCollection(["moesha_tv", "sister_sister_tv"])
SUN_MIDDAY = OrderedCollection(["moesha_tv", "sister_sister_tv"])
SUN_AFTERNOON = RandomCollection([
    "sister_sister_tv", "moesha_tv", "married_children_tv",
])
# Married... with Children is Totally 80s' *weekday* 17:00-20:00 strip; its
# weekend evening is a different four, so Sunday at seven is clear.
SUN_EVENING = OrderedCollection(["married_children_tv", "martin_tv"])

SUN_PRIME = Block(
    name="Fox Sunday",
    items=OrderedCollection([
        "married_children_tv",
        "in_living_color_tv",
        "martin_tv",
    ]),
    use_epg_group=False,
)

# In Living Color is Totally 80s' 23:00-24:00 Sketch Hour, so the late shift
# here takes Martin and the sketch show waits until after midnight.
SUN_LATE = "martin_tv"


# ==============================================================================
# 9. THE NOON HOUR
# ==============================================================================
#
# One show per day, no collection (G3): the hour reads as "M*A*S*H is on at
# noon" rather than "sitcoms are on". Each day's anchor comes from that day's
# network, so the strip turns over with the wheel.

# Saturday is the one hour-long entry, and the slot is why. `noon` is two hours;
# every other day fills it with four half-hours, and Saturday fills it with two
# 50-minute Comedy Hours -- the same 100 minutes, so the shape of the slot does
# not change. It is the only place on the channel an hour-long fits without
# stranding a half-hour strip's tail (G2), and at two episodes a week those 13
# run a 45-day cycle, which is what G6 asks of a pool too short to strip.
NOON_HOUR = {
    "MONDAY":    "mash_tv",
    "TUESDAY":   "wings_tv",
    "WEDNESDAY": "taxi_tv",
    "THURSDAY":  "cheers_tv",
    "FRIDAY":    "perfect_strangers_tv",
    "SATURDAY":  "lucy_desi_tv",
    "SUNDAY":    "martin_tv",
}


# ==============================================================================
# 10. THE LATE SHIFT (23:00-24:00)
# ==============================================================================
#
# One hour, and the only slot on the channel that has to dodge both Nick at
# Nite's 21:00-24:00 block and Totally 80s' Sketch Hour. The Smothers Brothers
# is a 60-minute variety hour, which is exactly one late shift, and Nick runs it
# at 00:00-02:00 -- so it can hold two nights a week and still cycle 67 episodes
# over eight months.

LATE_SHIFT = {
    "MONDAY":    "smothers_brothers_tv",
    "TUESDAY":   "night_court_tv",
    "WEDNESDAY": WED_LATE,
    "THURSDAY":  "3rd_rock_tv",
    "FRIDAY":    FRI_LATE,
    "SATURDAY":  "smothers_brothers_tv",
    "SUNDAY":    SUN_LATE,
}


# ==============================================================================
# 11. HOLIDAY EVENTS
# ==============================================================================
#
# The channel's own, rather than `common.HALLOWEEN_TV_EVENT` and
# `common.CHRISTMAS_TV_EVENT`: both of those lead with `*_animated_tv`, and a
# laugh-track channel that spends Halloween on cartoons is running another
# channel's holiday. These are episode-level keys -- the Halloween and Christmas
# episodes of the sitcoms already on the air here.

HALLOWEEN_EVENT = RandomCollection([
    "halloween_sitcoms_tv",
])

THANKSGIVING_EVENT = RandomCollection([
    "thanksgiving_sitcoms_tv",
    "thanksgiving_90s_tv",
])

CHRISTMAS_EVENT = RandomCollection([
    "christmas_80s_sitcoms_tv",
    "christmas_90s_sitcoms_tv",
])
